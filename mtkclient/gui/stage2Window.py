import os
from unittest import mock
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, QScrollArea, QComboBox, QCheckBox
from mtkclient.gui.toolkit import asyncThread, FDialog

class Stage2Window(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, sendToLog):
        super(Stage2Window, self).__init__(parent)
        self.parent = parent
        self.sendToLog = sendToLog
        self.ui = ui
        self.fdialog = FDialog(parent)
        self.setup_ui()

    def setup_ui(self):
        self.tab = QWidget()
        main_layout = QVBoxLayout(self.tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Stage2 Dumps Group
        dumps_group = QGroupBox("Stage2 Memory/Storage Dumps")
        dumps_layout = QVBoxLayout(dumps_group)
        
        h_off = QHBoxLayout()
        h_off.addWidget(QLabel("Start Offset:"))
        self.edit_start = QLineEdit("0x0")
        h_off.addWidget(self.edit_start)
        h_off.addWidget(QLabel("Length:"))
        self.edit_len = QLineEdit("0x0")
        h_off.addWidget(self.edit_len)
        dumps_layout.addLayout(h_off)

        h_btns = QHBoxLayout()
        self.btn_rpmb = QPushButton("Dump RPMB")
        self.btn_pl = QPushButton("Dump Preloader")
        self.btn_data = QPushButton("Dump MMC Data")
        self.btn_boot2 = QPushButton("Dump Boot2")
        h_btns.addWidget(self.btn_rpmb)
        h_btns.addWidget(self.btn_pl)
        h_btns.addWidget(self.btn_data)
        h_btns.addWidget(self.btn_boot2)
        dumps_layout.addLayout(h_btns)
        layout.addWidget(dumps_group)

        # Stage2 Memory Access Group
        mem_group = QGroupBox("Stage2 Memory Read/Write")
        mem_layout = QVBoxLayout(mem_group)
        
        h_mem1 = QHBoxLayout()
        h_mem1.addWidget(QLabel("Address:"))
        self.edit_mem_addr = QLineEdit("0x0")
        h_mem1.addWidget(self.edit_mem_addr)
        h_mem1.addWidget(QLabel("Length (Read):"))
        self.edit_mem_len = QLineEdit("0x100")
        h_mem1.addWidget(self.edit_mem_len)
        mem_layout.addLayout(h_mem1)

        h_mem2 = QHBoxLayout()
        h_mem2.addWidget(QLabel("Data (Write - Hex/File):"))
        self.edit_mem_data = QLineEdit()
        self.btn_browse_data = QPushButton("Browse File")
        h_mem2.addWidget(self.edit_mem_data)
        h_mem2.addWidget(self.btn_browse_data)
        mem_layout.addLayout(h_mem2)

        h_mem_btns = QHBoxLayout()
        self.btn_mem_read = QPushButton("Memory Read")
        self.btn_mem_write = QPushButton("Memory Write")
        h_mem_btns.addWidget(self.btn_mem_read)
        h_mem_btns.addWidget(self.btn_mem_write)
        mem_layout.addLayout(h_mem_btns)
        layout.addWidget(mem_group)

        # Stage2 Tools Group
        tools_group = QGroupBox("Stage2 Tools & Crypto")
        tools_layout = QVBoxLayout(tools_group)
        
        h_sec = QHBoxLayout()
        h_sec.addWidget(QLabel("SecCfg Flag:"))
        self.combo_seccfg = QComboBox()
        self.combo_seccfg.addItems(["unlock", "lock"])
        self.check_sw = QCheckBox("Use SW hashing")
        self.btn_gen_seccfg = QPushButton("Generate SecCfg")
        h_sec.addWidget(self.combo_seccfg)
        h_sec.addWidget(self.check_sw)
        h_sec.addWidget(self.btn_gen_seccfg)
        tools_layout.addLayout(h_sec)

        h_keys = QHBoxLayout()
        h_keys.addWidget(QLabel("Keys Mode:"))
        self.combo_keys_mode = QComboBox()
        self.combo_keys_mode.addItems(["dxcc", "sej", "gcpu", "sej_aes_decrypt", "sej_aes_encrypt", "sej_sst_decrypt_4g", "sej_sst_decrypt_5g", "sej_sst_encrypt_4g", "sej_sst_encrypt_5g"])
        h_keys.addWidget(self.combo_keys_mode)
        h_keys.addWidget(QLabel("OTP:"))
        self.edit_otp = QLineEdit()
        h_keys.addWidget(self.edit_otp)
        self.btn_get_keys = QPushButton("Extract Keys")
        h_keys.addWidget(self.btn_get_keys)
        tools_layout.addLayout(h_keys)

        self.btn_reboot = QPushButton("Reboot Device")
        tools_layout.addWidget(self.btn_reboot)
        layout.addWidget(tools_group)

        layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Connect buttons
        self.btn_rpmb.clicked.connect(lambda: self.run_st2_cmd("rpmb"))
        self.btn_pl.clicked.connect(lambda: self.run_st2_cmd("preloader"))
        self.btn_data.clicked.connect(lambda: self.run_st2_cmd("data"))
        self.btn_boot2.clicked.connect(lambda: self.run_st2_cmd("boot2"))
        self.btn_browse_data.clicked.connect(lambda: self.browse_file(self.edit_mem_data))
        self.btn_mem_read.clicked.connect(lambda: self.run_st2_cmd("memread"))
        self.btn_mem_write.clicked.connect(lambda: self.run_st2_cmd("memwrite"))
        self.btn_gen_seccfg.clicked.connect(lambda: self.run_st2_cmd("seccfg"))
        self.btn_get_keys.clicked.connect(lambda: self.run_st2_cmd("keys"))
        self.btn_reboot.clicked.connect(lambda: self.run_st2_cmd("reboot"))

    def browse_file(self, lineedit):
        fname = self.fdialog.open()
        if fname: lineedit.setText(fname)

    def run_st2_cmd(self, cmd):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_st2_async, parameters=[cmd])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_st2_async(self, toolkit, parameters):
        cmd = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = cmd
        v.start = self.edit_start.text()
        v.length = self.edit_len.text()
        v.reverse = False # We'll use default reverse=True logic from CLI main()
        v.filename = None
        v.data = self.edit_mem_data.text()
        v.flag = self.combo_seccfg.currentText()
        v.sw = self.check_sw.isChecked()
        v.otp = self.edit_otp.text() if self.edit_otp.text() else None
        v.mode = self.combo_keys_mode.currentText()

        # Handle file paths for dumps
        if cmd in ["rpmb", "preloader", "data", "boot2"]:
            v.filename = self.fdialog.save(f"stage2_{cmd}.bin")
            if not v.filename:
                self.enableButtonsSignal.emit()
                return

        if cmd == "memread":
            v.start = self.edit_mem_addr.text()
            v.length = self.edit_mem_len.text()
            v.filename = self.fdialog.save("st2_mem_read.bin")
            if not v.filename:
                self.enableButtonsSignal.emit()
                return

        if cmd == "memwrite":
            v.start = self.edit_mem_addr.text()

        # Use the logic from stage2.py main()
        from stage2 import Stage2, getint
        st2 = Stage2(v, loglevel=self.parent.loglevel)
        if st2.connect():
            if not st2.preinit():
                toolkit.sendToLogSignal.emit("Error: Stage2 preinit failed.")
            else:
                if cmd == "rpmb":
                    st2.rpmb(getint(v.start), getint(v.length), v.filename, True)
                elif cmd == "preloader":
                    st2.preloader(getint(v.start), getint(v.length), filename=v.filename)
                elif cmd == "data":
                    st2.userdata(getint(v.start), getint(v.length), filename=v.filename)
                elif cmd == "boot2":
                    st2.boot2(getint(v.start), getint(v.length), filename=v.filename)
                elif cmd == "memread":
                    st2.memread(getint(v.start), getint(v.length), v.filename)
                elif cmd == "memwrite":
                    start = getint(v.start)
                    if os.path.exists(v.data):
                        filename, data = v.data, None
                    else:
                        data = getint(v.data) if "0x" in v.data else v.data
                        filename = None
                    if st2.memwrite(start, data, filename):
                        toolkit.sendToLogSignal.emit(f"Successfully wrote data to {hex(start)}.")
                    else:
                        toolkit.sendToLogSignal.emit(f"Failed to write data to {hex(start)}.")
                elif cmd == "keys":
                    keys, keyinfo = st2.keys(data=v.data if v.data else b"", mode=v.mode, otp=v.otp)
                    toolkit.sendToLogSignal.emit(keyinfo)
                elif cmd == "reboot":
                    st2.reboot()
                elif cmd == "seccfg":
                    import hashlib
                    from struct import pack
                    lock_state = 3 if v.flag == "unlock" else 1
                    critical_lock_state = 1 if v.flag == "unlock" else 0
                    seccfg_ver, seccfg_size, sboot_runtime = 4, 0x3C, 0
                    seccfg_data = pack("<IIIIIII", 0x4D4D4D4D, seccfg_ver, seccfg_size, lock_state, critical_lock_state, sboot_runtime, 0x45454545)
                    dec_hash = hashlib.sha256(seccfg_data).digest()
                    enc_hash = st2.hwcrypto.sej.sej_sec_cfg_sw(dec_hash, True) if v.sw else st2.hwcrypto.sej.sej_sec_cfg_hw(dec_hash, True)
                    data = seccfg_data + enc_hash
                    data += b"\x00" * (0x200 - len(data))
                    with open("seccfg.bin", "wb") as wf:
                        wf.write(data)
                    toolkit.sendToLogSignal.emit("Successfully wrote seccfg to seccfg.bin. You need to write seccfg.bin to partition seccfg.")
            st2.close()
        else:
            toolkit.sendToLogSignal.emit("Error: Could not connect to Stage2. Make sure it is running on the device.")
        
        self.enableButtonsSignal.emit()

    def setEnabled(self, enabled):
        self.tab.setEnabled(enabled)

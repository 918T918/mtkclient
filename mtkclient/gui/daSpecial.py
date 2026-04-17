import os
from unittest import mock
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, QScrollArea, QComboBox
from mtkclient.gui.toolkit import asyncThread, FDialog

class DaSpecialWindow(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, da_handler, sendToLog):
        super(DaSpecialWindow, self).__init__(parent)
        self.mtkClass = da_handler.mtk
        self.parent = parent
        self.sendToLog = sendToLog
        self.da_handler = da_handler
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

        # GPT Group
        gpt_group = QGroupBox("GPT Tools")
        gpt_group.setToolTip("Manage GUID Partition Tables.")
        gpt_layout = QHBoxLayout(gpt_group)
        self.btn_print_gpt = QPushButton("Print GPT")
        self.btn_print_gpt.setToolTip("Displays the partition table in the log.")
        self.btn_save_gpt = QPushButton("Save GPT")
        self.btn_save_gpt.setToolTip("Saves the GPT headers to a directory.")
        gpt_layout.addWidget(self.btn_print_gpt)
        gpt_layout.addWidget(self.btn_save_gpt)
        layout.addWidget(gpt_group)

        # Keys & Security Group
        keys_group = QGroupBox("Keys & Security")
        keys_group.setToolTip("Hardware key extraction and security configuration.")
        keys_layout = QVBoxLayout(keys_group)
        h_keys = QHBoxLayout()
        self.btn_efuse = QPushButton("Read EFuse")
        self.btn_efuse.setToolTip("Reads the hardware eFuse data.")
        self.btn_gen_keys = QPushButton("Generate Keys")
        self.btn_gen_keys.setToolTip("Derives hardware-specific keys.")
        self.btn_key_server = QPushButton("Key Server")
        self.btn_key_server.setToolTip("Starts a local key server for external tools.")
        h_keys.addWidget(self.btn_efuse)
        h_keys.addWidget(self.btn_gen_keys)
        h_keys.addWidget(self.btn_key_server)
        keys_layout.addLayout(h_keys)

        h_sec = QHBoxLayout()
        self.btn_seccfg_unlock = QPushButton("Unlock (seccfg)")
        self.btn_seccfg_unlock.setToolTip("Modifies seccfg to unlock the bootloader.")
        self.btn_seccfg_lock = QPushButton("Lock (seccfg)")
        self.btn_seccfg_lock.setToolTip("Modifies seccfg to lock the bootloader.")
        h_sec.addWidget(self.btn_seccfg_unlock)
        h_sec.addWidget(self.btn_seccfg_lock)
        keys_layout.addLayout(h_sec)
        layout.addWidget(keys_group)

        # NVItem / IMEI Group
        nv_group = QGroupBox("NVItem / IMEI / Modem")
        nv_group.setToolTip("Read/Write IMEI and patch modem firmware.")
        nv_layout = QVBoxLayout(nv_group)
        h_imei = QHBoxLayout()
        h_imei.addWidget(QLabel("IMEIs (comma sep):"))
        self.edit_imei = QLineEdit()
        self.edit_imei.setToolTip("Enter 15-digit IMEIs separated by commas.")
        h_imei.addWidget(self.edit_imei)
        nv_layout.addLayout(h_imei)
        h_btns = QHBoxLayout()
        self.btn_read_imei = QPushButton("Read IMEI")
        self.btn_write_imei = QPushButton("Write IMEI")
        self.btn_patch_modem = QPushButton("Patch Modem")
        self.btn_patch_modem.setToolTip("Applies patches to modem partitions for security/unlocks.")
        h_btns.addWidget(self.btn_read_imei)
        h_btns.addWidget(self.btn_write_imei)
        h_btns.addWidget(self.btn_patch_modem)
        nv_layout.addLayout(h_btns)
        layout.addWidget(nv_group)

        # VBMeta Group
        vb_group = QGroupBox("VBMeta")
        vb_group.setToolTip("Modify VBMeta partition flags.")
        vb_layout = QHBoxLayout(vb_group)
        vb_layout.addWidget(QLabel("Mode:"))
        self.combo_vbmeta = QComboBox()
        self.combo_vbmeta.addItems(["0: Locked", "1: Disable Verity", "2: Disable Verification", "3: Disable Both"])
        self.btn_patch_vbmeta = QPushButton("Patch VBMeta")
        self.btn_patch_vbmeta.setToolTip("Applies Android Verified Boot (AVB) flags to VBMeta.")
        vb_layout.addWidget(self.combo_vbmeta)
        vb_layout.addWidget(self.btn_patch_vbmeta)
        layout.addWidget(vb_group)

        # Memory Group
        mem_group = QGroupBox("Memory Access")
        mem_group.setToolTip("Expert level memory dumping and poking.")
        mem_layout = QVBoxLayout(mem_group)
        h_mem1 = QHBoxLayout()
        self.btn_memdump = QPushButton("Dump All Memory")
        self.btn_memdram = QPushButton("Dump DRAM")
        h_mem1.addWidget(self.btn_memdump)
        h_mem1.addWidget(self.btn_memdram)
        mem_layout.addLayout(h_mem1)

        h_poke = QHBoxLayout()
        h_poke.addWidget(QLabel("Poke Addr:"))
        self.combo_poke_addr = QComboBox()
        self.combo_poke_addr.setEditable(True)
        self.combo_poke_addr.addItems(["0x100000", "0x200000", "0x40000000"])
        h_poke.addWidget(self.combo_poke_addr)
        h_poke.addWidget(QLabel("Data (hex):"))
        self.edit_poke_data = QLineEdit()
        self.btn_poke = QPushButton("Poke (Write)")
        self.btn_poke.setToolTip("Writes raw data to a specific memory address.")
        h_poke.addWidget(self.edit_poke_data)
        h_poke.addWidget(self.btn_poke)
        mem_layout.addLayout(h_poke)
        layout.addWidget(mem_group)

        # RPMB Group
        rpmb_group = QGroupBox("RPMB Tools")
        rpmb_group.setToolTip("Replay Protected Memory Block management.")
        rpmb_layout = QHBoxLayout(rpmb_group)
        self.btn_read_rpmb = QPushButton("Read RPMB")
        self.btn_write_rpmb = QPushButton("Write RPMB")
        self.btn_erase_rpmb = QPushButton("Erase RPMB")
        rpmb_layout.addWidget(self.btn_read_rpmb)
        rpmb_layout.addWidget(self.btn_write_rpmb)
        rpmb_layout.addWidget(self.btn_erase_rpmb)
        layout.addWidget(rpmb_group)

        # Meta & Reset Group
        meta_group = QGroupBox("Meta Mode & Reset")
        meta_group.setToolTip("Boot control and reset commands.")
        meta_layout = QVBoxLayout(meta_group)
        h_meta = QHBoxLayout()
        h_meta.addWidget(QLabel("Meta Mode:"))
        self.combo_meta = QComboBox()
        self.combo_meta.addItems(["FASTBOOT", "FACTFACT", "METAMETA", "FACTORYM", "ADVEMETA", "AT+NBOOT"])
        self.btn_meta = QPushButton("Enter Meta")
        self.btn_meta2 = QPushButton("Enter Meta (WDT)")
        h_meta.addWidget(self.combo_meta)
        h_meta.addWidget(self.btn_meta)
        h_meta.addWidget(self.btn_meta2)
        meta_layout.addLayout(h_meta)
        h_other = QHBoxLayout()
        self.btn_footer = QPushButton("Read Crypto Footer")
        self.btn_reset = QPushButton("Reset Device")
        h_other.addWidget(self.btn_footer)
        h_other.addWidget(self.btn_reset)
        meta_layout.addLayout(h_other)
        layout.addWidget(meta_group)

        layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Connect buttons
        self.btn_print_gpt.clicked.connect(lambda: self.run_da_cmd("printgpt"))
        self.btn_save_gpt.clicked.connect(self.save_gpt)
        self.btn_efuse.clicked.connect(lambda: self.run_da_subcmd("efuse"))
        self.btn_gen_keys.clicked.connect(lambda: self.run_da_subcmd("generatekeys"))
        self.btn_key_server.clicked.connect(lambda: self.run_da_subcmd("keyserver"))
        self.btn_seccfg_unlock.clicked.connect(lambda: self.run_seccfg("unlock"))
        self.btn_seccfg_lock.clicked.connect(lambda: self.run_seccfg("lock"))
        self.btn_read_imei.clicked.connect(lambda: self.run_da_subcmd("imei", write=False))
        self.btn_write_imei.clicked.connect(lambda: self.run_da_subcmd("imei", write=True))
        self.btn_patch_modem.clicked.connect(lambda: self.run_da_subcmd("patchmodem"))
        self.btn_patch_vbmeta.clicked.connect(self.patch_vbmeta)
        self.btn_memdump.clicked.connect(lambda: self.run_memdump("memdump"))
        self.btn_memdram.clicked.connect(lambda: self.run_memdump("memdram"))
        self.btn_poke.clicked.connect(self.run_poke)
        self.btn_read_rpmb.clicked.connect(lambda: self.run_rpmb("r"))
        self.btn_write_rpmb.clicked.connect(lambda: self.run_rpmb("w"))
        self.btn_erase_rpmb.clicked.connect(lambda: self.run_rpmb("e"))
        self.btn_meta.clicked.connect(self.run_meta)
        self.btn_meta2.clicked.connect(lambda: self.run_main_cmd("meta2"))
        self.btn_footer.clicked.connect(self.read_footer)
        self.btn_reset.clicked.connect(lambda: self.run_main_cmd("reset"))

    def save_gpt(self):
        directory = self.fdialog.opendir()
        if directory: self.run_da_cmd("gpt", directory=directory)

    def read_footer(self):
        filename = self.fdialog.save("footer.bin")
        if filename: self.run_da_cmd("footer", filename=filename)

    def run_da_cmd(self, cmd, **kwargs):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_da_cmd_async, parameters=[cmd, kwargs])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_da_cmd_async(self, toolkit, parameters):
        cmd, kwargs = parameters
        try:
            v = self.parent.settings.get_variables()
            for k, v_attr in kwargs.items(): setattr(v, k, v_attr)
            self.da_handler.handle_da_cmds(self.mtkClass, cmd, v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"DA COMMAND ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_main_cmd(self, cmd):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_main_cmd_async, parameters=[cmd])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_main_cmd_async(self, toolkit, parameters):
        cmd = parameters[0]
        try:
            v = self.parent.settings.get_variables()
            v.cmd = cmd
            if cmd == "meta": v.metamode = self.combo_meta.currentText()
            from mtkclient.Library.mtk_main import Main
            Main(v).run(None)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"MAIN COMMAND ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_meta(self):
        self.run_main_cmd("meta")

    def run_da_subcmd(self, subcmd, **kwargs):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_da_subcmd_async, parameters=[subcmd, kwargs])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_da_subcmd_async(self, toolkit, parameters):
        subcmd, kwargs = parameters
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = subcmd
            v.write = kwargs.get("write", False)
            v.imeis = self.edit_imei.text()
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"DA SUBCMD ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_seccfg(self, flag):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_seccfg_async, parameters=[flag])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_seccfg_async(self, toolkit, parameters):
        flag = parameters[0]
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = "seccfg"
            v.flag = flag
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"SECCFG ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def patch_vbmeta(self):
        mode = self.combo_vbmeta.currentIndex()
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_vbmeta_async, parameters=[mode])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_vbmeta_async(self, toolkit, parameters):
        mode = parameters[0]
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = "vbmeta"
            v.vbmode = str(mode)
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"VBMETA ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_memdump(self, subcmd):
        directory = self.fdialog.opendir()
        if directory:
            self.disableButtonsSignal.emit()
            thread = asyncThread(parent=self.parent, n=0, function=self.run_memdump_async, parameters=[subcmd, directory])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.start()

    def run_memdump_async(self, toolkit, parameters):
        subcmd, directory = parameters
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = subcmd
            v.directory = directory
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"MEMDUMP ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_poke(self):
        addr = self.combo_poke_addr.currentText()
        data = self.edit_poke_data.text()
        if addr and data:
            self.disableButtonsSignal.emit()
            thread = asyncThread(parent=self.parent, n=0, function=self.run_poke_async, parameters=[addr, data])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.start()

    def run_poke_async(self, toolkit, parameters):
        addr, data = parameters
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = "poke"
            v.address = addr
            v.data = data
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"POKE ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def run_rpmb(self, rpmb_subcmd):
        filename = None
        if rpmb_subcmd in ["r", "w"]:
            filename = self.fdialog.save("rpmb.bin") if rpmb_subcmd == "r" else self.fdialog.open("rpmb.bin")
            if not filename: return
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.run_rpmb_async, parameters=[rpmb_subcmd, filename])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def run_rpmb_async(self, toolkit, parameters):
        rpmb_subcmd, filename = parameters
        try:
            v = self.parent.settings.get_variables()
            v.subcmd = "rpmb"
            v.rpmb_subcmd = rpmb_subcmd
            v.filename = filename
            self.da_handler.handle_da_cmds(self.mtkClass, "da", v)
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"RPMB ERROR: {str(e)}")
        finally:
            self.enableButtonsSignal.emit()

    def setEnabled(self, enabled):
        self.tab.setEnabled(enabled)

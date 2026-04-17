import os
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, QScrollArea, QCheckBox, QComboBox
from mtkclient.gui.toolkit import FDialog

class SettingsWindow(QObject):
    def __init__(self, ui, parent, da_handler, sendToLog):
        super(SettingsWindow, self).__init__(parent)
        self.mtkClass = da_handler.mtk
        self.parent = parent
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

        # Connection & Interface
        conn_group = QGroupBox("Connection & Interface")
        conn_layout = QVBoxLayout(conn_group)
        
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("VID:"))
        self.edit_vid = QLineEdit()
        h1.addWidget(self.edit_vid)
        h1.addWidget(QLabel("PID:"))
        self.edit_pid = QLineEdit()
        h1.addWidget(self.edit_pid)
        conn_layout.addLayout(h1)

        h2 = QHBoxLayout()
        self.check_stock = QCheckBox("Use Stock DA")
        self.check_noreconnect = QCheckBox("No Reconnect")
        self.check_iot = QCheckBox("IoT Mode")
        self.check_socid = QCheckBox("Read Soc ID")
        conn_layout.addWidget(self.check_stock)
        conn_layout.addWidget(self.check_noreconnect)
        conn_layout.addWidget(self.check_iot)
        conn_layout.addWidget(self.check_socid)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Log Channel:"))
        self.combo_logchannel = QComboBox()
        self.combo_logchannel.addItems(["UART", "USB", "BOTH"])
        h3.addWidget(self.combo_logchannel)
        h3.addWidget(QLabel("UART Log Level:"))
        self.edit_uartloglevel = QLineEdit("2")
        h3.addWidget(self.edit_uartloglevel)
        conn_layout.addLayout(h3)
        layout.addWidget(conn_group)

        # Authentication
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout(auth_group)
        
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("Auth File:"))
        self.edit_auth = QLineEdit()
        self.btn_browse_auth = QPushButton("Browse")
        h4.addWidget(self.edit_auth)
        h4.addWidget(self.btn_browse_auth)
        auth_layout.addLayout(h4)

        h5 = QHBoxLayout()
        h5.addWidget(QLabel("Cert File:"))
        self.edit_cert = QLineEdit()
        self.btn_browse_cert = QPushButton("Browse")
        h5.addWidget(self.edit_cert)
        h5.addWidget(self.btn_browse_cert)
        auth_layout.addLayout(h5)
        layout.addWidget(auth_group)

        # Exploit Settings
        expl_group = QGroupBox("Exploit Settings")
        expl_layout = QVBoxLayout(expl_group)
        
        h6 = QHBoxLayout()
        h6.addWidget(QLabel("Payload Type (ptype):"))
        self.edit_ptype = QLineEdit()
        h6.addWidget(self.edit_ptype)
        h6.addWidget(QLabel("Var1:"))
        self.edit_var1 = QLineEdit()
        h6.addWidget(self.edit_var1)
        expl_layout.addLayout(h6)

        h7 = QHBoxLayout()
        h7.addWidget(QLabel("UART Addr:"))
        self.edit_uart_addr = QLineEdit()
        h7.addWidget(self.edit_uart_addr)
        h7.addWidget(QLabel("DA Addr:"))
        self.edit_da_addr = QLineEdit()
        h7.addWidget(self.edit_da_addr)
        expl_layout.addLayout(h7)

        h8 = QHBoxLayout()
        h8.addWidget(QLabel("BROM Addr:"))
        self.edit_brom_addr = QLineEdit()
        h8.addWidget(self.edit_brom_addr)
        h8.addWidget(QLabel("WDT Addr:"))
        self.edit_wdt = QLineEdit()
        h8.addWidget(self.edit_wdt)
        expl_layout.addLayout(h8)

        h9 = QHBoxLayout()
        self.check_skipwdt = QCheckBox("Skip WDT Init")
        self.check_crash = QCheckBox("Enforce Crash")
        h9.addWidget(self.check_skipwdt)
        h9.addWidget(self.check_crash)
        expl_layout.addLayout(h9)

        h10 = QHBoxLayout()
        h10.addWidget(QLabel("App ID (hex):"))
        self.edit_appid = QLineEdit()
        h10.addWidget(self.edit_appid)
        expl_layout.addLayout(h10)
        layout.addWidget(expl_group)

        # GPT Settings
        gpt_group = QGroupBox("GPT & Partition Settings")
        gpt_layout = QVBoxLayout(gpt_group)
        
        h11 = QHBoxLayout()
        h11.addWidget(QLabel("Sector Size:"))
        self.edit_sectorsize = QLineEdit("0x200")
        h11.addWidget(self.edit_sectorsize)
        h11.addWidget(QLabel("Part Type:"))
        self.edit_parttype = QLineEdit("user")
        h11.addWidget(self.edit_parttype)
        gpt_layout.addLayout(h11)

        h12 = QHBoxLayout()
        h12.addWidget(QLabel("GPT Num Entries:"))
        self.edit_gpt_num = QLineEdit("0")
        h12.addWidget(self.edit_gpt_num)
        h12.addWidget(QLabel("GPT Entry Size:"))
        self.edit_gpt_size = QLineEdit("0")
        h12.addWidget(self.edit_gpt_size)
        gpt_layout.addLayout(h12)

        h13 = QHBoxLayout()
        h13.addWidget(QLabel("GPT Start LBA:"))
        self.edit_gpt_start = QLineEdit("0")
        h13.addWidget(self.edit_gpt_start)
        h13.addWidget(QLabel("Skip Parts:"))
        self.edit_skip = QLineEdit()
        h13.addWidget(self.edit_skip)
        gpt_layout.addLayout(h13)
        layout.addWidget(gpt_group)

        layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Connect browse buttons
        self.btn_browse_auth.clicked.connect(lambda: self.browse_file(self.edit_auth))
        self.btn_browse_cert.clicked.connect(lambda: self.browse_file(self.edit_cert))

    def browse_file(self, lineedit):
        fname = self.fdialog.open()
        if fname:
            lineedit.setText(fname)

    def get_variables(self):
        v = mock.Mock()
        v.vid = self.edit_vid.text() if self.edit_vid.text() else None
        v.pid = self.edit_pid.text() if self.edit_pid.text() else None
        v.stock = self.check_stock.isChecked()
        v.noreconnect = self.check_noreconnect.isChecked()
        v.iot = self.check_iot.isChecked()
        v.socid = self.check_socid.isChecked()
        v.logchannel = self.combo_logchannel.currentText()
        v.uartloglevel = self.edit_uartloglevel.text()
        v.auth = self.edit_auth.text() if self.edit_auth.text() else None
        v.cert = self.edit_cert.text() if self.edit_cert.text() else None
        v.ptype = self.edit_ptype.text() if self.edit_ptype.text() else None
        v.var1 = self.edit_var1.text() if self.edit_var1.text() else None
        v.uart_addr = self.edit_uart_addr.text() if self.edit_uart_addr.text() else None
        v.da_addr = self.edit_da_addr.text() if self.edit_da_addr.text() else None
        v.brom_addr = self.edit_brom_addr.text() if self.edit_brom_addr.text() else None
        v.wdt = self.edit_wdt.text() if self.edit_wdt.text() else None
        v.skipwdt = self.check_skipwdt.isChecked()
        v.crash = self.check_crash.isChecked()
        v.appid = self.edit_appid.text() if self.edit_appid.text() else None
        v.sectorsize = self.edit_sectorsize.text()
        v.parttype = self.edit_parttype.text()
        v.gpt_num_part_entries = self.edit_gpt_num.text()
        v.gpt_part_entry_size = self.edit_gpt_size.text()
        v.gpt_part_entry_start_lba = self.edit_gpt_start.text()
        v.skip = self.edit_skip.text()
        return v

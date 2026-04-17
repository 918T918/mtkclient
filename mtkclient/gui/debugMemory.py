import os
from unittest import mock
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, QScrollArea, QCheckBox
from mtkclient.gui.toolkit import asyncThread, FDialog

class DebugMemoryWindow(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, da_handler, sendToLog):
        super(DebugMemoryWindow, self).__init__(parent)
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

        # Logs Group
        logs_group = QGroupBox("Target Logs")
        logs_layout = QHBoxLayout(logs_group)
        self.btn_get_logs = QPushButton("Get Target Logs")
        logs_layout.addWidget(self.btn_get_logs)
        layout.addWidget(logs_group)

        # Memory Peek Group
        peek_group = QGroupBox("Memory Peek (Read)")
        peek_layout = QVBoxLayout(peek_group)
        
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Address (hex):"))
        self.edit_addr = QLineEdit("0x0")
        h1.addWidget(self.edit_addr)
        h1.addWidget(QLabel("Length (hex):"))
        self.edit_len = QLineEdit("0x100")
        h1.addWidget(self.edit_len)
        peek_layout.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Preloader:"))
        self.edit_pl = QLineEdit()
        self.btn_browse_pl = QPushButton("Browse")
        h2.addWidget(self.edit_pl)
        h2.addWidget(self.btn_browse_pl)
        peek_layout.addLayout(h2)

        h3 = QHBoxLayout()
        self.btn_peek = QPushButton("Peek Memory")
        h3.addWidget(self.btn_peek)
        peek_layout.addLayout(h3)
        layout.addWidget(peek_group)

        # FUSE Group
        fuse_group = QGroupBox("FUSE Filesystem")
        fuse_layout = QVBoxLayout(fuse_group)
        
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("Mount Point:"))
        self.edit_mount = QLineEdit("/mnt/mtk")
        self.check_rw = QCheckBox("Read/Write")
        self.btn_mount = QPushButton("Mount FS")
        h4.addWidget(self.edit_mount)
        h4.addWidget(self.check_rw)
        h4.addWidget(self.btn_mount)
        fuse_layout.addLayout(h4)
        layout.addWidget(fuse_group)

        # Brom to Offs Group
        brom_to_offs_group = QGroupBox("Brom to Offsets (Header Generator)")
        brom_to_offs_layout = QVBoxLayout(brom_to_offs_group)
        h5 = QHBoxLayout()
        h5.addWidget(QLabel("BROM Dump:"))
        self.edit_brom_file = QLineEdit()
        self.btn_browse_brom = QPushButton("Browse")
        h5.addWidget(self.edit_brom_file)
        h5.addWidget(self.btn_browse_brom)
        brom_to_offs_layout.addLayout(h5)
        self.btn_gen_header = QPushButton("Generate Header (brom_to_offs)")
        brom_to_offs_layout.addWidget(self.btn_gen_header)
        layout.addWidget(brom_to_offs_group)

        # DA Parser Group
        da_parser_group = QGroupBox("DA Parser (Analyze Download Agent)")
        da_parser_layout = QVBoxLayout(da_parser_group)
        h6 = QHBoxLayout()
        h6.addWidget(QLabel("DA Loader:"))
        self.edit_da_file = QLineEdit()
        self.btn_browse_da = QPushButton("Browse")
        h6.addWidget(self.edit_da_file)
        h6.addWidget(self.btn_browse_da)
        da_parser_layout.addLayout(h6)
        self.btn_parse_da = QPushButton("Parse DA (da_parser)")
        da_parser_layout.addWidget(self.btn_parse_da)
        layout.addWidget(da_parser_group)

        layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Connect buttons
        self.btn_get_logs.clicked.connect(self.get_logs)
        self.btn_browse_pl.clicked.connect(lambda: self.browse_file(self.edit_pl))
        self.btn_peek.clicked.connect(self.peek_memory)
        self.btn_mount.clicked.connect(self.mount_fs)
        self.btn_browse_brom.clicked.connect(lambda: self.browse_file(self.edit_brom_file))
        self.btn_gen_header.clicked.connect(self.gen_header)
        self.btn_browse_da.clicked.connect(lambda: self.browse_file(self.edit_da_file))
        self.btn_parse_da.clicked.connect(self.parse_da)

    def parse_da(self):
        da_file = self.edit_da_file.text()
        if not da_file: return
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.parse_da_async, parameters=[da_file])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def parse_da_async(self, toolkit, parameters):
        da_file = parameters[0]
        from mtkclient.Tools.da_parser import main as da_main
        import sys
        old_argv = sys.argv
        sys.argv = ["da_parser", da_file]
        try:
            da_main()
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"Error: {str(e)}")
        finally:
            sys.argv = old_argv
        self.enableButtonsSignal.emit()

    def gen_header(self):
        brom_file = self.edit_brom_file.text()
        if not brom_file: return
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.gen_header_async, parameters=[brom_file])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def gen_header_async(self, toolkit, parameters):
        brom_file = parameters[0]
        from mtkclient.Tools.brom_to_offs import main as brom_main
        import sys
        old_argv = sys.argv
        sys.argv = ["brom_to_offs", brom_file]
        try:
            brom_main()
        except Exception as e:
            toolkit.sendToLogSignal.emit(f"Error: {str(e)}")
        finally:
            sys.argv = old_argv
        self.enableButtonsSignal.emit()

    def browse_file(self, lineedit):
        fname = self.fdialog.open()
        if fname: lineedit.setText(fname)

    def get_logs(self):
        filename = self.fdialog.save("log.txt")
        if filename:
            self.disableButtonsSignal.emit()
            thread = asyncThread(parent=self.parent, n=0, function=self.get_logs_async, parameters=[filename])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.start()

    def get_logs_async(self, toolkit, parameters):
        filename = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = "logs"
        v.filename = filename
        from mtkclient.Library.mtk_main import Main
        Main(v).run(None)
        self.enableButtonsSignal.emit()

    def peek_memory(self):
        filename = self.fdialog.save("peek_dump.bin")
        if not filename: return
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.peek_memory_async, parameters=[filename])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def peek_memory_async(self, toolkit, parameters):
        filename = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = "peek"
        v.address = self.edit_addr.text()
        v.length = self.edit_len.text()
        v.preloader = self.edit_pl.text() if self.edit_pl.text() else None
        v.filename = filename
        from mtkclient.Library.mtk_main import Main
        Main(v).run(None)
        self.enableButtonsSignal.emit()

    def mount_fs(self):
        mountpoint = self.edit_mount.text()
        rw = self.check_rw.isChecked()
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.mount_fs_async, parameters=[mountpoint, rw])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def mount_fs_async(self, toolkit, parameters):
        mountpoint, rw = parameters
        v = self.parent.settings.get_variables()
        v.cmd = "fs"
        v.mountpoint = mountpoint
        v.rw = rw
        self.da_handler.handle_da_cmds(self.mtkClass, "fs", v)
        self.enableButtonsSignal.emit()

    def setEnabled(self, enabled):
        self.tab.setEnabled(enabled)

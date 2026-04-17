import os
from unittest import mock
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGroupBox, QPlainTextEdit
from mtkclient.gui.toolkit import asyncThread, FDialog

class ScriptingWindow(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, da_handler, sendToLog):
        super(ScriptingWindow, self).__init__(parent)
        self.mtkClass = da_handler.mtk
        self.parent = parent
        self.sendToLog = sendToLog
        self.da_handler = da_handler
        self.ui = ui
        self.fdialog = FDialog(parent)
        self.setup_ui()

    def setup_ui(self):
        self.tab = QWidget()
        layout = QVBoxLayout(self.tab)

        # Script Group
        script_group = QGroupBox("Run Script")
        script_layout = QVBoxLayout(script_group)
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Script File:"))
        self.edit_script = QLineEdit()
        self.btn_browse_script = QPushButton("Browse")
        h1.addWidget(self.edit_script)
        h1.addWidget(self.btn_browse_script)
        script_layout.addLayout(h1)
        self.btn_run_script = QPushButton("Run Script")
        script_layout.addWidget(self.btn_run_script)
        layout.addWidget(script_group)

        # Multi-command Group
        multi_group = QGroupBox("Multi-Command")
        multi_layout = QVBoxLayout(multi_group)
        multi_layout.addWidget(QLabel("Commands (semicolon separated):"))
        self.edit_multi = QPlainTextEdit()
        self.btn_run_multi = QPushButton("Run Multi-Command")
        multi_layout.addWidget(self.edit_multi)
        multi_layout.addWidget(self.btn_run_multi)
        layout.addWidget(multi_group)

        # Devices Group
        devices_group = QGroupBox("Supported Devices")
        devices_layout = QHBoxLayout(devices_group)
        devices_layout.addWidget(QLabel("Filter:"))
        self.edit_filter = QLineEdit()
        self.btn_list_devices = QPushButton("List Devices")
        devices_layout.addWidget(self.edit_filter)
        devices_layout.addWidget(self.btn_list_devices)
        layout.addWidget(devices_group)

        layout.addStretch()

        # Connect buttons
        self.btn_browse_script.clicked.connect(lambda: self.browse_file(self.edit_script))
        self.btn_run_script.clicked.connect(self.run_script)
        self.btn_run_multi.clicked.connect(self.run_multi)
        self.btn_list_devices.clicked.connect(self.list_devices)

    def browse_file(self, lineedit):
        fname = self.fdialog.open()
        if fname: lineedit.setText(fname)

    def run_script(self):
        script = self.edit_script.text()
        if script:
            self.disableButtonsSignal.emit()
            thread = asyncThread(parent=self.parent, n=0, function=self.run_script_async, parameters=[script])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.start()

    def run_script_async(self, toolkit, parameters):
        script = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = "script"
        v.script = script
        from mtkclient.Library.mtk_main import Main
        Main(v).run(None)
        self.enableButtonsSignal.emit()

    def run_multi(self):
        commands = self.edit_multi.toPlainText().replace("\n", " ")
        if commands:
            self.disableButtonsSignal.emit()
            thread = asyncThread(parent=self.parent, n=0, function=self.run_multi_async, parameters=[commands])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.start()

    def run_multi_async(self, toolkit, parameters):
        commands = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = "multi"
        v.commands = commands
        from mtkclient.Library.mtk_main import Main
        Main(v).run(None)
        self.enableButtonsSignal.emit()

    def list_devices(self):
        self.disableButtonsSignal.emit()
        thread = asyncThread(parent=self.parent, n=0, function=self.list_devices_async, parameters=[self.edit_filter.text()])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.start()

    def list_devices_async(self, toolkit, parameters):
        filter_text = parameters[0]
        v = self.parent.settings.get_variables()
        v.cmd = "devices"
        v.filter = filter_text if filter_text else None
        from mtkclient.Library.mtk_main import Main
        Main(v).run(None)
        self.enableButtonsSignal.emit()

    def setEnabled(self, enabled):
        self.tab.setEnabled(enabled)

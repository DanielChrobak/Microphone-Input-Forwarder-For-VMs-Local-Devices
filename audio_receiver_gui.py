import sys
import pyaudio
import socket
import struct
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QProgressBar, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QProgressBar, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
EPSILON = 1e-10

class ReceiverThread(QThread):
    connection_status = pyqtSignal(bool)
    volume_update = pyqtSignal(float)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False

    def run(self):
        p = pyaudio.PyAudio()
        device_index = self.get_output_device_index(p, 'Cable Input')
        if device_index is None:
            print('Could not find Cable Input device')
            return

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        output=True, output_device_index=device_index,
                        frames_per_buffer=CHUNK)

        print(f'Playing audio to: {p.get_device_info_by_index(device_index)["name"]}')

        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.host, self.port))
                    print(f'Connected to {self.host}:{self.port}')
                    self.connection_status.emit(True)
                    while self.running:
                        length = struct.unpack('!I', sock.recv(4))[0]
                        data = sock.recv(length)
                        if not data:
                            break
                        stream.write(data)
                        
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        rms = np.sqrt(np.mean(np.square(audio_data.astype(float))) + EPSILON)
                        db = 20 * np.log10(rms / 32767 + EPSILON)
                        self.volume_update.emit(db)
            except ConnectionRefusedError:
                print(f'Could not connect to {self.host}:{self.port}. Retrying...')
                self.connection_status.emit(False)
            except (ConnectionResetError, struct.error):
                print('Server disconnected. Attempting to reconnect...')
                self.connection_status.emit(False)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def get_output_device_index(self, p, device_name):
        for i in range(p.get_device_count()):
            if device_name.lower() in p.get_device_info_by_index(i)['name'].lower():
                return i
        return None

class AudioReceiverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initSystemTray()

    def initUI(self):
        self.setWindowTitle('Audio Receiver')
        self.setGeometry(300, 300, 300, 250)

        layout = QVBoxLayout()

        host_layout = QHBoxLayout()
        host_label = QLabel('Host IP:')
        self.host_input = QLineEdit()
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        layout.addLayout(host_layout)

        port_layout = QHBoxLayout()
        port_label = QLabel('Port:')
        self.port_input = QLineEdit()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        self.status_label = QLabel('Status: Not Connected')
        layout.addWidget(self.status_label)

        self.start_button = QPushButton('Start Receiving')
        self.start_button.clicked.connect(self.toggle_receiving)
        layout.addWidget(self.start_button)

        volume_layout = QHBoxLayout()
        volume_label = QLabel('Volume:')
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)
        self.volume_bar.setTextVisible(False)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_bar)
        layout.addLayout(volume_layout)

        self.setLayout(layout)

        self.receiver_thread = None

    def initSystemTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        icon = self.create_tray_icon()
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.tray_icon.show()

    def create_tray_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.red))
        painter.drawEllipse(0, 0, 32, 32)
        painter.end()
        return QIcon(pixmap)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Audio Receiver",
            "Application was minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )

    def quit_application(self):
        if self.receiver_thread and self.receiver_thread.running:
            self.receiver_thread.running = False
            self.receiver_thread.quit()
            self.receiver_thread.wait()
        QApplication.quit()

    def toggle_receiving(self):
        if self.receiver_thread is None or not self.receiver_thread.running:
            try:
                host = self.host_input.text()
                port = int(self.port_input.text())
                self.receiver_thread = ReceiverThread(host, port)
                self.receiver_thread.connection_status.connect(self.update_status)
                self.receiver_thread.volume_update.connect(self.update_volume)
                self.receiver_thread.running = True
                self.receiver_thread.start()
                self.start_button.setText('Stop Receiving')
                self.status_label.setText('Status: Connecting...')
            except ValueError:
                self.status_label.setText('Status: Invalid port number')
        else:
            self.receiver_thread.running = False
            self.receiver_thread.quit()
            self.receiver_thread.wait()
            self.start_button.setText('Start Receiving')
            self.status_label.setText('Status: Not Connected')
            self.volume_bar.setValue(0)

    def update_status(self, connected):
        if connected:
            self.status_label.setText('Status: Connected')
            self.status_label.setStyleSheet('color: green')
        else:
            self.status_label.setText('Status: Disconnected')
            self.status_label.setStyleSheet('color: red')

    def update_volume(self, db):
        if np.isfinite(db):
            db_clamped = max(-60, min(0, db))
            value = int((db_clamped + 60) / 60 * 100) 
            self.volume_bar.setValue(value)
        else:
            self.volume_bar.setValue(0)

        self.volume_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 red, stop:0.5 yellow, stop:1 green);
            }}
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioReceiverGUI()
    ex.show()
    sys.exit(app.exec_())

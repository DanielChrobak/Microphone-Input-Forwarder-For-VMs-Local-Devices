import sys
import pyaudio
import socket
import struct
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HOST = '0.0.0.0'

class StreamerThread(QThread):
    connection_status = pyqtSignal(bool)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = False

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((HOST, self.port))
            sock.listen(1)
            print(f'Waiting for connection on {HOST}:{self.port}')
            
            while self.running:
                try:
                    conn, addr = sock.accept()
                    print(f'Connected by {addr}')
                    self.connection_status.emit(True)
                    try:
                        while self.running:
                            data = stream.read(CHUNK, exception_on_overflow=False)
                            conn.sendall(struct.pack('!I', len(data)) + data)
                    except (ConnectionResetError, BrokenPipeError):
                        print(f'Client {addr} disconnected')
                    finally:
                        conn.close()
                        self.connection_status.emit(False)
                except Exception as e:
                    print(f"Error: {e}")
                    self.connection_status.emit(False)

        stream.stop_stream()
        stream.close()
        p.terminate()

class AudioStreamerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Audio Streamer')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        port_label = QLabel('Port:')
        self.port_input = QLineEdit()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        self.status_label = QLabel('Status: Not Connected')
        layout.addWidget(self.status_label)

        self.start_button = QPushButton('Start Streaming')
        self.start_button.clicked.connect(self.toggle_streaming)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

        self.streamer_thread = None

    def toggle_streaming(self):
        if self.streamer_thread is None or not self.streamer_thread.running:
            try:
                port = int(self.port_input.text())
                self.streamer_thread = StreamerThread(port)
                self.streamer_thread.connection_status.connect(self.update_status)
                self.streamer_thread.running = True
                self.streamer_thread.start()
                self.start_button.setText('Stop Streaming')
                self.status_label.setText('Status: Waiting for connection')
            except ValueError:
                self.status_label.setText('Status: Invalid port number')
        else:
            self.streamer_thread.running = False
            self.streamer_thread.quit()
            self.streamer_thread.wait()
            self.start_button.setText('Start Streaming')
            self.status_label.setText('Status: Not Connected')

    def update_status(self, connected):
        if connected:
            self.status_label.setText('Status: Connected')
            self.status_label.setStyleSheet('color: green')
        else:
            self.status_label.setText('Status: Disconnected')
            self.status_label.setStyleSheet('color: red')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioStreamerGUI()
    ex.show()
    sys.exit(app.exec_())

import sys
import pyaudio
import socket
import struct

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HOST = '0.0.0.0'

def stream_audio(port):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, port))
        sock.listen(1)
        print(f'Waiting for connection on {HOST}:{port}')

        try:
            while True:
                conn, addr = sock.accept()
                print(f'Connected by {addr}')
                try:
                    while True:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                        conn.sendall(struct.pack('!I', len(data)) + data)
                except (ConnectionResetError, BrokenPipeError):
                    print(f'Client {addr} disconnected')
                finally:
                    conn.close()
        except KeyboardInterrupt:
            print("\nStreaming stopped by user")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python audio_streamer.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    stream_audio(port)
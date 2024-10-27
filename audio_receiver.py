import sys
import pyaudio
import socket
import struct

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def get_output_device_index(p, device_name):
    for i in range(p.get_device_count()):
        if device_name.lower() in p.get_device_info_by_index(i)['name'].lower():
            return i
    return None

def receive_audio(host, port):
    p = pyaudio.PyAudio()
    device_index = get_output_device_index(p, 'Cable Input')
    if device_index is None:
        print('Could not find Cable Input device')
        return

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    output=True, output_device_index=device_index,
                    frames_per_buffer=CHUNK)
    print(f'Playing audio to: {p.get_device_info_by_index(device_index)["name"]}')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            print(f'Connected to {host}:{port}')

            while True:
                length = struct.unpack('!I', sock.recv(4))[0]
                data = sock.recv(length)
                if not data:
                    break
                stream.write(data)

    except ConnectionRefusedError:
        print(f'Could not connect to {host}:{port}')
    except (ConnectionResetError, struct.error):
        print('Server disconnected')
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python audio_receiver.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    receive_audio(host, port)
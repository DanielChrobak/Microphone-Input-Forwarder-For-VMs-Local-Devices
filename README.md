# Audio Streaming System

This project consists of two Python scripts that work together to create an audio streaming system. The `audio_streamer.py` captures audio from a microphone and streams it over a network to a receiver, while the `audio_receiver.py` receives the audio stream and plays it through a virtual audio device which acts as a virtual microphone/input.

## Requirements

- Windows operating system
- Python 3.7+
- PyQt5
- PyAudio
- NumPy
- VB-CABLE Virtual Audio Device (for the receiver device)

## Installation

1. Clone this repository or download the `audio_streamer.py` and `audio_receiver.py` files.

2. Install the required Python packages:

> pip install pyqt5 pyaudio numpy

3. On the receiving computer, install the VB-CABLE Virtual Audio Device:
- Download and install VB-CABLE from [https://vb-audio.com/Cable/](https://vb-audio.com/Cable/)
- Follow the installation instructions provided on the website

## Usage

### Audio Streamer

1. Run the audio streamer on the computer that will capture and send microphone audio:

python audio_streamer.py

2. Enter the desired port number in the GUI.

3. Click "Start Streaming" to begin capturing and streaming audio.

### Audio Receiver

1. Run the audio receiver on the computer that will play the streamed audio:

python audio_receiver.py

2. Enter the IP address of the streaming computer and the port number used by the streamer.

3. Click "Start Receiving" to begin receiving and playing the audio stream.

## Important Notes

- This system is designed for Windows only.
- The computer running the audio receiver must have the VB-CABLE Virtual Audio Device installed.
- Ensure that your firewall allows the connection between the streamer and receiver.
- The audio quality and latency may vary depending on your network conditions.

## Troubleshooting

- If you encounter issues with audio playback, make sure the VB-CABLE is set as the default playback device in your Windows sound settings.
- Check that the correct input device is being used for audio capture on the streaming computer.
- Verify that the IP address and port numbers match between the streamer and receiver.

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- VB-Audio for their VB-CABLE Virtual Audio Device
- The PyAudio and PyQt5 communities for their excellent libraries

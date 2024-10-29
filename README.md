# Audio Streaming System

This project consists of two Python scripts that work together to create an audio streaming system. The `audio_streamer_gui.py` and `audio_streamer.py` capture audio from a microphone and streams it over a network to a receiver, while the `audio_receiver_gui.py` and `audio_receiver.py` receive the audio stream and plays it through a virtual audio device which acts as a virtual microphone/input.

## Background

This project was born out of a need for remote microphone input in a GPU-partitioned Hyper-V VM setup. The broader context involves:

- A single, powerful computer running in a centralized location (e.g., basement)
- Multiple VMs running on this computer, each serving as a personal computer for family members
- Sunshine installed on each VM to stream the desktop
- Thin clients (like OPi 5+ or RPi 5) running Moonlight to connect to these streams

This setup offers several advantages:
1. Cost-effective: One powerful computer instead of multiple individual PCs
2. Space-saving: Thin clients take up minimal space in living areas
3. Centralized management: Easier to maintain and upgrade a single system

However, this setup faced a challenge: Moonlight, the streaming client, doesn't support microphone input. This Audio Streaming System aims to solve that problem by allowing remote microphone streaming from the thin clients to the VMs.

## Project Overview

The Audio Streaming System consists of two main components, each available in both GUI and CLI versions:

1. Audio Streamer: Runs on the thin client, capturing audio from the local microphone and streaming it over the network.
2. Audio Receiver: Runs on the VM, receiving the audio stream and playing it through a virtual audio device, effectively creating a virtual microphone input.

This solution enables full audio input functionality in the GPU-partitioned VM setup, complementing the Sunshine/Moonlight streaming system.

## Requirements

- Python 3.7+
- PyAudio
- VB-CABLE Virtual Audio Device (for the receiver device)
- PyQt5 (for GUI versions only)
- NumPy (for GUI versions only)

## Installation

1. Clone this repository or download the audio streamer and receiver files.

2. Install the required Python packages:

   For CLI versions:
   > pip install pyaudio

   For GUI versions:
   > pip install pyqt5 pyaudio numpy

3. On the receiving computer, install the VB-CABLE Virtual Audio Device:
- Download and install VB-CABLE from [https://vb-audio.com/Cable/](https://vb-audio.com/Cable/)
- Follow the installation instructions provided on the website

## Usage

### CLI Versions

#### Audio Streamer (CLI)

1. Run the audio streamer on the computer that will capture and send microphone audio:

> python audio_streamer.py <port>

Replace `<port>` with the desired port number.

2. The streamer will start waiting for a connection on the specified port.

#### Audio Receiver (CLI)

1. Run the audio receiver on the computer that will play the streamed audio:

> python audio_receiver.py <host> <port>

Replace `<host>` with the IP address of the streaming computer and `<port>` with the port number used by the streamer.

2. The receiver will attempt to connect to the streamer and start playing the received audio through the VB-CABLE device.

### GUI Versions

#### Audio Streamer (GUI)

1. Run the audio streamer on the computer that will capture and send microphone audio:

> python audio_streamer_gui.py

2. Enter the desired port number in the GUI.

3. Click "Start Streaming" to begin capturing and streaming audio.

#### Audio Receiver (GUI)

1. Run the audio receiver on the computer that will play the streamed audio:

> python audio_receiver_gui.py

2. Enter the IP address of the streaming computer and the port number used by the streamer.

3. Click "Start Receiving" to begin receiving and playing the audio stream.


## Important Notes

- This system has been designed and tested on Windows, but should work on Linux as well with some changes to the input and output.
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

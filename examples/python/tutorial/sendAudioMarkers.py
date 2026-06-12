"""
LSL example - playing audio and sending a trigger.
"""

import argparse
import os

import sounddevice as sd
import soundfile as sf
from pylsl import StreamInfo, StreamOutlet


def parse_args():
    parser = argparse.ArgumentParser(description="Play audio and send LSL markers.")
    parser.add_argument(
        "--audio-file",
        default=os.getenv("LSL_AUDIO_FILE"),
        help="Path to .wav file. Can also be provided via LSL_AUDIO_FILE.",
    )
    parser.add_argument(
        "--trigger-mode",
        choices=["enter", "immediate"],
        default=os.getenv("LSL_TRIGGER_MODE", "enter"),
        help="enter: wait for ENTER before each playback, immediate: play in a loop without prompt.",
    )
    return parser.parse_args()


def wait_for_keypress():
    print("Press ENTER to start audio playback and send an LSL marker.")
    while True:
        input_str = input()
        if input_str == "":
            break


def audio_marker(audio_file, outlet):
    data, fs = sf.read(audio_file)

    print("Playing audio and sending LSL marker...")
    marker_val = [1]
    outlet.push_sample(marker_val)
    sd.play(data, fs)
    sd.wait()
    print("Audio playback finished.")


def main():
    args = parse_args()
    if not args.audio_file:
        raise ValueError("No audio file configured. Use --audio-file or set LSL_AUDIO_FILE.")

    stream_name = "AudioMarkers"
    stream_type = "Markers"
    n_chans = 1
    sr = 0
    chan_format = "int32"
    marker_id = "uniqueMarkerID12345"

    info = StreamInfo(stream_name, stream_type, n_chans, sr, chan_format, marker_id)
    outlet = StreamOutlet(info)

    while True:
        if args.trigger_mode == "enter":
            wait_for_keypress()
        audio_marker(args.audio_file, outlet)


if __name__ == "__main__":
    main()

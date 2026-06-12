"""Example program to show how to read a multi-channel time series from LSL."""
import argparse
import os
from pylsl import StreamInlet, resolve_stream

STREAM_TYPES = {
    1: "EEG",
    2: "Motion",
    3: "Contact-Quality",
    4: "EEG-Quality",
    5: "Performance-Metrics",
    6: "Band-Power",
}


def process_stream(stream_type):
    streams = resolve_stream("type", stream_type)
    if streams:
        return streams[0]
    return None


def parse_args():
    parser = argparse.ArgumentParser(description="Receive and print samples from an LSL stream.")
    parser.add_argument(
        "--stream-type",
        help=(
            "LSL stream type name (for example: EEG, Motion). "
            "Can also be provided with LSL_STREAM_TYPE."
        ),
    )
    parser.add_argument(
        "--stream-type-index",
        type=int,
        choices=sorted(STREAM_TYPES.keys()),
        help=(
            "Numeric stream type index. "
            "Can also be provided with LSL_STREAM_TYPE_INDEX."
        ),
    )
    return parser.parse_args()


def get_stream_type(args):
    stream_type = args.stream_type or os.getenv("LSL_STREAM_TYPE")
    if stream_type:
        return stream_type

    index_raw = args.stream_type_index
    if index_raw is None:
        env_idx = os.getenv("LSL_STREAM_TYPE_INDEX")
        if env_idx is not None:
            index_raw = int(env_idx)

    if index_raw is not None:
        return STREAM_TYPES[index_raw]

    raise ValueError(
        "No stream type configured. Set --stream-type or --stream-type-index, "
        "or LSL_STREAM_TYPE / LSL_STREAM_TYPE_INDEX."
    )


def main():
    args = parse_args()
    stream_type = get_stream_type(args)
    selected_stream = process_stream(stream_type)

    if not selected_stream:
        raise RuntimeError(f"No matching stream found for type '{stream_type}'.")

    print(f"Selected stream: {selected_stream.name()}")

    inlet = StreamInlet(selected_stream)
    info = inlet.info()
    print(f"\nThe manufacturer is: {info.desc().child_value('manufacturer')}")
    print("The channel labels are listed below:")
    ch = info.desc().child("channels").child("channel")
    labels = []
    for _ in range(info.channel_count()):
        labels.append(ch.child_value("label"))
        ch = ch.next_sibling()
    print(f"  {', '.join(labels)}")

    print("Now pulling samples...")

    while True:
        sample, timestamp = inlet.pull_sample()
        if timestamp is not None:
            print(sample)


if __name__ == "__main__":
    main()

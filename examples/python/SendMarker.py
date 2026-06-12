import argparse
import os
import time
from pylsl import StreamInfo, StreamOutlet, local_clock


def get_epoch_now():
    return time.time()


def parse_args():
    parser = argparse.ArgumentParser(description="Send marker samples to an LSL outlet.")
    parser.add_argument(
        "--option",
        type=int,
        choices=[1, 2],
        help="1: marker value only, 2: marker with explicit timestamp.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=float(os.getenv("LSL_MARKER_INTERVAL_SECONDS", "2")),
        help="Delay between markers (defaults to env LSL_MARKER_INTERVAL_SECONDS or 2).",
    )
    return parser.parse_args()


def resolve_option(cli_option):
    if cli_option is not None:
        return cli_option
    env_option = os.getenv("LSL_MARKER_OPTION")
    if env_option:
        return int(env_option)
    return 1


def main():
    args = parse_args()
    option = resolve_option(args.option)

    if option == 1:
        n_channel = 1
        channels = ["MarkerValue"]
        print("Start with Option 1")
    elif option == 2:
        n_channel = 3
        channels = ["MarkerTime", "MarkerValue", "TimeSent"]
        print("Start with Option 2")
    else:
        raise ValueError("Invalid option. Use 1 or 2 (or set LSL_MARKER_OPTION).")

    info = StreamInfo(
        name="SimpleMarker",
        type="Markers",
        channel_count=n_channel,
        channel_format="double64",
        source_id="Outlet1234",
    )

    chns = info.desc().append_child("channels")
    for channel in channels:
        chns.append_child("channel").append_child_value("label", channel).append_child_value("type", "Marker")

    outlet = StreamOutlet(info)
    print("Now sending data...")

    marker_value = 1
    while True:
        if option == 1:
            now = get_epoch_now()
            print(f"Marker, {marker_value}, {now}")
            outlet.push_sample([marker_value])
        else:
            current_time = get_epoch_now()
            marker_time = current_time - 0.05
            sample = [marker_time, marker_value, current_time]
            print(f"Marker with a timestamp, {marker_value}, {sample[0]}, {local_clock()}")
            outlet.push_sample(sample)

        marker_value += 1
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()

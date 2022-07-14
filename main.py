import sys
import json
import argparse
from video_download import VideoDownloader
from video_crop import VideoCroping
from most_replayed import MostReplayedHeatMap

parser = argparse.ArgumentParser(description="Test opetions")


"""Module Video Download and Crops

    Configs provide environment values like db scheme, file path, const values
    if value from file that ./secrets.json or os env(export DB=mysql:127.0.0.1)

    Typical usage example:

    config = Configs()ß
    credential = config.get_attr('CREDENTIAL')

    credential = Configs.instance().get_attr('CREDENTIAL')
"""

parser.add_argument("--type", required=True, help="operation type")
parser.add_argument(
    "--plugins",
    required=False,
    help="plug most replayed handling,  type d, plug h|c, download -> heapmap -> crop",
)
parser.add_argument(
    "--shorts", required=False, help="make for short video", action="store_true"
)
parser.add_argument("--out", required=False, help="video out folder")
parser.add_argument("--outfile", required=False, help="video out file name")
parser.add_argument("--vid", required=False, help="video id")
parser.add_argument("--file", required=False, help="video id")
parser.add_argument("--start", required=False, help="video crop start time(second)")
parser.add_argument("--end", required=False, help="video crop end time(second")
parser.add_argument("--width", required=False, help="video crop start time(second)")
parser.add_argument("--height", required=False, help="video crop end time(second")
parser.add_argument(
    "--progress", required=False, help="show progressbar", action="store_true"
)
parser.add_argument(
    "--crop",
    required=False,
    help="not resize crop video resolution",
    action="store_true",
)
parser.add_argument(
    "--frame",
    required=False,
    help="show video frame on progressing",
    action="store_true",
)

args = parser.parse_args()


def get_video_highlite_term(args):

    """return star, end second most replayed moment
    Args:
        args:
            video_id: youtube video id
            heat_minute: return center 1 min time for shorts
    Returns:
        start_second, end_second
    """
    video_id = None
    heat_minute = None

    if args.vid:
        video_id = args.vid

    if args.shorts:
        heat_minute = True

    mr = MostReplayedHeatMap(video_id)
    result = mr.extract_heatmap_data()

    bigest_maker = None
    for marker in result:
        if bigest_maker is None:
            bigest_maker = marker
        elif (
            bigest_maker["heatMarkerIntensityScoreNormalized"]
            < marker["heatMarkerIntensityScoreNormalized"]
        ):
            bigest_maker = marker

    if bigest_maker is not None:
        start_second = int(bigest_maker["timeRangeStartMillis"] / 1000)
        end_second = int(
            bigest_maker["timeRangeStartMillis"] / 1000
            + bigest_maker["markerDurationMillis"] / 1000
        )
        if heat_minute:
            if end_second - start_second > 60:
                center = end_second - start_second / 2
                heat_min_start = start_second + int(center / 2)
                heat_min_end = end_second - int(center / 2)
                return heat_min_start, heat_min_end

        heat_min_start = start_second
        heat_min_end = end_second
        return heat_min_start, heat_min_end


def crop_video(args):

    file_path = None
    file_name = None
    out = None
    progressbar = False
    frame = False

    start = None
    end = None

    plugs = []
    if args.plugins:
        plugs = args.plugins.split("|")

    for plug in plugs:
        if plug == "t":
            start_second, end_second = get_video_highlite_term(args)
            args.start = start_second
            args.end = end_second

    if args.file:
        file_path = args.file

    if args.progress:
        progressbar = True

    if args.frame:
        frame = True

    if args.start:
        start = int(args.start)

    if args.end:
        end = int(args.end)

    if args.out:
        out = args.out

    if args.outfile:
        file_name = args.outfile

    video_crop = VideoCroping(progressbar, frame)
    video_crop.crop(
        file_path, start_time=start, end_time=end, out=out, out_file_name=file_name
    )


def download_video(args):
    """download youtube video
    Args:
        args:
            args.type == download or d
            args.vid: youtoube video id
            args.out: download output foler
            args.progress: show progress
    Returns:
        None
    """
    video_id = None
    out = None
    progressbar = False
    plugs = []
    if args.vid:
        video_id = args.vid
    else:
        print("Please input video id")
        return

    if args.out:
        out = args.out

    if args.progress:
        progressbar = True

    if args.plugins:
        plugs = args.plugins.split("|")

    video_download = VideoDownloader(progressbar)

    start_second = None
    end_second = None
    for plug in plugs:
        if plug == "t":
            start_second, end_second = get_video_highlite_term(args)
            args.start = start_second
            args.end = end_second
        if plug == "c":
            if args.outfile is None:
                args.outfile = f"{video_id}_HL.mp4"
            if args.file is None:
                args.file = f"{out}/{video_id}_HL.mp4"

            crop_video(args)


def main(argv):
    if args.type == "d":
        download_video(args)
    if args.type == "c":
        crop_video(args)
    if args.type == "k":
        args.plugins = "t|c"
        download_video(args)


if __name__ == "__main__":
    main(sys.argv)

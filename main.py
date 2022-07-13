import sys
import json
import argparse
import video_download
import video_crop

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
parser.add_argument("--out", required=False, help="video out folder")
parser.add_argument("--vid", required=False, help="video id")
parser.add_argument("--file", required=False, help="video id")
parser.add_argument("--start", required=False, help="video id")
parser.add_argument("--end", required=False, help="video id")

args = parser.parse_args()


def crop_video(args):
    file_path = None
    if args.file:
        file_path = args.file

    video_crop.crop(file_path)


def download_video(args):

    """download youtube video
    Args:
        args:
            args.type == download or d
            args.vid: youtoube video id
            args.out: download output foler
    Returns:
        None
    """

    video_id = None
    out = None
    if args.vid:
        video_id = args.vid
    else:
        print("Please input video id")
        return

    if args.out:
        out = args.out

    print("Download Video: ", video_id)
    print("Download Folder: ", out)

    success = video_download.download(video_id, out)
    print("Youtube video download result: ", success)


def main(argv):
    if args.type == "d":
        download_video(args)
    if args.type == "c":
        crop_video(args)


if __name__ == "__main__":
    main(sys.argv)

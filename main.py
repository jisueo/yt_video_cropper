import sys
import os
import argparse
from video_download import VideoDownloader
from video_crop import VideoCroping
from most_replayed import MostReplayedHeatMap
from gs_uploader import upload_file
from shot_detections import analyze_shots_offset
from shutil import copyfile
from vision import vision_processing
import pathlib
import json

parser = argparse.ArgumentParser(description="Test opetions")


"""Module Video Download and Crops

    Configs provide environment values like db scheme, file path, const values
    if value from file that ./secrets.json or os env(export DB=mysql:127.0.0.1)

    Typical usage example:

    config = Configs()
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
parser.add_argument("--file", required=False, help="video file")
parser.add_argument("--json", required=False, help="make json result file", action="store_true")
parser.add_argument("--start", required=False, help="video crop start time(second)")
parser.add_argument("--end", required=False, help="video crop end time(second")
parser.add_argument("--width", required=False, help="video crop start time(second)")
parser.add_argument("--height", required=False, help="video crop end time(second")
parser.add_argument("--images", required=False, help="Images location folder path")
parser.add_argument("--threshold", required=False, help="Images similarity threshold")
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
parser.add_argument(
    "--gs",
    required=False,
    help="store download video google storage",
    action="store_true",
)

parser.add_argument(
    "--sd",
    required=False,
    help="video shot detection",
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

    heat_mil_start, heat_mil_end, _ = mr.extract_most_replayed_term()
    print(heat_mil_start, heat_mil_end)

    """
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
    """
    heat_min_start = int(heat_mil_start / 1000)
    heat_min_end = int(heat_mil_end / 1000)
    return heat_min_start, heat_min_end


def crop_video(args):

    file_path = None
    file_name = None
    out = None
    progressbar = False
    frame = False

    start = None
    end = None

    width = None
    height = None

    plugs = []
    if args.plugins is not None:
        plugs = args.plugins.split("|")

    for plug in plugs:
        if plug == "t":
            start_second, end_second = get_video_highlite_term(args)
            args.start = start_second
            args.end = end_second

    if args.file is not None:
        file_path = args.file

    if args.progress is not None:
        progressbar = True

    if args.frame is not None:
        frame = True

    if args.start is not None:
        start = int(args.start)

    if args.end is not None:
        end = int(args.end)

    if args.width is not None:
        width = int(args.width)

    if args.height is not None:
        height = int(args.height)

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
        args.plugins = None

    video_download = VideoDownloader(progressbar)
    download_file_path = video_download.download(video_id, out)
    if args.gs:
        upload_file(download_file_path)
    
    start_second = None
    end_second = None

    for plug in plugs:
        if plug == "t":
            print("start get term")
            start_second, end_second = get_video_highlite_term(args)
            args.start = start_second
            args.end = end_second
        if plug == "c":
            print("start extract highlight")
            print("start extract highlight start, end", args.start, args.end)

            if args.outfile is None:
                args.outfile = f"{video_id}_HL.mp4"
            if args.file is None:
                args.file = f"{out}/{video_id}.mp4"

            crop_video(args)

def shot_detect_video(args):
    video_id = None
    if args.vid:
        video_id = args.vid
    
    file_path = None
    if args.file is not None:
        file_path = args.file
    else:
        file_path = f"./downloads/{video_id}.mp4"

    out = None
    if args.out is not None:
        out = args.out

    json = None
    if args.json is not None:
        json = True

    if video_id is not None:
        offset_datas = analyze_shots_offset(video_id)
        times = list(map(lambda x:x["time"], offset_datas))
        progress = False
        if args.progress:
            progressbar = True
        frame = False
        if args.frame is not None:
            frame = True
        vc = VideoCroping(progress, frame)
        vc.capture(file_path, f"{out}/{video_id}", times)

def simularity_image_remove(args):
    out = None
    if args.out is not None:
        out = args.out

    image_folder = None
    if args.images is not None:
        image_folder = args.images

    score_threshold = 75
    if args.threshold is not None:
        score_threshold = int(args.threshold)
        
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    file_path_list = list(map(lambda x:f"{image_folder}/{x}" ,image_files))
    file_path_list = list(filter(lambda x: pathlib.Path(x).suffix == ".jpg", file_path_list))
    vc = VideoCroping()
    results = []
    for file_path in file_path_list:
        results.append(file_path)
        print("file_path_list len: ", len(file_path_list))
        file_path_list.remove(file_path)
        for file_compare in file_path_list:
            if file_path != file_compare:
                score, _ = vc.image_similarity(file_path, file_compare)
                if score > score_threshold:
                    print("find remove file:", file_compare)
                    file_path_list.remove(file_compare)
    print(file_path_list)
    
    for pure in results:
        copyfile(pure, f"{out}/{os.path.basename(pure)}")

        
    
def main(argv):
    print(argv)
    if args.type == "d":
        download_video(args)
    if args.type == "c":
        crop_video(args)
    if args.type == "k":
        args.plugins = "t|c"
        download_video(args)
    if args.type == "s":
        shot_detect_video(args)
    if args.type == "i":
        simularity_image_remove(args)
    if args.type == "f":
        result = vision_processing("public_videos_samples", "test")
        with open("./downloads/result22.json", 'w') as outfile:
            json.dump(result, outfile)


if __name__ == "__main__":
    main(sys.argv)

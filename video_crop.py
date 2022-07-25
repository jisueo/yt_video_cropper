import cv2
from tqdm import tqdm
from skimage.metrics import structural_similarity
import cv2
import numpy as np


class VideoCroping:

    __show_progress = False
    __show_frames = False

    def __init__(self, show_progress=False, show_frames=False) -> None:
        """init cropping video module
        Args:
            show_progress: True or False, default False, if you want to se progress bar on screen, set True
            show_frame: True or False, default False, if you want to see video frame on screen, set True
        """
        self.__show_progress = show_progress
        self.__show_frames = show_frames

    def image_similarity(self, origin_image_path, compare_image_path):
        """init cropping video module
        Ref:
            https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
        Args:
            origin_image_path: original image
            compare_image_path: compare image
        """
        first = cv2.imread(origin_image_path)
        second = cv2.imread(compare_image_path)

        # Convert images to grayscale
        first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
        second_gray = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between two images
        score, diff = structural_similarity(first_gray, second_gray, full=True)
        return score * 100, (diff * 255).astype("uint8")

    def capture (self, video_file_path: str, out: str = None, times: list[int] = None):
        try:
            file_name = video_file_path
            cap = cv2.VideoCapture(file_name)
            fps = cap.get(cv2.CAP_PROP_FPS)

            video_cropping_progress = None
            if self.__show_progress:
                video_cropping_progress = tqdm(total=len(times), desc="Capture Video Frames Count:")

            counter = 1  # set counter
            for index, time in enumerate(times):
                capture_frame = fps * time
                cap.set(cv2.CAP_PROP_POS_FRAMES, capture_frame)
                success, frame = cap.read()
                outfile = f"{out}/{index}.jpg"
                if success:
                    cv2.imwrite(outfile,frame)
                if self.__show_frames:
                    cv2.imshow("Frame", frame)  # display frame
                if video_cropping_progress is not None:
                    video_cropping_progress.update(1)
                    
            cv2.destroyAllWindows()
        except Exception as e:
            raise e

    def crop(
        self,
        video_file_path: str,
        out: str = None,
        out_file_name: str = None,
        start_time: int = None,
        end_time: str = None,
        width=None,
        height=None,
        crop=False,
    ):
        """Get channel info from video id
        Args:
            video_file_path(str): video file path
            start_time(int): video capture start second
            end_time(int): video capture end second
            width(int): output Width
            height(int): output Height
            crop: out put crop if w/h rate dose not fit into origin size
        Returns:
            None
        Exception:
            raise NotFoundFile
            raise OpenCV Error raise
        """
        try:
            if out is None and out_file_name is None:
                out = "output.mp4"
            else:
                out = f"{out}/{out_file_name}"
            print(out)
            file_name = video_file_path
            cap = cv2.VideoCapture(file_name)
            fps = cap.get(cv2.CAP_PROP_FPS)

            origin_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            origin_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

            if width is None or height is None:
                height = origin_height
                width = origin_width
            start_frame = fps * start_time
            end_frame = fps * (end_time - start_time)

            video_cropping_progress = None
            if self.__show_progress:
                video_cropping_progress = tqdm(total=end_frame, desc="Cropping Video :")

            # set start frame, video skip to start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # make output video writer
            fourcc = cv2.VideoWriter_fourcc(*"FMP4")
            out_video = cv2.VideoWriter(out, fourcc, fps, (width, height))

            counter = 1  # set counter

            while cap.isOpened():  # while the cap is open
                __, frame = cap.read()  # read frame
                if frame is None:  # if frame is None
                    break
                if crop == False:
                    frame = cv2.resize(frame, (width, height))  # resize the frame
                else:
                    left = (origin_width - width) / 2
                    right = (origin_width - width) / 2 + width
                    top = (origin_height - height) / 2
                    bottom = (origin_height - height) / 2 + height
                    frame[top:bottom, left:right]
                if counter <= end_frame:  # check for range of output
                    out_video.write(frame)  # output
                else:
                    break
                if self.__show_frames:
                    cv2.imshow("Frame", frame)  # display frame
                counter += 1
                if video_cropping_progress is not None:
                    video_cropping_progress.update(1)
            out_video.release()
            cv2.destroyAllWindows()
        except Exception as e:
            raise e

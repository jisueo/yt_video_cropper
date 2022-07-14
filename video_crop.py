import cv2
from tqdm import tqdm


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
                    break;
                if self.__show_frames:
                    cv2.imshow("Frame", frame)  # display frame
                counter += 1
                if video_cropping_progress is not None:
                    video_cropping_progress.update(1)

            out_video.release()
            cv2.destroyAllWindows()
        except Exception as e:
            raise e

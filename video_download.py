from xmlrpc.client import boolean
from pytube import YouTube, Stream
import ssl
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context


class VideoDownloader:

    __show_progress = False
    __progress_current_rate = 0
    __video_download_pbar = None

    def __init__(self, show_progress=False) -> None:
        """init download video module
        Args:
            show_progress: True or False, default False, if you want to se progress bar on screen, set True
        """
        self.__show_progress = show_progress
        if self.__show_progress:
            self.__video_download_pbar = tqdm(total=100, desc="Download Video :")

    def __download_procegress_callback(
        self, stream: Stream = None, chunk=None, remaining=None
    ):

        file_size = stream.filesize
        current_rate = (100 * (file_size - remaining)) / file_size
        update_rate = current_rate - self.__progress_current_rate
        self.__video_download_pbar.update(update_rate)
        self.__progress_current_rate = current_rate

    def __complete_callback(self, stream: Stream = None, msg: str = None):
        self.__video_download_pbar.update(100)

    def download(self, video_id: str, download_foler, file_name=None) -> str:
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(video_url)
            youtube_video = YouTube(
                video_url,
                on_complete_callback=lambda stream, msg: self.__complete_callback(
                    stream, msg
                )
                if self.__show_progress
                else None,
                on_progress_callback=lambda stream, chunk, remaining: self.__download_procegress_callback(
                    stream, chunk, remaining
                )
                if self.__show_progress
                else None,
            )
            stream = youtube_video.streams.get_highest_resolution()
            if file_name is None:
                file_name = video_id

            stream.download(download_foler, f"{file_name}.mp4")
            return f"{download_foler}/{file_name}.mp4"
        except Exception as e:
            raise e

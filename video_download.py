from xmlrpc.client import boolean
from pytube import YouTube
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def download(video_id: str, download_foler, file_name=None) -> boolean:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    if file_name is None:
        file_name = video_id
    stream.download(download_foler, f"{file_name}.mp4")
    return f"{download_foler}/{file_name}.mp4"

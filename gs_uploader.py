from google.cloud import storage
import os
from configs.config import Configs

storage_client = storage.Client.from_service_account_json(
    Configs.instance().get_attr("GCP_CREDENTIAL")
)
GCS_BUCKET = Configs.instance().get_attr("GCS_BUCKET")

"""Module google storage Uploader, 

    Video file이나 Image file을 Google Storage file에 업로드 합니다.
    Video, Vision API를 사용하기 위해서는 보통 Image나 Video는 Google Storage에 저장되어 있어야 합니다.

    Typical usage example:
        import gs_uploader
        credential = gs_uploader.upload_blob_storage("file/path/video.mp4", "video.mp4", "/prefix/folder/")
        credential = gs_uploader.upload_file("file/path/video.mp4")
"""

def upload_blob_storage(file_path, title, prefix = None):
    try:
        print("start upload google storage")
        if not os.path.exists(file_path):
            print("Video File Not Exist")
            return False
        
        bucket = storage_client.get_bucket(GCS_BUCKET)
        if prefix is not None:
            title = f"{prefix}{title}"
        is_exist = storage.Blob(bucket=bucket, name=title).exists(storage_client)
        if is_exist:
            print(f"Already {title} file is exist in Google Storage!!!")
            return False
        blob = bucket.blob(title)
        blob.upload_from_filename(file_path, timeout=360)
        return True
    except Exception as e:
        print(e)
        return False

def upload_file(file_path: str) -> bool:
    try:
        upload_blob_storage(file_path, os.path.basename(file_path))
        return True
    except Exception as e:
        print("error", e)
        return False

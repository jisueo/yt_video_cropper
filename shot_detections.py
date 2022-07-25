from google.cloud import videointelligence
from configs.config import Configs
import json
GCS_BUCKET = Configs.instance().get_attr("GCS_BUCKET")
video_client = videointelligence.VideoIntelligenceServiceClient.from_service_account_json(
    Configs.instance().get_attr("GCP_CREDENTIAL")
)

def analyze_shots_offset(video_id):
    """Detects camera shot changes."""
    features = [videointelligence.Feature.SHOT_CHANGE_DETECTION]
    operation = video_client.annotate_video(
        request={"features": features, "input_uri": f"gs://{GCS_BUCKET}/{video_id}.mp4"}
    )
    print("\nProcessing video for shot change annotations:")

    result = operation.result(timeout=120)
    print("\nFinished processing.")

    shots_infos = []
    for i, shot in enumerate(result.annotation_results[0].shot_annotations):
        start_time = (
            shot.start_time_offset.seconds + shot.start_time_offset.microseconds / 1e6
        )
        end_time = (
            shot.end_time_offset.seconds + shot.end_time_offset.microseconds / 1e6
        )
        shots_infos.append({
            "start": start_time,
            "end": end_time,
            "time": int(start_time + (end_time - start_time) / 2)
        })
    return shots_infos
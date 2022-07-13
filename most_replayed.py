import requests
import re
import json
from urllib import parse

VIDEO_URL = "https://www.youtube.com/watch?v="
YOUTUBE_INIT_VARIABLE_NAME = "ytInitialData"


class MostReplayedHeatMap:

    __video_id = None

    def __init__(self, video_id):
        self.__video_id = video_id

    def cal_totals(self, data):
        markers = data.get("heatMarkers", {})
        total = 0
        for marker in markers:
            total += marker["heatMarkerRenderer"]["heatMarkerIntensityScoreNormalized"]
        return total

    def extract_heatmap_data(self):
        try:
            video_url = VIDEO_URL + parse.quote(self.__video_id)
            response = requests.get(video_url)
            html = None
            if response.status_code == 200:
                html = response.text
            if html is not None:
                reCompYtInfo = re.compile(
                    YOUTUBE_INIT_VARIABLE_NAME + " = ({.*?});", re.DOTALL
                )
                searchCompYtInfo = reCompYtInfo.search(html)
                if searchCompYtInfo is None:
                    return False, "can not found ytinitialdata variable"

                strYTInit = searchCompYtInfo.group(1)
                ytData = json.loads(strYTInit)

                markersMaps = (
                    ytData.get("playerOverlays", {})
                    .get("playerOverlayRenderer", {})
                    .get("decoratedPlayerBarRenderer", {})
                    .get("decoratedPlayerBarRenderer", {})
                    .get("playerBar")
                    .get("multiMarkersPlayerBarRenderer")
                    .get("markersMap")
                )
                if len(markersMaps) > 0:
                    for marker in markersMaps:
                        if (
                            marker.get("value") is not None
                            and marker.get("value", {}).get("heatmap") is not None
                        ):
                            return (
                                marker.get("value", {})
                                .get("heatmap", {})
                                .get("heatmapRenderer")
                            )

                    return None
        except Exception as e:
            print(e)
            raise e

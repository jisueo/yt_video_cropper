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

    def normalized_range_data(self, data):
        # 기본적으로 구간 당 10초가 넘어가야 구간으로 인정 한다.
        # 각각의 머지해버린다.
        # 무조건 100개가 있어야 하기 때문에, 몇개씩 머지 해야 되는지 확인 해 본다.
        heat_markers = data["heatMarkers"]
        heat_markers = heat_markers[1:99]
        heat_markers_len = len(heat_markers)

        time_unit = heat_markers[0]["heatMarkerRenderer"]["markerDurationMillis"]

        # count_unit만큼씩 머지 한다.
        count_unit = int(10000 / time_unit) + int(1 if 10000 % time_unit > 0 else 0)

        new_heatmap = []
        for index, marker in enumerate(heat_markers):
            current_duration = marker["heatMarkerRenderer"]["markerDurationMillis"]
            current_norm = marker["heatMarkerRenderer"][
                "heatMarkerIntensityScoreNormalized"
            ]
            current_start = marker["heatMarkerRenderer"]["timeRangeStartMillis"]
            for sindex in range(1, count_unit):
                if index + sindex < heat_markers_len:
                    current_duration += heat_markers[index + sindex][
                        "heatMarkerRenderer"
                    ]["markerDurationMillis"]
                    current_norm = heat_markers[index + sindex]["heatMarkerRenderer"][
                        "heatMarkerIntensityScoreNormalized"
                    ]

            new_heatmap.append(
                {
                    "markerDurationMillis": current_duration,
                    "heatMarkerIntensityScoreNormalized": current_norm,
                    "timeRangeStartMillis": current_start,
                }
            )
        return new_heatmap

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

                            return self.normalized_range_data(
                                (
                                    marker.get("value", {})
                                    .get("heatmap", {})
                                    .get("heatmapRenderer")
                                )
                            )
        except Exception as e:
            raise e

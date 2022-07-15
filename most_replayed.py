import requests
import re
import json
from urllib import parse

VIDEO_URL = "https://www.youtube.com/watch?hl=en&v="
YOUTUBE_INIT_VARIABLE_NAME = "ytInitialData"
# [{"timedMarkerDecorationRenderer":{"visibleTimeRangeStartMillis":19651940,"visibleTimeRangeEndMillis":20253530,"decorationTimeMillis":19852470,"label":{"runs":[{"text":"가장 많이 다시 본 장면"}]


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

    def extract_most_replayed_term(self):
        try:
            data = self.extract_heatmap_data()
            heat_markers_decos = data["heatMarkersDecorations"]
            for deco in heat_markers_decos:
                timeMarker = deco.get("timedMarkerDecorationRenderer", {})
                if timeMarker is not None:
                    if timeMarker.get("label") is not None:
                        texts = timeMarker.get("label", {}).get("runs")
                        for text in texts:
                            if text.get("text") == "Most replayed":
                                return (
                                    timeMarker["visibleTimeRangeStartMillis"],
                                    timeMarker["visibleTimeRangeEndMillis"],
                                    timeMarker["decorationTimeMillis"],
                                )
            return None
        except Exception as e:
            return None

    def normalized_range_data(self, data):
        # 기본적으로 3개 구간을 사용하는 것으로 파악 된다.
        heat_markers = data["heatMarkers"]
        heat_markers_len = len(heat_markers)

        time_unit = heat_markers[0]["heatMarkerRenderer"]["markerDurationMillis"]

        # count_unit만큼씩 머지 한다.
        count_unit = 3

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

    def extract_visual_normalized_heatmap_data(self):
        try:
            return self.normalized_range_data(self.extract_heatmap_data())
        except Exception as e:
            raise e

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
            raise e

from html import entities
from unittest import result
from google.cloud import vision_v1
from google.cloud import translate_v2
from google.cloud import storage

from configs.config import Configs

storage_client = storage.Client.from_service_account_json(
    Configs.instance().get_attr("GCP_CREDENTIAL")
)
client = vision_v1.ImageAnnotatorClient.from_service_account_file(
    Configs.instance().get_attr("GCP_CREDENTIAL")
)
trClient = translate_v2.Client.from_service_account_json(
    Configs.instance().get_attr("GCP_CREDENTIAL")
)

def vision_processing(image_bucket: str, prefix: str):
    try:
        print(image_bucket, prefix)
        blobs = storage_client.list_blobs(image_bucket)
        image_info_list = []
        blobs = filter( lambda x:  "GrAYU37dJ8s" in x.name and ".jpg" in x.name, list(blobs))
        for blob in blobs:
            print(f"gs://{image_bucket}/{blob.name}")
            source = {"image_uri": f"gs://{image_bucket}/{blob.name}"}
            image = {"source": source}
            features = [
                {"type_": vision_v1.Feature.Type.LABEL_DETECTION},
                {"type_": vision_v1.Feature.Type.IMAGE_PROPERTIES},
                {"type_": vision_v1.Feature.Type.WEB_DETECTION},
            ]

            requests = [{"image": image, "features": features}]
            r = client.batch_annotate_images(requests=requests)

            results = {
                "labels": r.responses[0].label_annotations,
                "props": r.responses[0].image_properties_annotation,
                "web_labels": r.responses[0].web_detection,
            }

            props = []
            image_labels = []
            web_detection_results = {
                "best_labels": [],
                "pages_with_matching_images": [],
                "entities": [],
            }

            if results["web_labels"].best_guess_labels:
                for wlabel in results["web_labels"].best_guess_labels:
                    web_detection_results["best_labels"].append(wlabel.label)

            if results["web_labels"].pages_with_matching_images:
                for page in results["web_labels"].pages_with_matching_images:
                    web_detection_results["pages_with_matching_images"].append(page.url)

            if results["web_labels"].web_entities:
                for entity in results["web_labels"].web_entities:
                    web_detection_results["entities"].append(
                        {"description": entity.description, "score": entity.score}
                    )

            for label in results["labels"]:
                image_labels.append(
                    {
                        "description": label.description,
                        "score": label.score,
                        "topicality": label.topicality,
                    }
                )

            for color in results["props"].dominant_colors.colors:
                props.append(
                    {
                        "pixel_fraction": float(color.pixel_fraction),
                        "red": float(color.color.red),
                        "green": float(color.color.green),
                        "blue": float(color.color.blue),
                    }
                )

            web_detection_labels_entities = list(
                map(lambda x: x["description"], web_detection_results["entities"])
            )
            image_labels_descs = list(map(lambda x: x["description"], image_labels))

            web_detaction_labels_text = ",".join(web_detection_labels_entities)
            web_detaction_labels_text_ko = trClient.translate(
                web_detaction_labels_text, "ko"
            )

            image_labels_text = ",9".join(image_labels_descs)
            image_labels_text_ko = trClient.translate(image_labels_text, "ko")
            image_info_list += web_detaction_labels_text_ko[
                    "translatedText"
                ].split(",") 
            '''
            image_info_list.append( {
                "file": blob.name,
                "props": props,
                "image_labels": image_labels,
                "image_labels": image_labels_text_ko["translatedText"].split(","),
                "web_labels": web_detection_results,
                "web_detection_labels_text": web_detaction_labels_text_ko["translatedText"],
                "web_detection_labels_text_array": web_detaction_labels_text_ko[
                    "translatedText"
                ].split(","),
                "web_detection_labels_text_origin": web_detaction_labels_text,
            })
            '''
        return list(set(image_info_list))
    except Exception as e:
        print(e)

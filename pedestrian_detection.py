import os
from pathlib import Path

from dotenv import load_dotenv
import cv2
import torch
from ultralytics import YOLO

import rawpy

load_dotenv()


def preprocess_image(dng_path):
    with rawpy.imread(dng_path) as raw:
        rgb_image = raw.postprocess(
            no_auto_bright=False,
            output_bps=8,
            use_camera_wb=True,
            gamma=(2, 4),
            exp_shift=2,
        )
    # lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
    # l, a, b = cv2.split(lab)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # cl = clahe.apply(l)
    # lab = cv2.merge((cl, a, b))
    # enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    return rgb_image


def resize_image(image, target_width=1024):
    h, w, _ = image.shape
    scale_factor = target_width / w
    new_dimensions = (target_width, int(h * scale_factor))
    resized_image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)
    return resized_image, scale_factor


def detect_pedestrians(image):
    model = YOLO("yolov8m.pt")
    # Set the device to MPS if available (for Apple silicon)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model.to(device)
    results = model(image, conf=0.3)  # 0.3=confidence threshold
    return results


def upscale_boxes(results, scale_factor):
    scaled_boxes = []
    for result in results:
        for box in result.boxes:
            cls = int(box.cls.cpu().item())
            if cls == 0:
                x1, y1, x2, y2 = box.xyxy.cpu().numpy()[0]
                conf = box.conf.cpu().item()
                scaled_box = [int(coord / scale_factor) for coord in (x1, y1, x2, y2)]
                scaled_boxes.append((*scaled_box, conf, cls))
    return scaled_boxes


def draw_boxes(image, boxes):
    for x1, y1, x2, y2, conf, cls in boxes:
        label = f"Person: {conf:.2f}"
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image


def main(image_dir_path: Path, destination: Path):
    str_path = image_dir_path.as_posix()
    if not destination.exists():
        os.makedirs(destination)
    enhanced_image = preprocess_image(str_path)
    resized_image, scale_factor = resize_image(enhanced_image)
    results = detect_pedestrians(resized_image)
    boxes = upscale_boxes(results, scale_factor)
    result_image = draw_boxes(enhanced_image, boxes)
    image_name = image_dir_path.name.split(".")[0]
    result_image_path = destination.joinpath(image_name + "-cv.jpg").as_posix()
    cv2.imwrite(
        result_image_path,
        result_image[..., ::-1],
    )


def get_image_dir_from_env():
    try:
        return Path(os.environ.get("IMAGE_PATH")).resolve()
    except Exception:
        raise

    # if __name__ == "__main__":


image_dir = get_image_dir_from_env()

print(image_dir)

for im in image_dir.rglob("*.dng"):
    main(image_dir_path=im, destination=Path("./cv_results"))

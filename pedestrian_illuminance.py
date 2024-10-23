import os
from pathlib import Path

import numpy as np
import pandas as pd
import rawpy

from pedestrian_detection import (
    preprocess_image,
    resize_image,
    detect_pedestrians,
    upscale_boxes,
    draw_boxes,
    get_image_dir_from_env,
)

import cv2


def read_raw_image(dng_path: str) -> np.array:
    with rawpy.imread(dng_path) as raw:
        rgb_image = raw.postprocess(
            no_auto_bright=False,
            output_bps=8,
            use_camera_wb=True,
        )
    return rgb_image


def crop_image(image: np.array, x1: int, y1: int, x2: int, y2: int) -> np.array:
    """Crop an image to a specified region."""
    return image[y1:y2, x1:x2]


def get_yuv_luminance(image: np.array) -> float:
    """Calculate the luminance of an image from YUV color space."""
    yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
    return np.mean(yuv[:, :, 0]).astype(np.float32)


def write_luminance_to_image(
    image: np.ndarray, luminance: float, rms: float, x1: int, y1: int
) -> np.array:
    """Write the luminance value to an image."""
    cv2.putText(
        image,
        f"luminance: {luminance:.2f}",
        (x1, y1 - 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2,
    )

    cv2.putText(
        image,
        f"RMS: {rms:.2f}",
        (x1, y1 - 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2,
    )
    return image


def main(image_dir_path: Path, destination: Path):
    str_path = image_dir_path.as_posix()
    if not destination.exists():
        os.makedirs(destination)
    original_image = read_raw_image(str_path)
    enhanced_image = preprocess_image(str_path)
    resized_image, scale_factor = resize_image(enhanced_image)
    results = detect_pedestrians(resized_image)
    boxes = upscale_boxes(results, scale_factor)

    luminances = []
    rms_data = []
    csv_data = []
    image_name = image_dir_path.name.split(".")[0]

    for idx, box in enumerate(boxes):
        cropped = crop_image(original_image, *box[:4])
        luminance = get_yuv_luminance(cropped)
        rms = np.sqrt(np.mean(cropped[:, :, 0] ** 2))
        luminances.append(luminance)
        csv_data.append(
            {
                "image": image_name,
                "person_index": idx,
                "luminance": luminance,
                "rms": rms,
                "confidence": box[4],
            }
        )
        rms_data.append(rms)

    df = pd.DataFrame(csv_data)

    result_image = np.ndarray.copy(enhanced_image)
    for luminance, rms, box in zip(luminances, rms_data, boxes):
        result_image = write_luminance_to_image(result_image, luminance, rms, *box[:2])
    result_image = draw_boxes(result_image, boxes)

    result_image_path = destination.joinpath(image_name + f"-luminance.jpg").as_posix()
    cv2.imwrite(
        result_image_path,
        result_image[..., ::-1],
    )
    return df


if __name__ == "__main__":
    image_dir = get_image_dir_from_env()
    all_data = []

    for im in image_dir.rglob("*.dng"):
        df = main(image_dir_path=im, destination=Path("./illuminance_results"))
        all_data.append(df)

    # Concatenate all data frames and save to a single CSV file
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv("./illuminance_results/all_images_luminance.csv", index=False)

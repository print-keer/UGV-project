from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ai.inference.backends import RuntimeFrame

if TYPE_CHECKING:
    from collections.abc import Iterator


def load_image_frame(image_path: str | Path) -> RuntimeFrame:
    image_path = Path(image_path)
    image = _read_image(image_path)
    return RuntimeFrame(
        frame_id=image_path.stem,
        image=image,
        description=f"Loaded from {image_path}",
    )


def stream_camera_frames(
    *,
    camera_index: int = 0,
    max_frames: int = 10,
) -> "Iterator[RuntimeFrame]":
    cv2 = _import_cv2()
    capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera index {camera_index}.")
    try:
        for frame_number in range(max_frames):
            success, image = capture.read()
            if not success:
                break
            yield RuntimeFrame(
                frame_id=f"camera-{camera_index}-frame-{frame_number:04d}",
                image=image,
                description=f"Live camera frame {frame_number}",
            )
    finally:
        capture.release()


def _read_image(image_path: Path):
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found at {image_path}.")
    cv2 = _import_cv2()
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"OpenCV failed to read image at {image_path}.")
    return image


def _import_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is not installed. Install it with `pip install opencv-python` to use camera or image inference."
        ) from exc
    return cv2

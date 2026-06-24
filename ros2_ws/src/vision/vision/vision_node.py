from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_root_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(repo_root))


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run vision_node. Use the pure Python inference modules or install ROS2 Humble."
        ) from exc

    _add_repo_root_to_path()

    from ai.inference.backends import InferenceDependencyError, YoloVisionBackend
    from ai.inference.camera import load_image_frame
    from ai.inference.pipeline import run_mock_inference, run_runtime_inference
    from ai.threat_classifier.contracts import serialize_detection_result

    class VisionNode(Node):
        def __init__(self) -> None:
            super().__init__("vision_node")
            self.detection_publisher = self.create_publisher(String, "vision/detections", 10)
            repo_root = Path(__file__).resolve().parents[4]
            sample_image = repo_root / "ai" / "dataset" / "sample_frame.jpg"
            model_path = repo_root / "ai" / "models" / "best.pt"
            if sample_image.exists() and YoloVisionBackend(model_path).is_ready():
                try:
                    results = run_runtime_inference(
                        [load_image_frame(sample_image)],
                        model_path=str(model_path),
                    )
                    self.get_logger().info("Vision node is using runtime YOLO inference.")
                except (RuntimeError, FileNotFoundError, InferenceDependencyError) as exc:
                    self.get_logger().warning(f"Falling back to mock inference: {exc}")
                    results = run_mock_inference()
            else:
                self.get_logger().info("Vision node scaffold is using mock inference samples.")
                results = run_mock_inference()
            for result in results:
                message = String()
                message.data = serialize_detection_result(result)
                self.detection_publisher.publish(message)
                self.get_logger().info(
                    f"{result.frame_id}: detections={len(result.detections)} backend={result.backend_name}"
                )

    rclpy.init()
    node = VisionNode()
    try:
        rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

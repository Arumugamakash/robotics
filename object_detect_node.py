import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
import json
from ultralytics import YOLO


class YoloNode(Node):

    def __init__(self):
        super().__init__('yolo_node')

        # Load YOLO model
        self.model = YOLO("yolov8n.pt")

        self.bridge = CvBridge()

        # Subscribers
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publishers
        self.image_pub = self.create_publisher(Image, '/yolo/detected_image', 10)
        self.data_pub = self.create_publisher(String, '/yolo/detections', 10)

        self.get_logger().info("YOLO Node Started")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Run YOLO
        results = self.model(frame)

        boxes = results[0].boxes

        detection_list = []
        counts = {}

        for box in boxes:
            cls_id = int(box.cls[0])
            name = self.model.names[cls_id]
            conf = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0]

            # Center
            cx = float((x1 + x2) / 2)
            cy = float((y1 + y2) / 2)

            # Size
            width = float(x2 - x1)
            height = float(y2 - y1)

            # Count
            counts[name] = counts.get(name, 0) + 1

            detection_list.append({
                "type": name,
                "confidence": conf,
                "center": [cx, cy],
                "size": [width, height]
            })

        # Log counts
        self.get_logger().info(f"Counts: {counts}")

        # Publish detection data
        msg_out = String()
        msg_out.data = json.dumps({
            "counts": counts,
            "objects": detection_list
        })
        self.data_pub.publish(msg_out)

        # Annotated image
        annotated = results[0].plot()

        img_msg = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
        self.image_pub.publish(img_msg)


def main(args=None):
    rclpy.init(args=args)
    node = YoloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
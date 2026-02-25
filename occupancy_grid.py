# #!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node

# import numpy as np

# from sensor_msgs.msg import PointCloud2
# from nav_msgs.msg import OccupancyGrid
# from std_msgs.msg import Header

# from sensor_msgs_py import point_cloud2
# from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

# class PointCloudToOccupancy(Node):

#     def __init__(self):
#         super().__init__('pointcloud_to_occupancy')


#         # ✅ CORRECT: Declare parameter on Node
#         self.declare_parameter('use_sim_time', False)
        
#         # ✅ Get parameter from Node (not Context)
#         use_sim_time = self.get_parameter('use_sim_time').value
        
#         if use_sim_time:
#             self.get_logger().info('Using simulation time')
#         else:
#             self.get_logger().info('Using wall clock time')

#         # -------- Parameters --------
#         self.declare_parameter('resolution', 0.05)   # meters/cell
#         self.declare_parameter('width', 20.0)         # meters
#         self.declare_parameter('height', 20.0)        # meters
#         self.declare_parameter('min_z', 0.05)         # floor filter
#         self.declare_parameter('max_z', 2.0)          # ignore ceiling
#         self.declare_parameter('frame_id', 'map')

#         self.resolution = self.get_parameter('resolution').value
#         self.width = self.get_parameter('width').value
#         self.height = self.get_parameter('height').value
#         self.min_z = self.get_parameter('min_z').value
#         self.max_z = self.get_parameter('max_z').value
#         self.frame_id = self.get_parameter('frame_id').value

#         self.grid_width = int(self.width / self.resolution)
#         self.grid_height = int(self.height / self.resolution)

#         # -------- ROS Interfaces --------
#         self.sub = self.create_subscription(
#             PointCloud2,
#             '/camera/points',
#             self.cloud_callback,
#             10
#         )

#         qos = QoSProfile(
#             depth=1,
#             durability=DurabilityPolicy.TRANSIENT_LOCAL,
#             reliability=ReliabilityPolicy.RELIABLE
#         )

#         self.pub = self.create_publisher(
#             OccupancyGrid,
#             '/overhead_obstacles',
#             qos
#         )

#         self.get_logger().info('PointCloud → OccupancyGrid node started')

#     def cloud_callback(self, msg: PointCloud2):
#         # Initialize grid (unknown = -1)
#         grid = -1 * np.ones((self.grid_height, self.grid_width), dtype=np.int8)

#         # Origin (bottom-left of grid in world frame)
#         origin_x = -self.width / 2.0
#         origin_y = -self.height / 2.0

#         # Read points
#         for point in point_cloud2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True):
#             x, y, z = point

#             # Height filtering
#             if z < self.min_z or z > self.max_z:
#                 continue

#             # Convert to grid index
#             gx = int((x - origin_x) / self.resolution)
#             gy = int((y - origin_y) / self.resolution)

#             if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
#                 grid[gy, gx] = 100  # occupied

#         # Unknown → free (optional)
#         # grid[grid == -1] = 0

#         # Build OccupancyGrid message
#         og = OccupancyGrid()
#         og.header = Header()
#         og.header.stamp = self.get_clock().now().to_msg()
#         og.header.frame_id = self.frame_id

#         og.info.resolution = self.resolution
#         og.info.width = self.grid_width
#         og.info.height = self.grid_height
#         og.info.origin.position.x = origin_x
#         og.info.origin.position.y = origin_y
#         og.info.origin.position.z = 0.0
#         og.info.origin.orientation.w = 1.0

#         og.data = grid.flatten().tolist()

#         self.pub.publish(og)


# def main():
#     rclpy.init()
#     node = PointCloudToOccupancy()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main() 


#!/usr/bin/env python3
"""
PointCloud to OccupancyGrid Converter
Converts 3D point clouds to 2D occupancy grids for navigation costmaps
"""

import rclpy
from rclpy.node import Node
import numpy as np
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import Header
from sensor_msgs_py import point_cloud2
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy


class PointCloudToOccupancy(Node):
    def __init__(self):
        super().__init__('pointcloud_to_occupancy')
        
        # -------- Parameters --------
        # Note: use_sim_time is automatically declared by ROS 2
        # Don't declare it again or you'll get ParameterAlreadyDeclaredException
        
        self.declare_parameter('resolution', 0.05)   # meters/cell
        self.declare_parameter('width', 20.0)         # meters
        self.declare_parameter('height', 20.0)        # meters
        self.declare_parameter('min_z', 0.05)         # floor filter
        self.declare_parameter('max_z', 2.0)          # ignore ceiling
        # self.declare_parameter('frame_id', 'map')
        self.declare_parameter('frame_id', 'camera_link') 
        
        # -------- Get Parameters --------
        self.resolution = self.get_parameter('resolution').value
        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value
        self.min_z = self.get_parameter('min_z').value
        self.max_z = self.get_parameter('max_z').value
        self.frame_id = self.get_parameter('frame_id').value
        
        # You CAN read use_sim_time if you want (it's auto-declared)
        # But you don't need to - ROS 2 handles it
        
        self.grid_width = int(self.width / self.resolution)
        self.grid_height = int(self.height / self.resolution)
        
        self.get_logger().info(
            f'PointCloud → OccupancyGrid Converter Started\n'
            f'  Input: /camera/points\n'
            f'  Output: /overhead_obstacles\n'
            f'  Grid: {self.grid_width}x{self.grid_height} @ {self.resolution}m/cell'
        )
        
        # -------- ROS Interfaces --------
        self.sub = self.create_subscription(
            PointCloud2,
            '/camera/points',
            self.cloud_callback,
            10
        )
        
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )
        
        self.pub = self.create_publisher(
            OccupancyGrid,
            '/overhead_obstacles',
            qos
        )
    
    def cloud_callback(self, msg: PointCloud2):
        """Convert point cloud to occupancy grid"""
        
        # Initialize grid (unknown = -1)
        grid = -1 * np.ones((self.grid_height, self.grid_width), dtype=np.int8)
        
        # Origin (bottom-left of grid in world frame)
        origin_x = -self.width / 2.0
        origin_y = -self.height / 2.0
        
        # Read points
        for point in point_cloud2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True):
            x, y, z = point
            
            # Height filtering
            if z < self.min_z or z > self.max_z:
                continue
            
            # Convert to grid index
            gx = int((x - origin_x) / self.resolution)
            gy = int((y - origin_y) / self.resolution)
            
            if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
                grid[gy, gx] = 100  # occupied
        
        # Build OccupancyGrid message
        og = OccupancyGrid()
        og.header = Header()
        og.header.stamp = self.get_clock().now().to_msg()
        og.header.frame_id = self.frame_id
        og.info.resolution = self.resolution
        og.info.width = self.grid_width
        og.info.height = self.grid_height
        og.info.origin.position.x = origin_x
        og.info.origin.position.y = origin_y
        og.info.origin.position.z = 0.0
        og.info.origin.orientation.w = 1.0
        og.data = grid.flatten().tolist()
        
        self.pub.publish(og)


def main():
    rclpy.init()
    node = PointCloudToOccupancy()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
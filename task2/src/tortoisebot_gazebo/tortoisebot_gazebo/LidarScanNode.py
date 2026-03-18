import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
# import math
import numpy as np
from std_msgs.msg import Float32  
import time


class LidarScanNode(Node):

    def __init__(self):
        super().__init__('lidar_scan_node')
        self.sub=self.create_subscription(
            LaserScan,'/scan',self.filter_scan,10
        )
        self.get_logger().info("LIDAR Filter Node started!")
        self.pub_min=self.create_publisher(Float32,'closest_object',7)
        # self.pub_median=self.create_publisher(Float32,'median_object',10)

    def filter_scan(self,msg:LaserScan):
       
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        range_value = msg.ranges
            # Define ±15 degrees region in radians
            # pi=3.141592653589793
            # degree=15
            # radians=degree*(pi/180)
            # print(radians)
        find_radian=np.radians(15)
        min_angle=-find_radian
        max_angle=find_radian
        filtered_ranges=[]
        
        for i in range(len(range_value)):
            distance=range_value[i]
            angle=angle_min + i * angle_increment
            
            if(np.isfinite(distance) and min_angle<= angle<= max_angle):
                filtered_ranges.append(round(distance,2))
            
        self.find_median(filtered_ranges)
        self.find_minimum(filtered_ranges)      

    def find_median(self,filtered_ranges):
        # print('filter1 ',filtered_ranges)
        n=len(filtered_ranges)
        for i in range(0,n-1):
            if i!=n :
                before=filtered_ranges[i-1]
                current=filtered_ranges[i]
                after=filtered_ranges[i+1]
                group=[before,current,after]
                sorted(group)
                median=group[len(group)//2] 
                filtered_ranges[i]=median
        # time.sleep(1)
        print('Median Array \n',filtered_ranges)
                
    def find_minimum(self,filtered_ranges):
        if filtered_ranges:
            self.closest=min(filtered_ranges)
            print('min ',self.closest)
            self.get_logger().info("Object is detected")
            close = Float32()
            close.data = self.closest
            self.pub_min.publish(close)
        else:
            self.get_logger().info("No valid object detected ahead")

    # def find_median2(self,filtered_ranges):
    #         data=sorted(filtered_ranges)
    #         print(data)
    #         n=len(data)
    #         print('length',n)
    #         if n%2==1 :
    #             median_data=data[n//2]
    #         else :
    #             median_data=(data[n//2-1] +data[n//2])//2
    #             print('median ',median_data)
      
            

def main(args=None):
    rclpy.init(args=args)
    lidar = LidarScanNode()
    rclpy.spin(lidar)
    lidar.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
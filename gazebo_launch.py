import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command,TextSubstitution
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.actions import SetEnvironmentVariable
from pathlib import Path

def generate_launch_description():
    
    pkg_description = get_package_share_directory('dynamic_obstacle_avoidance')
    urdf_file = os.path.join (pkg_description,'urdf','tortoisebot.urdf')
        
    robot_desc = TextSubstitution(text=Path(urdf_file).read_text())

    robot_description = {"robot_description": robot_desc}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="screen"
    )
    
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value='/home/arz-1017/Desktop/Evaluation4/dynamic_avoidance/src/dynamic_obstacle_avoidance/models'

    )

    world_file = os.path.join(
        get_package_share_directory('dynamic_obstacle_avoidance'),
        'worlds',
        'warehouse.world'
    )
    
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    

    start_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])
        ), 
        launch_arguments={
            'gz_args': world_file,
            'on_exit_shutdown': 'true'
        }.items(),
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'tortoisebot',
            '-x', '2',
            '-y', '12',
            '-z', '1'
        ],
        output='screen'
    )

    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',
            'camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            'camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            'camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            'camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen"
    )
    return LaunchDescription([
        gz_resource_path,  # ✅ Set resource paths first
        # gz_model_path,     # ✅ Set model paths
        start_gazebo,      # Start Gazebo with world
        robot_state_publisher_node, # ✅ FIXED: Now has robot_description
        spawn_robot,       # Spawn robot in world
        bridge_cmd_vel,    # Bridge ROS <-> Gazebo
        rviz_node          # Visualize in RViz
    ])
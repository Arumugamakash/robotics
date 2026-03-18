import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import TextSubstitution
from pathlib import Path

def generate_launch_description():

    # Absolute path to your URDF file
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),'urdf','tortoisebot.urdf'
    )

    # # # convert URDF XML string
    robot_description_config = TextSubstitution(text=Path(urdf_file).read_text())
    
    # Include Gazebo simulation launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': 'empty.sdf -r',
            'on_exit_shutdown': 'true'
        }.items()
    )

    # Robot State Publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_config}]
    )

    # Spawn TortoiseBot in Gazebo
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'tortoisebot',
            '-allow_renaming', 'true',
            '-z', '1'
        ]
    )

    # ROS ↔ Gazebo bridge (cmd_vel and LaserScan)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ]
    )

    return LaunchDescription([
        gz_sim, 
        rsp_node,
        spawn_node,
        bridge_node
    ])

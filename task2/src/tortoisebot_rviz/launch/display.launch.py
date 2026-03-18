import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import TextSubstitution
from pathlib import Path
from launch.actions import Shutdown

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),'urdf','tortoisebot.urdf'
    )
    robot_description_config = TextSubstitution(text=Path(urdf_file).read_text())

    robot_state_publisher_node=Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            # arguments=[urdf_file],
            parameters=[{'robot_description': robot_description_config}]
        )
    joint_state_publisher_node=Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        )
    rviz_node=Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            on_exit=Shutdown()
        )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node,
        joint_state_publisher_node
    ])

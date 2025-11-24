# tortoisebot_description/launch/display.launch.py
import os
# import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import TextSubstitution
from pathlib import Path

from launch.actions import RegisterEventHandler, EmitEvent, Shutdown
# from launch.event_handlers import OnProcessExit
# from launch.events import Shutdown

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),'urdf','tortoisebot.urdf'
    )
    # # # If using xacro, convert to URDF XML string
    robot_description_config = TextSubstitution(text=Path(urdf_file).read_text())

     # Read the URDF contents
    # with open(urdf_file, 'r') as infp:
    #     robot_desc = infp.read()
    
    robot_state_publisher_node=Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file],
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
        joint_state_publisher_node,
        # RegisterEventHandler(
        #     event_handler=OnProcessExit(
        #         target_action=rviz_node,
        #         on_exit=[EmitEvent(event=Shutdown())]
        #     )
        # )
    ])

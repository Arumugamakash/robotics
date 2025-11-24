import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Path to your URDF file
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),'urdf','tortoisebot.urdf'
    )
    
    # Path to a world file (empty world)
    world_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),'worlds','empty.sdf'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        # Pass the world file path to the launch file
            launch_arguments={'gz_args': f'{world_file} -r','on_exit_shutdown':'true'}.items()
    ),
    
    
         # Robot State Publisher (publishes TF from URDF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            # name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file]
        ),

        # Spawn robot entity inside Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic', 'robot_description',
                '-name', 'tortoisebot',
                '-allow_renaming', 'true','-z','1'
            ],
            output='screen'
        ),
        # ROS ↔ Gazebo bridge (for cmd_vel and odom)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            output='screen',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                # '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry'
            ]
        ),
        
    ])
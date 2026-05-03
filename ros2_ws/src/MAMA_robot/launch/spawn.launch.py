from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_path

def generate_launch_description():
    urdf_path = get_package_share_path('MAMA_robot') / 'urdf' / 'robot.urdf'
    
    return LaunchDescription([
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-file', str(urdf_path), '-entity', 'MAMA_robot'],
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_path).read()}],
        ),
    ])

import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class IrrigationPatternNode(Node):
    """Publish a simple irrigation-like movement pattern for RViz visualization."""

    def __init__(self):
        super().__init__('irrigation_pattern')
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.cmd_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        self.timer_period = 0.05
        self.timer = self.create_timer(self.timer_period, self.on_timer)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        turn_speed = 0.6
        quarter_turn_duration = (math.pi / 2.0) / turn_speed

        self.phases = [
            ('straight_1', 6.0, 0.12, 0.0),
            ('pause', 1.2, 0.0, 0.0),
            ('turn_right_1', quarter_turn_duration, 0.0, -turn_speed),
            ('shift_1', 1.5, 0.10, 0.0),
            ('turn_right_2', quarter_turn_duration, 0.0, -turn_speed),
            ('straight_2', 6.0, 0.12, 0.0),
            ('pause', 1.2, 0.0, 0.0),
            ('turn_left_1', quarter_turn_duration, 0.0, turn_speed),
            ('shift_2', 1.5, 0.10, 0.0),
            ('turn_left_2', quarter_turn_duration, 0.0, turn_speed),
        ]
        self.phase_index = 0
        self.phase_elapsed = 0.0

        self.get_logger().info('Irrigation pattern started: straight lane, edge turn, short offset, edge turn, repeat.')

    def on_timer(self):
        """Advance the pose and publish TF, odometry and the current command."""
        _, duration, linear_speed, angular_speed = self.phases[self.phase_index]

        self.x += linear_speed * math.cos(self.yaw) * self.timer_period
        self.y += linear_speed * math.sin(self.yaw) * self.timer_period
        self.yaw += angular_speed * self.timer_period
        self.phase_elapsed += self.timer_period

        if self.phase_elapsed >= duration:
            self.phase_index = (self.phase_index + 1) % len(self.phases)
            self.phase_elapsed = 0.0

        self.publish_cmd(linear_speed, angular_speed)
        self.publish_transform()
        self.publish_odometry(linear_speed, angular_speed)

    def publish_cmd(self, linear_speed, angular_speed):
        """Publish the command for visibility in ROS topics."""
        cmd = Twist()
        cmd.linear.x = linear_speed
        cmd.angular.z = angular_speed
        self.cmd_publisher.publish(cmd)

    def publish_transform(self):
        """Publish the moving transform used by RViz."""
        now = self.get_clock().now().to_msg()
        transform = TransformStamped()
        transform.header.stamp = now
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0

        qx, qy, qz, qw = self.yaw_to_quaternion(self.yaw)
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(transform)

    def publish_odometry(self, linear_speed, angular_speed):
        """Publish odometry so the movement can be inspected if needed."""
        now = self.get_clock().now().to_msg()
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        qx, qy, qz, qw = self.yaw_to_quaternion(self.yaw)
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = linear_speed
        odom.twist.twist.angular.z = angular_speed
        self.odom_publisher.publish(odom)

    @staticmethod
    def yaw_to_quaternion(yaw):
        """Convert a yaw angle into a quaternion."""
        return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)


def main(args=None):
    """Run the irrigation movement node."""
    rclpy.init(args=args)
    node = IrrigationPatternNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

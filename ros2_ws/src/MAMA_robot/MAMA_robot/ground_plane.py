import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from visualization_msgs.msg import Marker


class GroundPlaneNode(Node):
    """Publish a green floor and simple grass tufts for RViz."""

    def __init__(self):
        super().__init__('ground_plane')
        self.publisher = self.create_publisher(Marker, 'ground_marker', 10)
        self.timer = self.create_timer(0.5, self.publish_ground)
        self.grass_layers = self.build_grass_layers()

    @staticmethod
    def build_grass_layers():
        """Create dense deterministic point grids that look like fine grass."""
        layers = []
        configs = [
            (0.22, 0.04, 0.12, 0.42, 0.12),
            (0.18, 0.06, 0.16, 0.50, 0.14),
            (0.14, 0.08, 0.20, 0.58, 0.16),
        ]

        for step, offset_x, offset_y, green_value, z_scale in configs:
            points = []
            x_val = -10.0
            row = 0
            while x_val <= 10.0:
                y_val = -10.0
                while y_val <= 10.0:
                    point = Point()
                    point.x = x_val + (offset_x if row % 2 == 0 else -offset_x)
                    point.y = y_val + (offset_y if row % 2 == 0 else -offset_y)
                    point.z = z_scale / 2.0
                    points.append(point)
                    y_val += step
                x_val += step
                row += 1
            layers.append((points, green_value, z_scale))

        return layers

    def publish_ground(self):
        """Publish a solid green floor plus dense fine grass blades."""
        stamp = self.get_clock().now().to_msg()

        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = stamp
        marker.ns = 'ground'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.pose.position.z = -0.02
        marker.scale.x = 20.0
        marker.scale.y = 20.0
        marker.scale.z = 0.02
        marker.color.r = 0.10
        marker.color.g = 0.45
        marker.color.b = 0.10
        marker.color.a = 1.0
        self.publisher.publish(marker)

        for idx, (points, green_value, z_scale) in enumerate(self.grass_layers, start=1):
            grass = Marker()
            grass.header.frame_id = 'odom'
            grass.header.stamp = stamp
            grass.ns = 'grass'
            grass.id = idx
            grass.type = Marker.CUBE_LIST
            grass.action = Marker.ADD
            grass.pose.orientation.w = 1.0
            grass.scale.x = 0.015
            grass.scale.y = 0.015
            grass.scale.z = z_scale
            grass.color.r = 0.05
            grass.color.g = green_value
            grass.color.b = 0.05
            grass.color.a = 1.0
            grass.points = points
            self.publisher.publish(grass)


def main(args=None):
    """Run the ground plane publisher."""
    rclpy.init(args=args)
    node = GroundPlaneNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

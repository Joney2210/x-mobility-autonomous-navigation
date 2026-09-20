import carb
import omni
import omni.graph.core as og
from isaacsim.core.utils.extensions import enable_extension
from isaacsim.core.api import PhysicsContext
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.storage.native import get_assets_root_path
from pxr import Usd
import numpy as np
import rclpy

enable_extension("omni.isaac.ros2_bridge")
omni.kit.app.get_app().update()

carb.settings.get_settings().set_bool(
    "/exts/omni.isaac.ros2_bridge/publish_without_verification", True
)

rclpy.init()

assets_root = get_assets_root_path()
scene_usd = assets_root + "/Isaac/Environments/Simple_Warehouse/full_warehouse.usd"
robot_usd = assets_root + "/Isaac/Samples/ROS2/Robots/Nova_Carter_ROS.usd"

print("Loading warehouse scene...")
omni.usd.get_context().open_stage(scene_usd)
for _ in range(20):
    omni.kit.app.get_app().update()

stage = omni.usd.get_context().get_stage()
with Usd.EditContext(stage, stage.GetRootLayer()):
    stage.SetEndTimeCode(10000000.0)

PhysicsContext(physics_dt=1.0/60.0)

print("Adding Nova Carter...")
robot = WheeledRobot(
    prim_path="/World/Nova_Carter",
    wheel_dof_names=["joint_wheel_left", "joint_wheel_right"],
    create_robot=True,
    usd_path=robot_usd,
    position=np.array([0.0, 0.0, 0.0]),
)

for _ in range(10):
    omni.kit.app.get_app().update()

try:
    og.Controller.attribute("/World/Nova_Carter/front_hawk/left_camera_render_product.inputs:enabled").set(True)
    og.Controller.attribute("/World/Nova_Carter/front_hawk/right_camera_render_product.inputs:enabled").set(True)
    for cam in ["/left_hawk", "/right_hawk", "/back_hawk"]:
        og.Controller.attribute(f"/World/Nova_Carter{cam}/left_camera_render_product.inputs:enabled").set(False)
        og.Controller.attribute(f"/World/Nova_Carter{cam}/right_camera_render_product.inputs:enabled").set(False)
except Exception as e:
    print(f"Camera setup note: {e}")

timeline = omni.timeline.get_timeline_interface()
timeline.play()
for _ in range(5):
    omni.kit.app.get_app().update()

robot.initialize()

print("\n=== CARTER NAVIGATION RUNNING ===")
print("Check topics in another terminal: ros2 topic list")

node = rclpy.create_node("isaac_heartbeat")
frame = 0
app = omni.kit.app.get_app()
try:
    while app.is_running():
        app.update()
        rclpy.spin_once(node, timeout_sec=0)
        frame += 1
        if frame % 600 == 0:
            print(f"Running... frame {frame}")
except KeyboardInterrupt:
    print("Stopping...")

node.destroy_node()
rclpy.shutdown()
timeline.stop()

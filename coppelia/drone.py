from dcs_world.communication.messages import RobotStatusMessage
from dcs_world.robot import Drone
from dcs_world.geometry import Twist, Vector3, Pose
from dcs_world.communication import Publisher, Subscriber

STATUS_PUBLISH_TOPIC = "dcs_world.drone_1.status"

# Velocita' di prova in m/s
TEST_VEL_X = 0.1
TEST_VEL_Y = 0.0


def set_target_pose(pose: Pose, target_handle):
    sim.setObjectPosition(target_handle, -1, [pose.x, pose.y, pose.z])
    sim.setObjectOrientation(target_handle, -1, [0.0, 0.0, pose.yaw])
    

def sysCall_init():
    sim = require('sim')
    
    self.drone_handle = sim.getObject('/Quadcopter')
    self.target_handle = sim.getObject('/target')
    
    # Publishers and subscribers
    self.status_pub = Publisher(
        sim=sim,
        topic=STATUS_PUBLISH_TOPIC
    )
    
    # Initialize the drone model with its initial pose and state of charge
    init_pose = Pose.from_coordinates(
        x=sim.getObjectPosition(self.drone_handle, -1)[0],
        y=sim.getObjectPosition(self.drone_handle, -1)[1],
        z=sim.getObjectPosition(self.drone_handle, -1)[2],
        yaw=sim.getObjectOrientation(self.drone_handle, -1)[2]
    )
    
    self.drone = Drone(
        init_pose=init_pose,
        init_soc = 100.0,
        config = Drone.DEFAULT_CONFIG
    )
    
    drone_status_msg = RobotStatusMessage(
        timestamp=sim.getSimulationTime(),
        id="drone_1",
        robot_type="Drone",
        pose = self.drone.pose,
        velocity = self.drone.velocity,
        soc = self.drone.soc,
        status = self.drone.status
    )
    
    self.status_pub.publish(drone_status_msg)

    self.dt = sim.getSimulationTimeStep()


def sysCall_actuation():
    # Per ora generiamo noi i comandi
    cmd_vel_x = TEST_VEL_X
    cmd_vel_y = TEST_VEL_Y

    cmd_vel_twist = Twist(
        linear=Vector3(x=cmd_vel_x, y=cmd_vel_y, z=0.0),
        angular=Vector3(x=0.0, y=0.0, z=0.0)
    )
    
    self.drone.move(cmd_vel_twist, self.dt)
    
    set_target_pose(self.drone.pose, self.target_handle)
    # control_loop(cmd_vel_twist, self.dt)


def sysCall_sensing():
    pass


def sysCall_cleanup():
    pass
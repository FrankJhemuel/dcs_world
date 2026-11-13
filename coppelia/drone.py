from dcs_world.robot.drone import Drone
from dcs_world.geometry import Twist, Pose
from dcs_world.communication import Publisher, Subscriber
from dcs_world.coppelia.utils import get_next_drone_id

# Velocita' di prova in m/s
TEST_VEL_X = 0.1
TEST_VEL_Y = 0.0

#* ====================================
#* UTILITY FUNCTIONS
#* ====================================

def set_target_pose(pose: Pose, target_handle):
    sim.setObjectPosition(target_handle, -1, [pose.x, pose.y, pose.z])
    sim.setObjectOrientation(target_handle, -1, [0.0, 0.0, pose.yaw])
    

#* ====================================
#* COPPELIA SIMULATION CALLBACKS
#* ====================================

def sysCall_init():
    sim = require('sim')
    
    self.drone_handle = sim.getObject('/Quadcopter')
    self.target_handle = sim.getObject('/target')
    
    robot_id = get_next_drone_id(sim)
    
    # Initialize the drone model with its initial pose and state of charge
    init_pose = Pose.from_coordinates(
        x=sim.getObjectPosition(self.drone_handle, -1)[0],
        y=sim.getObjectPosition(self.drone_handle, -1)[1],
        z=sim.getObjectPosition(self.drone_handle, -1)[2],
        yaw=sim.getObjectOrientation(self.drone_handle, -1)[2]
    )
    
    self.drone = Drone(
        id=str(robot_id),
        init_pose=init_pose,
        init_soc = 100.0,
        config = Drone.DEFAULT_CONFIG
    )
    
    # Publishers and subscribers
    self.status_pub = Publisher(
        sim=sim,
        topic=f"{robot_id}.status",
    )
    
    drone_status_msg = self.drone.to_robot_status_message()
    
    self.status_pub.publish(drone_status_msg)

    self.dt = sim.getSimulationTimeStep()


def sysCall_actuation():
    # Per ora generiamo noi i comandi
    cmd_vel_x = TEST_VEL_X
    cmd_vel_y = TEST_VEL_Y

    cmd_vel_twist = Twist(
        linear=[cmd_vel_x, cmd_vel_y, 0.0],
        angular=[0.0, 0.0, 0.0]
    )
    
    self.drone.move(cmd_vel_twist, self.dt)
    
    set_target_pose(self.drone.pose, self.target_handle)
    self.status_pub.publish(self.drone.to_robot_status_message())


def sysCall_sensing():
    pass


def sysCall_cleanup():
    pass
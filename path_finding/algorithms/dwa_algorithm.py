"""
Dynamic Window Approach (DWA) Algorithm
Optimized for integration with GUI-based pathfinding systems.
"""

import math
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import time


class RobotType(Enum):
    circle = 0
    rectangle = 1


class Config:
    """ Simulation parameter class """
    def __init__(self):
        # Robot parameters
        self.max_speed = 1.0  # [m/s]
        self.min_speed = -0.5  # [m/s]
        self.max_yaw_rate = 40.0 * math.pi / 180.0  # [rad/s]
        self.max_accel = 0.2  # [m/s²]
        self.max_delta_yaw_rate = 40.0 * math.pi / 180.0  # [rad/s²]
        self.v_resolution = 0.01  # [m/s]
        self.yaw_rate_resolution = 0.1 * math.pi / 180.0  # [rad/s]
        self.dt = 0.1  # [s]
        self.predict_time = 3.0  # [s]
        self.to_goal_cost_gain = 0.15
        self.speed_cost_gain = 1.0
        self.obstacle_cost_gain = 1.0
        self.robot_stuck_flag_cons = 0.001
        self.robot_type = RobotType.circle
        self.robot_radius = 1.0
        self.robot_width = 0.5
        self.robot_length = 1.2


def motion(x, u, dt):
    """ Motion model """
    x[2] += u[1] * dt
    x[0] += u[0] * math.cos(x[2]) * dt
    x[1] += u[0] * math.sin(x[2]) * dt
    x[3] = u[0]
    x[4] = u[1]
    return x


def calc_dynamic_window(x, config):
    """ Calculate dynamic window based on current state """
    Vs = [config.min_speed, config.max_speed,
          -config.max_yaw_rate, config.max_yaw_rate]

    Vd = [x[3] - config.max_accel * config.dt,
          x[3] + config.max_accel * config.dt,
          x[4] - config.max_delta_yaw_rate * config.dt,
          x[4] + config.max_delta_yaw_rate * config.dt]

    dw = [max(Vs[0], Vd[0]), min(Vs[1], Vd[1]),
          max(Vs[2], Vd[2]), min(Vs[3], Vd[3])]
    return dw


def predict_trajectory(x_init, v, y, config):
    """ Predict trajectory given velocity and yaw rate """
    x = np.array(x_init)
    trajectory = np.array(x)
    time_ = 0
    while time_ <= config.predict_time:
        x = motion(x, [v, y], config.dt)
        trajectory = np.vstack((trajectory, x))
        time_ += config.dt
    return trajectory


def calc_to_goal_cost(trajectory, goal):
    """ Calculate cost based on distance to goal """
    dx = goal[0] - trajectory[-1, 0]
    dy = goal[1] - trajectory[-1, 1]
    error_angle = math.atan2(dy, dx)
    cost_angle = error_angle - trajectory[-1, 2]
    return abs(math.atan2(math.sin(cost_angle), math.cos(cost_angle)))


def calc_obstacle_cost(trajectory, ob, config):
    """ Calculate obstacle cost (infinite if collision occurs) """
    ox = ob[:, 0]
    oy = ob[:, 1]
    dx = trajectory[:, 0] - ox[:, None]
    dy = trajectory[:, 1] - oy[:, None]
    r = np.hypot(dx, dy)

    if config.robot_type == RobotType.rectangle:
        yaw = trajectory[:, 2]
        rot = np.array([[np.cos(yaw), -np.sin(yaw)], [np.sin(yaw), np.cos(yaw)]])
        rot = np.transpose(rot, [2, 0, 1])
        local_ob = ob[:, None] - trajectory[:, 0:2]
        local_ob = local_ob.reshape(-1, local_ob.shape[-1])
        local_ob = np.array([local_ob @ x for x in rot])
        local_ob = local_ob.reshape(-1, local_ob.shape[-1])
        upper_check = local_ob[:, 0] <= config.robot_length / 2
        right_check = local_ob[:, 1] <= config.robot_width / 2
        bottom_check = local_ob[:, 0] >= -config.robot_length / 2
        left_check = local_ob[:, 1] >= -config.robot_width / 2
        if (np.logical_and(np.logical_and(upper_check, right_check),
                           np.logical_and(bottom_check, left_check))).any():
            return float("Inf")
    elif config.robot_type == RobotType.circle:
        if np.array(r <= config.robot_radius).any():
            return float("Inf")
    min_r = np.min(r)
    return 1.0 / min_r


def calc_control_and_trajectory(x, dw, config, goal, ob):
    """ Evaluate trajectories and select best control input """
    x_init = x[:]
    min_cost = float("inf")
    best_u = [0.0, 0.0]
    best_trajectory = np.array([x])

    for v in np.arange(dw[0], dw[1], config.v_resolution):
        for y in np.arange(dw[2], dw[3], config.yaw_rate_resolution):
            trajectory = predict_trajectory(x_init, v, y, config)
            to_goal_cost = config.to_goal_cost_gain * calc_to_goal_cost(trajectory, goal)
            speed_cost = config.speed_cost_gain * (config.max_speed - trajectory[-1, 3])
            ob_cost = config.obstacle_cost_gain * calc_obstacle_cost(trajectory, ob, config)
            final_cost = to_goal_cost + speed_cost + ob_cost
            if min_cost >= final_cost:
                min_cost = final_cost
                best_u = [v, y]
                best_trajectory = trajectory
                if abs(best_u[0]) < config.robot_stuck_flag_cons and abs(x[3]) < config.robot_stuck_flag_cons:
                    best_u[1] = -config.max_delta_yaw_rate
    return best_u, best_trajectory


def dwa_control(x, config, goal, ob):
    """ Main Dynamic Window Approach control """
    dw = calc_dynamic_window(x, config)
    u, trajectory = calc_control_and_trajectory(x, dw, config, goal, ob)
    return u, trajectory


def plot_robot(x, y, yaw, config):
    """Draw robot shape"""
    if config.robot_type == RobotType.rectangle:
        outline = np.array([[-config.robot_length / 2, config.robot_length / 2,
                             config.robot_length / 2, -config.robot_length / 2,
                             -config.robot_length / 2],
                            [config.robot_width / 2, config.robot_width / 2,
                             -config.robot_width / 2, -config.robot_width / 2,
                             config.robot_width / 2]])
        Rot1 = np.array([[math.cos(yaw), math.sin(yaw)],
                         [-math.sin(yaw), math.cos(yaw)]])
        outline = (outline.T.dot(Rot1)).T
        outline[0, :] += x
        outline[1, :] += y
        plt.plot(outline[0, :], outline[1, :], "-k")
    elif config.robot_type == RobotType.circle:
        circle = plt.Circle((x, y), config.robot_radius, color="b", fill=False)
        plt.gca().add_artist(circle)
        out_x, out_y = (np.array([x, y]) +
                        np.array([np.cos(yaw), np.sin(yaw)]) * config.robot_radius)
        plt.plot([x, out_x], [y, out_y], "-k")


def run_algorithm(start, goal, obstacles, slam_data=None, visualize=False):
    """
    Unified entry point for DWA for GUI and analysis modules.
    """
    try:
        config = Config()
        x = np.array([start[0], start[1], 0.0, 0.0, 0.0])  # [x, y, yaw, v, omega]
        goal = np.array(goal)
        ob = np.array(obstacles)
        trajectory = np.array(x)
        iterations = 0
        start_time = time.time()

        while True:
            u, predicted_trajectory = dwa_control(x, config, goal, ob)
            x = motion(x, u, config.dt)
            trajectory = np.vstack((trajectory, x))
            iterations += 1

            dist_to_goal = math.hypot(x[0] - goal[0], x[1] - goal[1])

            if visualize and iterations % 10 == 0:
                plt.cla()
                plt.plot(predicted_trajectory[:, 0], predicted_trajectory[:, 1], "-g")
                plt.plot(trajectory[:, 0], trajectory[:, 1], "-r")
                plt.plot(ob[:, 0], ob[:, 1], "ok")
                plt.scatter(goal[0], goal[1], c='b', label='Goal')
                plot_robot(x[0], x[1], x[2], config)
                plt.axis("equal")
                plt.grid(True)
                plt.pause(0.001)

            # Exit conditions
            if dist_to_goal <= config.robot_radius or iterations > 1000:
                break

        metrics = {
            'path_length': np.sum(np.linalg.norm(np.diff(trajectory[:, :2], axis=0), axis=1)),
            'iterations': iterations,
            'success_rate': 1.0 if dist_to_goal <= config.robot_radius else 0.0,
            'execution_time': time.time() - start_time,
            'smoothness': np.std(np.diff(trajectory[:, 2])) if len(trajectory) > 2 else 0,
        }

        if visualize:
            plt.plot(trajectory[:, 0], trajectory[:, 1], "-r")
            plt.title("DWA Path")
            plt.show(block=False)
            plt.pause(0.1)

        return trajectory[:, :2], metrics

    except Exception as e:
        print(f"[ERROR] {__name__} failed: {e}")
        return None, {'error': str(e)}


# For standalone testing
if __name__ == "__main__":
    start = np.array([0.0, 0.0])
    goal = np.array([10.0, 10.0])
    obstacles = np.array([[3, 3], [6, 6], [7, 5]])
    run_algorithm(start, goal, obstacles, visualize=True)

"""
Author: HTY
Email: 1044213317@qq.com
Date: 2023-02-16 16:04
Description:
    - [Optimal Trajectory Generation for Dynamic Street Scenarios in a Frenet Frame]
    (https://www.researchgate.net/profile/Moritz_Werling/publication/224156269_Optimal_Trajectory_Generation_for_Dynamic_Street_Scenarios_in_a_Frenet_Frame/links/54f749df0cf210398e9277af.pdf)
    (https://www.youtube.com/watch?v=Cj6tAQe7UCY)
"""

from algorithms.lattice.quintic_polynomial import QuinticPolynomial
from algorithms.lattice.quartic_polynomial import QuarticPolynomial
from algorithms.lattice.cubic_spline import CubicSpline2D

import numpy as np
import matplotlib.pyplot as plt
import copy


class FrenetPath:
    def __init__(self):
        self.lat_traj = None
        self.lon_traj = None
        self.index = 0
        self.t = []

        self.d = []  # 左负右正
        self.d_d = []
        self.d_dd = []
        self.d_ddd = []
        self.s = []
        self.s_d = []
        self.s_dd = []
        self.s_ddd = []

        self.x = []
        self.y = []
        self.yaw = []
        self.ds = []  # 用来算曲率
        self.curvature = []

        self.satisfied = True

class LatticePlanner:
    # Parameter
    MAX_V = 8   # maximum speed [m/s]
    MIN_V = 1   # minimum speed [m/s]
    DELTA_V = 1 # speed sampling length [m/s]

    MAX_D = 4.0     # maximum road width [m]
    MIN_D = -4.0    # minimun road width [m]
    DELTA_D = 1.0   # road width sampling length [m]

    MAX_T = 8.0  # max prediction time [s]
    MIN_T = 1.0  # min prediction time [s]
    DELTA_T = 1  # time tick [s]

    MAX_S = 30.0  # max longitude distance [m]
    MIN_S = 10.0  # min longitude distance [m]
    DELTA_S = 5.0  # distance sampling length [m]

    MAX_A = 5.0  # maximum acceleration [m/ss]
    MAX_K = 1.0  # maximum curvature [1/m]
    ROBOT_RADIUS = 2.0  # robot radius [m]

    # cost weights
    K_J = 0.1
    K_T = 0.1
    K_D = 1.0
    K_LAT = 1.0
    K_LON = 1.0

    def __init__(self):
        self.t_dim = int((self.MAX_T - self.MIN_T) / self.DELTA_T + 1)  # 3
        self.v_dim = int((self.MAX_V - self.MIN_V) / self.DELTA_V + 1)  # 5
        self.s_dim = int((self.MAX_S - self.MIN_S) / self.DELTA_S + 1)  # 5
        self.d_dim = int((self.MAX_D - self.MIN_D) / self.DELTA_D + 1)  # 7
        self.sample_dim = int(self.t_dim * self.v_dim * self.d_dim)
        self.dt = 0.05

        self.index_dict = {}
        index = 0
        for ti in np.arange(self.MIN_T, self.MAX_T + self.DELTA_T, self.DELTA_T):  # 轨迹时间
            for di in np.arange(-self.MAX_D, self.MAX_D + self.DELTA_D, self.DELTA_D):  # 道路宽度
                for vi in np.arange(self.MIN_V, self.MAX_V + self.DELTA_V, self.DELTA_V):  # 末端速度
                    self.index_dict[index] = (ti, di, vi)
                    index += 1

    def calc_frenet_paths(self, s, s_d, s_dd, d, d_d, d_dd):
        frenet_paths = []
        index = 0

        for ti in np.arange(self.MIN_T, self.MAX_T + self.DELTA_T, self.DELTA_T):  # 轨迹时间
            for di in np.arange(-self.MAX_D, self.MAX_D + self.DELTA_D, self.DELTA_D):  # 道路宽度
                lat_traj = QuinticPolynomial(d, d_d, d_dd, di, 0.0, 0.0, ti)
                fp = FrenetPath()
                fp.lat_traj = lat_traj
                t_else = np.arange(ti + self.dt, self.MAX_T + self.dt, self.dt)
                t_origin = np.arange(0.0, ti + self.dt, self.dt)
                fp.t = np.concatenate((t_origin, t_else), axis=0)
                d_else = np.array([lat_traj.calc_point(t_origin[-1])] * len(t_else))
                fp.d = np.concatenate((lat_traj.calc_point(t_origin), d_else), axis=0)
                fp.d_d = lat_traj.calc_first_derivative(t_origin)
                fp.d_dd = lat_traj.calc_second_derivative(t_origin)
                fp.d_ddd = lat_traj.calc_third_derivative(t_origin)

                for vi in np.arange(self.MIN_V, self.MAX_V + self.DELTA_V, self.DELTA_V):  # 末端速度
                    lon_traj = QuarticPolynomial(s, s_d, s_dd, vi, 0.0, ti)
                    # for si in np.arange(self.MIN_S, self.MAX_S + self.DELTA_S, self.DELTA_S):   # 道路长度
                    #     lon_traj = QuinticPolynomial(s, s_d, s_dd, s + si, vi, 0.0, ti)

                    fp_copy = copy.deepcopy(fp)
                    fp_copy.lon_traj = lon_traj
                    fp_copy.index = index

                    fp_copy.s = lon_traj.calc_point(t_origin)
                    v_else = np.array([lon_traj.calc_first_derivative(t_origin[-1])] * len(t_else))
                    fp_copy.s_d = np.concatenate((lon_traj.calc_first_derivative(t_origin), v_else), axis=0)
                    fp_copy.s_dd = lon_traj.calc_second_derivative(t_origin)
                    fp_copy.s_ddd = lon_traj.calc_third_derivative(t_origin)

                    frenet_paths.append(fp_copy)
                    index += 1
                    # if check_paths(fp_copy):
                    #     frenet_paths.append(fp_copy)
        return frenet_paths
    
    def calc_frenet_path(self, s, s_d, s_dd, d, d_d, d_dd, index):
        ti, di, vi = self.index_dict[index]
        fp = FrenetPath()
        fp.t = np.arange(0.0, ti + self.dt, self.dt)
        fp.lat_traj = QuinticPolynomial(d, d_d, d_dd, di, 0.0, 0.0, ti)
        fp.lon_traj = QuarticPolynomial(s, s_d, s_dd, vi, 0.0, ti)

        return fp

    def calc_cartesian_paths(self, frenet_path, reference_line):
        # calc global positions
        for i in range(len(frenet_path.s)):
            xi, yi = reference_line.calc_position(frenet_path.s[i])
            if xi is None:
                break
            yaw = reference_line.calc_yaw(frenet_path.s[i])
            di = frenet_path.d[i]
            # frenet to cartesian
            fx = xi + di * np.cos(yaw + np.pi / 2.0)
            fy = yi + di * np.sin(yaw + np.pi / 2.0)
            frenet_path.x.append(fx)
            frenet_path.y.append(fy)

        # calc yaw and ds
        for i in range(len(frenet_path.x) - 1):
            dx = frenet_path.x[i + 1] - frenet_path.x[i]
            dy = frenet_path.y[i + 1] - frenet_path.y[i]
            frenet_path.yaw.append(np.arctan2(dy, dx))
            frenet_path.ds.append(np.hypot(dx, dy))

        frenet_path.yaw.append(frenet_path.yaw[-1])
        frenet_path.ds.append(frenet_path.ds[-1])

        # calc curvature
        for i in range(len(frenet_path.yaw) - 1):
            frenet_path.curvature.append((frenet_path.yaw[i + 1] - frenet_path.yaw[i]) / frenet_path.ds[i])

        return frenet_path

    def check_collision(self, fp, ob):
        for i in range(len(ob[:, 0])):
            d = [((xi - ob[i, 0]) ** 2 + (yi - ob[i, 1]) ** 2)
                 for (xi, yi) in zip(fp.x, fp.y)]

            collision = any([di <= self.ROBOT_RADIUS ** 2 for di in d])
            if collision:
                return False

        return True

    def check_paths(self, path) -> bool:
        # if any([v > self.MAX_V for v in path.s_d]):  # Max speed check
        #     return False
        if any([abs(a) > self.MAX_A for a in path.s_dd]):  # Max accel check
            return False
        elif any([abs(curvature) > self.MAX_K for curvature in path.curvature]):  # Max curvature check
            return False
        return True

    def frenet_optimal_planning(self, reference_line: CubicSpline2D, s, s_d, s_dd, d, d_d, d_dd, ob):
        fplist = self.calc_frenet_paths(s, s_d, s_dd, d, d_d, d_dd)
        path = [self.calc_cartesian_paths(fp, reference_line) for fp in fplist]

        return path

        # find minimum cost path
        min_cost = float("inf")
        best_path = None
        for fp in fplist:
            if min_cost >= fp.cf:
                min_cost = fp.cf
                best_path = fp

        return best_path

    def generate_target_course(self, x: list, y: list):
        reference_line = CubicSpline2D(x, y)
        s_list = np.arange(0, reference_line.s[-1], 0.1)

        x_list, y_list, yaw_list, curvature_list = [], [], [], []
        for s in s_list:
            x, y = reference_line.calc_position(s)
            x_list.append(x)
            y_list.append(y)
            yaw_list.append(reference_line.calc_yaw(s))
            curvature_list.append(reference_line.calc_curvature(s))

        return x_list, y_list, yaw_list, curvature_list, reference_line

    def cartesian_to_frenet(self, reference_line, x, y):
        """ s前为正，d左为正 """
        xi, yi = reference_line.calc_perpendicular_point(x, y)
        s = reference_line.calc_s(xi)
        d = np.hypot(y - yi, x - xi) if x <= xi else -np.hypot(y - yi, x - xi)
        return s, d

    def frenet_to_cartesian(self, reference_line, s, d):
        x, y = reference_line.calc_position(s)
        # yaw = reference_line.calc_yaw(s)
        yaw = reference_line.yaw
        x -= d * np.sin(yaw)
        y += d * np.cos(yaw)
        return x, y


def main():
    print(__file__ + " start!!")

    # way points & obstacles
    way_points_x = [0.0, 10.0, 20.5, 35.0, 70.5]
    way_points_y = [0.0, -6.0, 5.0, 6.5, 0.0]
    ob = np.array([[20.0, 10.0], [30.0, 6.0], [30.0, 8.0], [35.0, 8.0], [50.0, 3.0]])
    # way_points_x = [0.0, 40.0]
    # way_points_y = [0.0, 40.0]
    # ob = np.array([[3.0, 3.0], [10.0, 11.0], [23.0, 25.0]])

    planner = LatticePlanner()
    tx, ty, tyaw, tc, reference_line = planner.generate_target_course(way_points_x, way_points_y)

    # initial state
    s = 10.0  # current course position
    s_d = 10/3.6  # current speed [m/s]
    s_dd = 0.0  # current acceleration [m/ss]
    d = 2.0  # current lateral position [m]
    d_d = 0.0  # current lateral speed [m/s]
    d_dd = 0.0  # current lateral acceleration [m/s]

    area = 30.0  # animation area length [m]

    while True:
        # path = frenet_optimal_planning(reference_line, s, s_d, s_dd, d, d_d, d_dd, ob)
        #
        # s = path.s[1]
        # d = path.d[1]
        # d_d = path.d_d[1]
        # d_dd = path.d_dd[1]
        # s_d = path.s_d[1]
        # s_dd = path.s_dd[1]
        #
        # if np.hypot(path.z[1] - tx[-1], path.y[1] - ty[-1]) <= 2.0:
        #     print("Goal")
        #     break

        # x, y = 30, 10
        # x_d, y_d = 1, 0
        # s, d, s_d, d_d = planner.cartesian_to_frenet(reference_line, x, y, x_d, y_d)
        # plt.plot(reference_line.x, reference_line.y)
        # plt.plot(x, y, "x")
        # plt.grid(True)
        # plt.show()

        candidate_trajectories = planner.frenet_optimal_planning(reference_line, s, s_d, s_dd, d, d_d, d_dd, ob)
        print(len(candidate_trajectories))
        # if show_animation:  # pragma: no cover
        for path in candidate_trajectories:
            # plt.cla()
            # for stopping simulation with the esc key.
            plt.gcf().canvas.mpl_connect(
                'key_release_event',
                lambda event: [exit(0) if event.key == 'escape' else None])
            plt.plot(tx, ty)
            # plt.plot(ob[:, 0], ob[:, 1], "xk")
            if planner.check_paths(path) is False:
                color = 'silver'
            else:
                color = 'k'
            plt.plot(path.x[1:], path.y[1:], c=color)
            plt.plot(path.x[1], path.y[1], "vc")
            plt.xlabel('x[m]')
            plt.ylabel('y[m]')
            plt.xlim(path.x[1] - 10, path.x[1] + 20)
            plt.ylim(path.y[1] - 10, path.y[1] + 20)
            plt.grid(True)
            # plt.pause(0.0001)
        plt.show()
        print()
        # for path in candidate_trajectories:
        #     # plt.cla()
        #     # for stopping simulation with the esc key.
        #     plt.gcf().canvas.mpl_connect(
        #         'key_release_event',
        #         lambda event: [exit(0) if event.key == 'escape' else None])
        #     if planner.check_paths(path) is False:
        #         color = 'silver'
        #     else:
        #         color = 'k'
        #     plt.plot(path.t, path.d, c=color, linewidth=1.0)
        #     plt.xlabel('T[s]')
        #     plt.ylabel('d[m]')
        #     plt.grid(True, ls='--')
        #     # plt.pause(0.0001)
        # plt.show()
        # for path in candidate_trajectories:
        #     # plt.cla()
        #     # for stopping simulation with the esc key.
        #     plt.gcf().canvas.mpl_connect(
        #         'key_release_event',
        #         lambda event: [exit(0) if event.key == 'escape' else None])
        #     if planner.check_paths(path) is False:
        #         color = 'silver'
        #     else:
        #         color = 'k'
        #     plt.plot(path.t, path.s_d, c=color, linewidth=1.0)
        #     plt.xlabel('T[s]')
        #     plt.ylabel('v[m/s]')
        #     plt.grid(True, ls='--')
        # plt.show()

    print("Finish")
    if show_animation:  # pragma: no cover
        plt.grid(True)
        plt.pause(0.0001)
        plt.show()


if __name__ == '__main__':
    main()

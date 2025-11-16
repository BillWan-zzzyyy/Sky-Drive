import sys
import glob
import os
import time
import cv2
import yaml

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import copy
import gym
import numpy as np
import carla
import math
import random
import json
from scipy.interpolate import CubicSpline
import weakref


SEP = os.sep
label_class = {1: 'car',
               2: 'bus',
               3: 'truck',
               4: 'trailer',
               5: 'construction_vehicle',
               6: 'pedestrian',
               7: 'motorcycle',
               8: 'bicycle',
               9: 'traffic_cone',
               10: 'barrier'
               }
class_blueprint = {
    'car': ['vehicle.tesla.model3', 'vehicle.audi.tt',
            'vehicle.chevrolet.impala'],
    'bus': ['vehicle.volkswagen.t2', 'vehicle.carlamotors.carlacola'],
    'truck': ['vehicle.carlamotors.firetruck', 'vehicle.carlamotors.carlacola',
              'vehicle.ford.ambulance'],
    'trailer': ['vehicle.carlamotors.carlacola', 'vehicle.tesla.cybertruck'],
    'construction_vehicle': ['vehicle.carlamotors.carlacola'],
    'pedestrian': ['walker.pedestrian.0001', 'walker.pedestrian.0002',
                   'walker.pedestrian.0003', 'walker.pedestrian.0004'],
    'motorcycle': ['vehicle.kawasaki.ninja', 'vehicle.yamaha.yzf'],
    'bicycle': ['vehicle.diamondback.century', 'vehicle.gazelle.omafiets'],
    'traffic_cone': ['static.prop.trafficcone01', 'static.prop.trafficcone02'],
    'barrier': ['static.prop.streetbarrier']
}
root_path = os.path.abspath(os.path.dirname(__file__))


class CollisionDetector(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        world = self._parent.get_world()
        blueprint_library = world.get_blueprint_library()
        collision_sensor_bp = blueprint_library.find('sensor.other.collision')
        self.sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(), attach_to=self._parent)
        self.sensor.listen(self._on_collision)
        self.collision_occurred = False

    def _on_collision(self, event):
        self.collision_occurred = True


class RGBCamera:
    def __init__(self, world, ego_vehicle, save_dir=None, data_dump=False, direction='front_rgb_camera', resolution=(256, 256), fov=105):
        super(RGBCamera, self).__init__()
        self.world = world
        self.ego_vehicle = ego_vehicle
        self.direction = direction
        self.resolution = resolution
        self.fov = fov
        self.save_dir = save_dir
        self.data_dump = data_dump

        self._weak_self = weakref.ref(self)

        self.sensor = None
        self.data_dict = {}

        self.frame = -1

    def spawn_sensor(self):
        half_width = self.ego_vehicle.bounding_box.extent.y
        half_length = self.ego_vehicle.bounding_box.extent.x
        half_height = self.ego_vehicle.bounding_box.extent.z
        ego_id = self.ego_vehicle.id

        # https://blog.csdn.net/zataji/article/details/130177492
        cam_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        cam_bp.set_attribute("image_size_x", str(self.resolution[0]))
        cam_bp.set_attribute("image_size_y", str(self.resolution[1]))
        cam_bp.set_attribute("fov", str(self.fov))
        self.image_width = int(cam_bp.get_attribute('image_size_x'))
        self.image_height = int(cam_bp.get_attribute('image_size_y'))

        if self.direction.lower() == "front_rgb_camera":
            cam_location = carla.Location(half_length - 0.05, 0, half_height - 0.01)
            cam_rotation = carla.Rotation(0, 0, 0)
        elif self.direction.lower() == "left_rgb_camera":
            cam_location = carla.Location(0, -half_width + 0.05, half_height - 0.01)
            cam_rotation = carla.Rotation(0, -90, 0)
        elif self.direction.lower() == "back_rgb_camera":
            cam_location = carla.Location(-half_length + 0.05, 0, half_height - 0.01)
            cam_rotation = carla.Rotation(0, 180, 0)
        elif self.direction.lower() == "right_rgb_camera":
            cam_location = carla.Location(0, half_width - 0.05, half_height - 0.01)
            cam_rotation = carla.Rotation(0, 90, 0)
        else:
            raise TypeError(
                "Only front_rgb_camera, left_rgb_camera, back_rgb_camera, and right_rgb_camera are allowed!")
        cam_transform = carla.Transform(cam_location, cam_rotation)

        try:
            ego_cam = self.world.spawn_actor(cam_bp, cam_transform, attach_to=self.ego_vehicle,
                                             attachment_type=carla.AttachmentType.Rigid)
            self.sensor = ego_cam
        except Exception:
            raise RuntimeError("Spawn RGB Camera failed!")

        if self.direction == "front_rgb_camera":
            world_2_camera = np.array(ego_cam.get_transform().get_inverse_matrix())
            fov = cam_bp.get_attribute("fov").as_float()
            """
            get_bbx(self.world, image, fov, world_2_camera, self.ego_vehicle,
                                                           self.save_dir, self.direction)
            """
            # ego_cam.listen(
            #     lambda image: image)
            ego_cam.listen(
                lambda event: self._on_data_event(self._weak_self, event, self.direction, ego_id))
        else:
            ego_cam.listen(
                lambda event: self._on_data_event(self._weak_self, event, self.direction, ego_id))

    @staticmethod
    def _on_data_event(weak_self, event, direction, ego_id):
        self = weak_self()
        if not self:
            return
        self.data_dump = True
        if self.save_dir and self.data_dump:
            dir_name = os.path.join(self.save_dir, 'rgb')
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f'created dir {dir_name}')
            event.save_to_disk(
                os.path.join(dir_name, f'{event.frame}_{direction}.jpg'))

        image = np.array(event.raw_data)
        image = image.reshape((self.image_height, self.image_width, 4))
        # we need to remove the alpha channel
        image = image[:, :, :3]

        self.data_dict['data'] = image
        self.data_dict['frame'] = event.frame
        self.data_dict['timestamp'] = event.timestamp
        self.frame = event.frame

    def get_last_data(self):
        # image = self.data_dict['data']
        try:
            # the sensor may not work in the very beginning, and the feature_dim should be first
            image = self.data_dict['data']#.transpose(2, 0, 1)  # (3, 256, 256)  (3, height, width)
        except:
            image = np.zeros((self.resolution[0], self.resolution[1], 3), dtype=np.int8)
        return image


def smooth_action(old_value, new_value, smooth_factor):
    return old_value * smooth_factor + new_value * (1.0 - smooth_factor)


class ReplayManager(gym.Env):
    def __init__(self, client, scene_list, config):
        # base setting
        self.client = client
        self.traffic_manager = client.get_trafficmanager()
        self.scene_list = scene_list
        self.config = config

        # traffic
        self.bg_vehicle_managers = {}
        self.spawn_queue = {}  # trajectories buffer

        # sensors
        self.save_dir = config['save_dir']
        self.bbx = config['bbx']
        self.resolution = config['resolution']
        self.fov = config['fov']
        self.data_dump = config['data_dump']
        self.channels = config['channels']
        self.points_per_second = config['points_per_second']
        self.rotation_frequency = config['rotation_frequency']
        self.range = config['range']

        # dummy
        self.world = None
        self.collision_detector_ego = None
        self.rgb_camera_ego = None
        self.start_point = None
        self.end_point = None
        self.ego_speed = None
        self.yaw_radians = None
        self.ego_vehicle = None
        self.shadow_ego_vehicle = None
        self.sim_end = 9999
        self.manual_drive = False
        self.ego_control = carla.VehicleControl()
        self.rl_active = False

        # constant scenario settings
        self.dis_scale = 1
        self.underground_dis = -50
        self.max_attempts = 5

        # constant RL settings
        self.action_smoothing = 0.
        # rl_active, steer, throttle, brake
        self.action_space = gym.spaces.Box(np.array([-1, 0, 0]), np.array([1, 1, 1]), dtype=np.float32)
        observation_space = {}
        observation_space['rgb_camera'] = gym.spaces.Box(low=0, high=255, shape=(256, 256, 3), dtype=np.uint8)
        self.observation_space = gym.spaces.Dict(observation_space)

        # dynamic RL settings
        self.last_reward = 0.
        self.total_reward = 0.
        self.done = 0
        self.timestep = 1

        # RL reward function
        self.reward_fn = (lambda x: 0)  # if not callable(reward_fn) else reward_fn

    def init_data_base(self, path):
        data_base = {}
        with open(path, 'r') as f:
            data_dict = json.load(f)
        for timestep, data_ts in data_dict.items():
            for inst in data_ts:
                if inst['score'] < 0.3:
                    continue
                if inst['tracking_id'] not in data_base:
                    data_base[inst['tracking_id']] = {}
                    data_base[inst['tracking_id']]['timestep'] = [int(timestep)]
                    data_base[inst['tracking_id']]['loc_x'] = [inst['loc'][2]]
                    data_base[inst['tracking_id']]['loc_y'] = [inst['loc'][0]]
                    data_base[inst['tracking_id']]['loc_z'] = [inst['loc'][1]]
                    data_base[inst['tracking_id']]['rot_y'] = [inst['rot_y']]
                    data_base[inst['tracking_id']]['dep'] = [inst['dep'][0]]
                    data_base[inst['tracking_id']]['class'] = inst['class']
                else:
                    data_base[inst['tracking_id']]['timestep'].append(int(timestep))
                    data_base[inst['tracking_id']]['loc_x'].append(inst['loc'][2])
                    data_base[inst['tracking_id']]['loc_y'].append(inst['loc'][0])
                    data_base[inst['tracking_id']]['loc_z'].append(inst['loc'][1])
                    data_base[inst['tracking_id']]['rot_y'].append(inst['rot_y'])
                    data_base[inst['tracking_id']]['dep'].append(inst['dep'][0])

        data_base_copy = copy.deepcopy(data_base)
        for tracking_id, data_dict in data_base.items():
            # if random.random() > :
            #     continue

            timestep_np = np.array(data_dict['timestep'])
            loc_x_np = np.array(data_dict['loc_x'])
            loc_y_np = np.array(data_dict['loc_y'])
            loc_z_np = np.array(data_dict['loc_z'])
            rot_y_np = np.array(data_dict['rot_y'])
            dep_np = np.array(data_dict['dep'])
            # remove the outliers
            data = np.vstack((timestep_np, loc_x_np, loc_y_np, loc_z_np, rot_y_np, dep_np)).T

            def calculate_angles(data):
                diffs = np.diff(data, axis=0)
                angles = np.arctan2(diffs[:, 1], diffs[:, 0])
                return angles

            # Function to remove points with large angle deviations
            def remove_large_deviations(data, angle_threshold=np.pi / 4):
                angles = calculate_angles(data)
                angle_changes = np.abs(np.diff(angles))

                filtered_entries = np.ones(len(data), dtype=bool)
                filtered_entries[1:-1] = angle_changes < angle_threshold
                return data[filtered_entries]

            cleaned_data = data  # remove_large_deviations(data)
            if cleaned_data.shape[0] < 3:
                del data_base_copy[tracking_id]
                continue
            timestep_np = cleaned_data[:, 0][: -1]
            loc_x_np = cleaned_data[:, 1][: -1]
            loc_y_np = cleaned_data[:, 2][: -1]
            loc_z_np = cleaned_data[:, 3][: -1]
            rot_y_np = cleaned_data[:, 4][: -1]
            dep_np = cleaned_data[:, 5][: -1]

            # interpolate the trajectory
            interpolate_timestep = np.arange(timestep_np.min(), timestep_np.max() + 1, 1)
            cs_x = CubicSpline(timestep_np, loc_x_np)
            cs_y = CubicSpline(timestep_np, loc_y_np)
            cs_z = CubicSpline(timestep_np, loc_z_np)
            cs_rot = CubicSpline(timestep_np, rot_y_np)
            cs_dep = CubicSpline(timestep_np, dep_np)
            interpolate_pos_x = cs_x(interpolate_timestep)
            interpolate_pos_y = cs_y(interpolate_timestep)
            interpolate_pos_z = cs_z(interpolate_timestep)
            interpolate_rot_y = cs_rot(interpolate_timestep)
            interpolate_dep = cs_dep(interpolate_timestep)

            # Compute the average direction vector of all segments
            segment_vectors = np.diff(cleaned_data, axis=0)
            average_direction = np.mean(segment_vectors, axis=0)
            average_direction /= np.linalg.norm(average_direction)  # Normalize the direction vector

            # Extrapolate based on the average segment direction
            extrapolation_length = int(50 - interpolate_timestep.max())  # number of extra points
            if extrapolation_length > 0:
                extrapolated_timestep = np.arange(interpolate_timestep.max(), 51)
                extrapolated_pos_x = [interpolate_pos_x[-1] + i * average_direction[1] for i in
                                      range(1, extrapolation_length + 1)]
                extrapolated_pos_y = [interpolate_pos_y[-1] + i * average_direction[2] for i in
                                      range(1, extrapolation_length + 1)]
                extrapolated_pos_z = [interpolate_pos_z[-1] + i * average_direction[3] for i in
                                      range(1, extrapolation_length + 1)]
                extrapolated_rot_y = [interpolate_rot_y[-1] + i * average_direction[4] for i in
                                      range(1, extrapolation_length + 1)]
                final_timestep = np.concatenate((interpolate_timestep, extrapolated_timestep))
                final_pos_x = np.concatenate((interpolate_pos_x, extrapolated_pos_x))
                final_pos_y = np.concatenate((interpolate_pos_y, extrapolated_pos_y))
                final_pos_z = np.concatenate((interpolate_pos_z, extrapolated_pos_z))
                final_rot_y = np.concatenate((interpolate_rot_y, extrapolated_rot_y))
            else:
                final_timestep = interpolate_timestep
                final_pos_x = interpolate_pos_x
                final_pos_y = interpolate_pos_y
                final_pos_z = interpolate_pos_z
                final_rot_y = interpolate_rot_y

            data_base_copy[tracking_id]['timestep'] = [int(i) for i in final_timestep]
            data_base_copy[tracking_id]['loc_x'] = final_pos_x.tolist()
            data_base_copy[tracking_id]['loc_y'] = final_pos_y.tolist()
            data_base_copy[tracking_id]['loc_z'] = final_pos_z.tolist()
            data_base_copy[tracking_id]['rot_y'] = final_rot_y.tolist()

            data_base_copy[tracking_id]['interpolate_timestep'] = [int(i) for i in interpolate_timestep]
            data_base_copy[tracking_id]['dep'] = interpolate_dep.tolist()

        data_base = data_base_copy
        return data_base

    def init_ego_base(self, path):
        with open(path, 'r') as file:
            data_dict = yaml.safe_load(file)
        return data_dict

    def tick_spectator(self, trigger_transform, view="top_down_"):
        spectator = self.world.get_spectator()
        if view == 'top_down':
            spector_transform = carla.Transform(trigger_transform.location + carla.Vector3D(0, 0, 100),
                                                carla.Rotation(pitch=-90))
        else:
            try:
                ego_position = self.ego_vehicle.get_transform().location + carla.Vector3D(0, 0, 1.9)
                spector_transform = carla.Transform(location=ego_position,
                                                    rotation=self.ego_vehicle.get_transform().rotation)
            except:
                spector_transform = carla.Transform(trigger_transform.location + carla.Vector3D(0, 0, 50),
                                                    carla.Rotation(pitch=-90))
        spectator.set_transform(spector_transform)

    def spawn_ego(self, bp='vehicle.tesla.model3'):
        # spawn ego
        ego_bp = self.world.get_blueprint_library().find(bp)
        self.start_point.location.z += self.underground_dis
        self.ego_vehicle = self.world.try_spawn_actor(ego_bp, self.start_point)
        self.collision_detector_ego = CollisionDetector(self.ego_vehicle)
        self.rgb_camera_ego = RGBCamera(self.world, self.ego_vehicle, save_dir=self.save_dir + '/' + self.scene_name, data_dump=self.data_dump)
        self.rgb_camera_ego.spawn_sensor()
        control = carla.VehicleControl(throttle=0.2)
        self.ego_vehicle.apply_control(control)
        forward_vector = self.start_point.get_forward_vector()
        velocity_vector = carla.Vector3D(
            x=forward_vector.x * self.ego_speed,
            y=forward_vector.y * self.ego_speed,
            z=0.
        )
        self.ego_vehicle.set_target_velocity(velocity_vector)

    def spawn_shadow_ego(self, bp='vehicle.tesla.model3'):
        ego_bp = self.world.get_blueprint_library().find(bp)
        self.shadow_ego_vehicle = self.world.try_spawn_actor(ego_bp, self.start_point)
        while not self.shadow_ego_vehicle:
            self.start_point.location.z += 0.01
            self.shadow_ego_vehicle = self.world.try_spawn_actor(ego_bp, self.start_point)
        control = carla.VehicleControl(throttle=0.2)
        self.shadow_ego_vehicle.apply_control(control)
        forward_vector = self.start_point.get_forward_vector()
        velocity_vector = carla.Vector3D(
            x=forward_vector.x * self.ego_speed,
            y=forward_vector.y * self.ego_speed,
            z=0.
        )
        self.shadow_ego_vehicle.set_target_velocity(velocity_vector)
        self.shadow_ego_vehicle.set_enable_gravity(False)
        self.start_point.location.z -= self.underground_dis
        self.shadow_ego_vehicle.set_transform(self.start_point)

    def move_ego(self, timestep):
        data_ego = [item for item in self.ego_base if item['timestep'] == timestep][0]
        trans = data_ego['transform']
        ego_transform = carla.Transform(
            location=carla.Location(x=trans[0], y=trans[1], z=trans[2]),
            rotation=carla.Rotation(pitch=trans[3], yaw=trans[4], roll=trans[5]))
        self.ego_vehicle.set_transform(ego_transform)
        collision_occurred = data_ego['collision_occurred']
        if collision_occurred:
            return timestep
        else:
            return 9999

    def tick_shadow_ego_pose(self, timestep):
        data_ego = [item for item in self.ego_base if item['timestep'] == timestep][0]
        trans = data_ego['transform']
        ego_transform = carla.Transform(
            location=carla.Location(x=trans[0], y=trans[1], z=trans[2] - self.underground_dis),
            rotation=carla.Rotation(pitch=trans[3], yaw=trans[4], roll=trans[5]))
        self.shadow_ego_vehicle.set_transform(ego_transform)
        self.yaw_radians = math.radians(self.ego_vehicle.get_transform().rotation.yaw)

    def tick_veh(self, timestep):
        # bgs
        for tracking_id, inst in self.data_base.items():
            if tracking_id == 'ego':
                continue
            if timestep == inst['timestep'][0]:
                cur_timestep = timestep
                cur_index = inst['timestep'].index(cur_timestep)
                cur_loc_x = inst['loc_x'][cur_index]
                cur_loc_y = inst['loc_y'][cur_index]
                cur_loc_z = inst['loc_z'][cur_index]
                cur_rot_y = inst['rot_y'][cur_index]
                ego_t = self.shadow_ego_vehicle.get_transform()
                z = ego_t.location.z + 0.65 + self.underground_dis \
                    if self.data_base[tracking_id]['class'] == 6 \
                    else ego_t.location.z + self.underground_dis
                cur_point = carla.Transform(location=carla.Location(
                    x=ego_t.location.x + cur_loc_x * math.cos(self.yaw_radians) - cur_loc_y * math.sin(
                        self.yaw_radians) * self.dis_scale,
                    y=ego_t.location.y + cur_loc_x * math.sin(self.yaw_radians) + cur_loc_y * math.cos(
                        self.yaw_radians) * self.dis_scale,
                    z=z),
                    rotation=carla.Rotation(roll=0.,
                                            yaw=ego_t.rotation.yaw +
                                                math.degrees(cur_rot_y) + 90,  # +90
                                            pitch=0.))

                # spawn
                inst_class = label_class[self.data_base[tracking_id]['class']]
                inst_bp = self.world.get_blueprint_library().find(random.choice(class_blueprint[inst_class]))
                for i in range(self.max_attempts):
                    ego_vehicle = self.world.try_spawn_actor(inst_bp, cur_point)
                    if ego_vehicle:
                        self.bg_vehicle_managers[tracking_id] = {}
                        bg_vehicle_manager = ego_vehicle
                        self.bg_vehicle_managers[tracking_id]['actor'] = bg_vehicle_manager
                        break
                    else:
                        cur_point.location.z += 0.01
                        if i == self.max_attempts - 1:
                            self.spawn_queue[tracking_id] = {}
                            self.spawn_queue[tracking_id]['inst_bp'] = inst_bp
                            self.spawn_queue[tracking_id]['cur_point'] = cur_point

            elif timestep in inst['timestep']:
                cur_timestep = timestep
                cur_index = inst['timestep'].index(cur_timestep)
                cur_loc_x = inst['loc_x'][cur_index]
                cur_loc_y = inst['loc_y'][cur_index]
                cur_loc_z = inst['loc_z'][cur_index]
                cur_rot_y = inst['rot_y'][cur_index]
                ego_t = self.shadow_ego_vehicle.get_transform()
                z = ego_t.location.z + 0.65 + self.underground_dis \
                    if self.data_base[tracking_id]['class'] == 6 \
                    else ego_t.location.z + self.underground_dis

                cur_point = carla.Transform(location=carla.Location(
                    x=ego_t.location.x + cur_loc_x * math.cos(self.yaw_radians) - cur_loc_y * math.sin(
                        self.yaw_radians) * self.dis_scale,
                    y=ego_t.location.y + cur_loc_x * math.sin(self.yaw_radians) + cur_loc_y * math.cos(
                        self.yaw_radians) * self.dis_scale,
                    z=z),
                    rotation=carla.Rotation(roll=0.,
                                            yaw=ego_t.rotation.yaw +
                                                math.degrees(cur_rot_y) + 90,  # +90
                                            pitch=0.))

                # spawn the un-spawned vehicles
                if tracking_id in self.spawn_queue:
                    spawn_inst = self.spawn_queue[tracking_id]
                    inst_bp = spawn_inst['inst_bp']
                    for i in range(self.max_attempts):
                        ego_vehicle = self.world.try_spawn_actor(inst_bp, cur_point)
                        if ego_vehicle:
                            self.bg_vehicle_managers[tracking_id] = {}
                            bg_vehicle_manager = ego_vehicle
                            self.bg_vehicle_managers[tracking_id]['actor'] = bg_vehicle_manager
                            del self.spawn_queue[tracking_id]
                            break
                        else:
                            cur_point.location.z += 0.01

                # move by request
                try:
                    self.run_obj(self.bg_vehicle_managers[tracking_id], cur_point)
                except:
                    pass
            else:
                # autopilot
                try:
                    self.bg_vehicle_managers[tracking_id]['actor'].set_autopilot(True)
                except:
                    pass

    def run_obj(self, obj, cur_point):
        obj['actor'].set_transform(cur_point)

    def destroy(self):
        for hero in self.bg_vehicle_managers.values():
            hero['actor'].destroy()
        self.bg_vehicle_managers = {}

        if self.ego_vehicle:
            self.ego_vehicle.destroy()
            self.ego_vehicle = None

        if self.shadow_ego_vehicle:
            self.shadow_ego_vehicle.destroy()
            self.shadow_ego_vehicle = None

    def visual_video(self):
        video_path = f'{root_path}/data/videos/{self.scene_name}.mp4'  #### hardcoded, make sure you change it
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"The video from {video_path} cannot be opened!")
            exit()

        delay_per_frame = int(50)  # 5000 ms for 5 seconds
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow(f'{self.scene_name}', frame)
            if cv2.waitKey(delay_per_frame) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    ##################################################################
    #                           RL functions
    ##################################################################

    def new_scenario(self):
        # re-spawn a new scenario
        data_scene = random.choice(self.scene_list)
        self.scene_name = data_scene['id']
        print(f"Loading new scenario {self.scene_name} in {data_scene['town']}...")
        traj_path = f'{root_path}{SEP}data{SEP}trajectories{SEP}default_{self.scene_name}.mp4_results.json'
        self.data_base = self.init_data_base(traj_path)
        ego_path = f"{root_path}{SEP}data{SEP}egos{SEP}{self.scene_name}_{data_scene['town']}.yaml"
        self.ego_base = self.init_ego_base(ego_path)

        # world
        self.world = self.client.load_world(data_scene['town'])
        self.world_settings = self.world.get_settings()
        self.world_settings.synchronous_mode = self.config['world']['synchronous_mode']
        self.world_settings.fixed_delta_seconds = self.config['world']['fixed_delta_seconds']
        self.world_settings.no_rendering_mode = self.config['world']['no_rendering_mode']
        self.world_settings.quality_level = self.config['world']['quality_level']
        self.world.apply_settings(self.world_settings)

        # ego initials
        start_location, start_rotation = data_scene['start_location'], data_scene['start_rotation']
        self.start_point = self.original_start_point = carla.Transform(
            location=carla.Location(x=start_location[0], y=start_location[1], z=start_location[2]),
            rotation=carla.Rotation(pitch=start_rotation[0], yaw=start_rotation[1], roll=start_rotation[2]))
        end_location, end_rotation = data_scene['end_location'], data_scene['end_rotation']
        self.end_point = self.original_end_point = carla.Transform(
            location=carla.Location(x=end_location[0], y=end_location[1], z=end_location[2]),
            rotation=carla.Rotation(pitch=end_rotation[0], yaw=end_rotation[1], roll=end_rotation[2]))
        self.ego_speed = data_scene['speed']

        # others
        self.spawn_queue = {}  # temp trajectories

        # ego and shadow
        self.spawn_shadow_ego()
        self.spawn_ego()

    def old_scenario(self):
        print(f"Resetting old scenario {self.scene_name}...")
        # reset the same scenario if the agent failed in the last one
        # make sure destroy the actors first
        self.spawn_shadow_ego()
        self.spawn_ego()

        # reset ego initials
        self.start_point = self.original_start_point
        self.end_point = self.original_end_point

        # others
        self.spawn_queue = {}

    def reset(self, is_training=False):
        if not self.world:  # initialize
            self.new_scenario()
        else:
            self.destroy()
            if self._collided:
                self.new_scenario()################                     self.old_scenario()
            elif self.done:
                self.new_scenario()
            else:
                self.new_scenario()

        # reset dynamic RL settings
        self.last_reward = 0.
        self.total_reward = 0.
        self.done = 0
        self.timestep = 1

        self.observation = self._get_observation()
        return self.observation

    def step(self, action):
        self.tick_shadow_ego_pose(self.timestep)
        self.tick_veh(self.timestep)
        self.tick_spectator(self.ego_vehicle.get_transform())

        self.sim_end = self.move_ego(self.timestep)
        steer, throttle, brake = [float(a) for a in action]
        self.ego_control.steer = smooth_action(self.ego_control.steer, steer, self.action_smoothing)
        self.ego_control.throttle = smooth_action(self.ego_control.throttle, throttle, self.action_smoothing)
        self.ego_control.brake = smooth_action(self.ego_control.brake, brake, self.action_smoothing)
        self.ego_vehicle.apply_control(self.ego_control)

        # world tick
        self.world.tick()

        # end criteria
        # if collided because of driver's misbehavior or not taking any action
        if self._collided():
            self.reset()
        else:
            if self.timestep > self.sim_end or self.timestep >= 49:
                self.done = 1
                self.reset()
            else:
                self.timestep += 1
            time.sleep(0.1)

        # dynamic update
        self.observation = self._get_observation()
        self.last_reward = 0
        info = {}
        return self.observation, self.last_reward, self.done, info

    def _get_observation(self):
        save_dir = None  # f'data/rgb/{self.scene_name}'
        front_rgb_camera = self.rgb_camera_ego
        obs = front_rgb_camera.get_last_data()
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)

            # 构造文件名：带时间戳或帧号
            filename = f"{self.timestep:02d}.png"
            save_path = os.path.join(save_dir, filename)

            # 如果 obs 是 numpy 格式，用 cv2 保存
            cv2.imwrite(save_path, cv2.cvtColor(obs.astype('uint8'), cv2.COLOR_RGB2BGR))
        return {'rgb_camera': obs}

    def _collided(self):
        return self.collision_detector_ego.collision_occurred

    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        return [seed]

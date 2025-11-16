"""
    @Author: Yansong Qu
    @Date: 2025 Oct 26
    @Description:
        The main file to launch the video replay function.
"""

import random
import carla
import argparse
import yaml
import os
import time
import subprocess
import sys
from stable_baselines3 import PPO, DDPG, SAC


# Assuming this script is somewhere within the project directory
root_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(root_path)

from RLEnv import ReplayManager as ScenarioManager

argparser = argparse.ArgumentParser()
argparser.add_argument(
    '-cb', '--config_base',
    default=f'{root_path}/config_yaml/base_config.yaml',
    type=str,
    help='the path of config_base')
argparser.add_argument(
    '-dw', '--dynamic_weather',
    default=False,
    type=bool,
    help='The modified param: dynamic_weather')
argparser.add_argument(
    '-dd', '--data_dump',
    default=False,
    type=bool,
    help='The modified param: data_dump')
argparser.add_argument(
    '-sc', '--scene',
    default='all&video&manipulate',  # '000014,000018,000024,000028,000031'
    type=str,
    help='The modified param: data_dump')
argparser.add_argument(
    '-cr', '--CARLA_ROOT',
    default='/home/ai/qys/softwares/CARLA_0.9.15/',
    type=str,
    help='CARLA ROOT PATH')
args = argparser.parse_args()

SEP = os.sep
START_POINT_TYPES = {'straight': 1, 'intersection':2, 'long_left_turn': 3, 'long_right_turn': 4}
TURN_IN_INTERSECTION = {'left': 1, 'right':2}


def kill_process_on_port(port):
    result = subprocess.run(['lsof', '-ti', f':{port}'], stdout=subprocess.PIPE)
    pids = result.stdout.decode().splitlines()
    for pid in pids:
        os.system(f"kill -9 {pid}")


if __name__ == '__main__':
    if args.CARLA_ROOT:
        os.environ['CARLA_ROOT'] = args.CARLA_ROOT
    else:
        print('You did not specify the CARLA_ROOT, please launch the CARLA first, or specify it in command line.')
        exit()
    carla_path = os.path.join(os.environ["CARLA_ROOT"], "CarlaUE4.sh")
    launch_command = [carla_path]
    # For unknown reason, we have to use high-quality render, or else the following error will occur
    # Process finished with exit code 134 (interrupted by signal 6: SIGABRT)
    # launch_command += ['-quality-level=Low']
    launch_command += ["-fps=%i" % 10]
    launch_command += ['-prefernvidia']
    # launch_command += ['-RenderOffScreen']
    print("Running command:")
    print(" ".join(launch_command))
    carla_process = subprocess.Popen(launch_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("Waiting for CARLA to initialize\n")
    time.sleep(15)

    # config
    with open(args.config_base, 'r') as f_base:
        config_base = yaml.safe_load(f_base)
    try:
        with open(config_base['sensor_config'], 'r') as f_sensor:
            config_sensor = yaml.safe_load(f_sensor)
    except:
        raise RuntimeError('Open sensor config failed!')
    config = {**config_base, **config_sensor}

    if not os.path.exists(config['output_path']):
        os.makedirs(config['output_path'])

    # decode the scene order
    # if scene == 'all', we select all scenes from a txt file, this will also enter a scene reselection mode.
    if 'all' in args.scene:
        with open(f'{root_path}{SEP}data{SEP}output_final2.yaml', 'r', encoding='utf-8') as file:
            scene_list = yaml.safe_load(file)
            print(f'Number {len(scene_list)} in total!')
            # random.shuffle(scene_list)
    flag_video = False
    if 'video' in args.scene:
        flag_video = True

    client = carla.Client('localhost', 2000)
    client.set_timeout(50)

    config['scenario']['dynamic_weather'] = args.dynamic_weather
    config['data_dump'] = args.data_dump

    # scenario running
    scenario_manager = ScenarioManager(client, scene_list, config)

    # rl
    from utils import lr_schedule
    from utils import HParamCallback, TensorboardCallback, write_json, parse_wrapper_class
    from stable_baselines3.common.callbacks import CheckpointCallback
    import torch
    algorithm_params = {
        "PPO": dict(
            learning_rate=lr_schedule(1e-4, 1e-6, 2),
            gamma=0.98,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.05,
            n_epochs=10,
            n_steps=1024,
            policy_kwargs=dict(activation_fn=torch.nn.ReLU,
                               net_arch=[dict(pi=[500, 300], vf=[500, 300])]))}
    CONFIG = {
        "algorithm": "PPO",
        "algorithm_params": algorithm_params["PPO"],
        "vae_model": "vae_64",
        "action_smoothing": 0.75,
        "reward_fn": "reward_clip",
        "obs_res": (160, 80),
        "seed": 100,
        "wrappers": []
    }
    algorithm_dict = {"PPO": PPO, "DDPG": DDPG, "SAC": SAC}
    AlgorithmRL = algorithm_dict[CONFIG["algorithm"]]
    total_timesteps = 1_000_000
    num_checkpoints = 10
    model_dir = '/home/ai/qys/projects/videoscg/output'
    model = AlgorithmRL('MultiInputPolicy', scenario_manager, verbose=1, seed=42, device='cuda',
                        **CONFIG["algorithm_params"])
    model.learn(total_timesteps=total_timesteps,
                callback=[HParamCallback(CONFIG), TensorboardCallback(1), CheckpointCallback(
                    save_freq=total_timesteps // num_checkpoints,
                    save_path=model_dir,
                    name_prefix="model")], reset_num_timesteps=False)

    if carla_process:
        carla_process.terminate()
        kill_process_on_port(2000)





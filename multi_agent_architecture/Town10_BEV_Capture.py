#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file captures a single bird's-eye image in CARLA from a top-down RGB camera.
本文件在 CARLA 中从BEV视角 RGB 相机采集一张鸟瞰图。
1. Start CARLA
2. Change the map name in CONFIG if you want to use a different map (default: town10hd_opt)
"""

# -----------------------------
# Config
# -----------------------------
import os
import time
import pathlib
from datetime import datetime
import threading
import carla

CONFIG = {
    "carla": {
        "host": os.getenv("CARLA_HOST", "localhost"),
        "port": int(os.getenv("CARLA_PORT", "2000")),
        "timeout_sec": float(os.getenv("CARLA_TIMEOUT", "10.0")),
        "town_map": os.getenv("CARLA_TOWN", "Town10HD_Opt"),  # change different map: "Town10HD_Opt"
        "use_sync_mode": False,  # set True if you prefer deterministic frame capture /
    },
    "camera": {
        # Camera physical placement / 相机外参：顶视角鸟瞰
        "transform": {
            "location": {"x": 0.0, "y": 30.0, "z": 160.0},
            "rotation": {"pitch": -90.0, "yaw": 0.0, "roll": 0.0},
        },
        # Camera intrinsics / 相机内参
        "image_size_x": int(os.getenv("IMG_W", "1920")),
        "image_size_y": int(os.getenv("IMG_H", "1080")),
        "fov": float(os.getenv("IMG_FOV", "90.0")),  # degrees
        "sensor_id": "sensor.camera.rgb",  # blueprint id
    },
    "output": {
        "dir": os.getenv("OUTPUT_DIR", "output"),
        "filename_pattern": "town10hd_birdseye_{ts}.png",  # {ts} will be replaced by timestamp / {ts} 将替换为时间戳
        "overwrite_single": False,  # True -> fixed name; False -> timestamped / True 固定文件名，False 时间戳文件名
    },
    "debug": {
        "print_camera_spawn": True,
    },
}

# -----------------------------
# Utilities
# -----------------------------
def ensure_dir(dir_path: str) -> None:
    """
    Ensure output directory exists.
    确保输出目录存在。
    """
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def timestamp_str() -> str:
    """
    Get a compact timestamp string.
    获取时间戳。
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def build_output_path(dir_path: str, pattern: str, overwrite_single: bool) -> str:
    """
    Build final output file path.

    Args:
        dir_path (str): Directory to save / 保存目录
        pattern (str): Pattern with optional {ts} / 可包含 {ts} 的模板
        overwrite_single (bool): Whether to overwrite a single fixed name / 是否使用固定文件名覆盖

    Returns:
        str: Absolute path

    Example:
        # returns ".../output/town10hd_birdseye_2025-10-30_12-00-00.png"
    """
    if overwrite_single:
        filename = pattern.replace("{ts}", "single")
    else:
        filename = pattern.replace("{ts}", timestamp_str())
    return str(pathlib.Path(dir_path) / filename)


def log_info(*args):
    """
    Lightweight logger info; replace with logging in production.
    """
    print("[INFO ]", *args)


def log_warn(*args):
    """
    Lightweight logger warn.
    """
    print("[WARN ]", *args)


def log_error(*args):
    """
    Lightweight logger error.
    """
    print("[ERROR]", *args)


# -----------------------------
# CARLA Helpers
# -----------------------------
def connect_client(host: str, port: int, timeout_sec: float) -> carla.Client:
    """
    Create and configure a CARLA client.
    创建并配置 CARLA 客户端。

    Args:
        host (str): CARLA host / 主机名
        port (int): CARLA port / 端口
        timeout_sec (float): Request timeout / 请求超时（秒）

    Returns:
        carla.Client: Connected client / 已连接客户端

    Example:
        client = connect_client('localhost', 2000, 10.0)
    """
    client = carla.Client(host, port)
    client.set_timeout(timeout_sec)
    return client


def load_town(client: carla.Client, town_map: str) -> carla.World:
    """
    Load a specific town synchronously.
    同步加载指定地图。

    Args:
        client (carla.Client): CARLA client / 客户端
        town_map (str): e.g., "Town10HD_Opt"

    Returns:
        carla.World: World of the loaded map / 已加载地图的世界对象
    """
    client.load_world(town_map)
    world = client.get_world()
    return world


def set_sync_mode(world: carla.World, enable: bool) -> dict:
    """
    Optionally enable synchronous mode; returns previous settings to restore.
    可选开启同步模式；返回旧设置以便恢复。

    Args:
        world (carla.World): The world / 世界对象
        enable (bool): True to enable / True 启用

    Returns:
        dict: Previous settings snapshot / 旧设置快照
    """
    settings = world.get_settings()
    prev = {
        "synchronous_mode": settings.synchronous_mode,
        "fixed_delta_seconds": settings.fixed_delta_seconds,
    }
    if enable:
        settings.synchronous_mode = True
        if not settings.fixed_delta_seconds:
            settings.fixed_delta_seconds = 1.0 / 20.0  # 20 FPS as a safe default
        world.apply_settings(settings)
    return prev


def restore_settings(world: carla.World, prev: dict) -> None:
    """
    Restore world settings to previous snapshot.
    恢复世界设置到之前的快照。
    """
    settings = world.get_settings()
    settings.synchronous_mode = prev.get("synchronous_mode", False)
    settings.fixed_delta_seconds = prev.get("fixed_delta_seconds", None)
    world.apply_settings(settings)


def make_camera_blueprint(world: carla.World) -> carla.ActorBlueprint:
    """
    Create and configure the RGB camera blueprint from CONFIG.
    根据 CONFIG 创建并配置 RGB 相机蓝图。

    Returns:
        carla.ActorBlueprint: Configured camera blueprint
    """
    bp_lib = world.get_blueprint_library()
    camera_bp = bp_lib.find(CONFIG["camera"]["sensor_id"])
    camera_bp.set_attribute("image_size_x", str(CONFIG["camera"]["image_size_x"]))
    camera_bp.set_attribute("image_size_y", str(CONFIG["camera"]["image_size_y"]))
    camera_bp.set_attribute("fov", str(CONFIG["camera"]["fov"]))
    if camera_bp.has_attribute("motion_blur_intensity"):
        camera_bp.set_attribute("motion_blur_intensity", "0.0")
    if camera_bp.has_attribute("shutter_speed"):
        camera_bp.set_attribute("shutter_speed", "1.0")
    return camera_bp


def camera_transform_from_config() -> carla.Transform:
    """
    Build camera transform from CONFIG.
    从 CONFIG 构建相机位姿。
    """
    loc = CONFIG["camera"]["transform"]["location"]
    rot = CONFIG["camera"]["transform"]["rotation"]
    return carla.Transform(
        carla.Location(x=loc["x"], y=loc["y"], z=loc["z"]),
        carla.Rotation(pitch=rot["pitch"], yaw=rot["yaw"], roll=rot["roll"]),
    )


# -----------------------------
# Capture
# -----------------------------
def save_image_to_disk(image: carla.Image, output_path: str) -> None:
    """
    Save a CARLA image to disk
    将 CARLA 图像保存到磁盘

    Args:
        image (carla.Image): Image object from sensor / 传感器图像
        output_path (str): Absolute file path / 绝对输出路径

    Example:
        save_image_to_disk(image, '/tmp/bird.png')
    """
    image.save_to_disk(output_path)


def listen_and_capture_one_frame(camera: carla.Sensor, output_path: str, done_event: threading.Event) -> None:
    """
    Listen the camera stream and save the first received frame, then stop.

    Args:
        camera (carla.Sensor): Spawned camera actor / 已创建的相机
        output_path (str): Save path / 保存路径
        done_event (threading.Event): Completion flag / 完成事件
    """
    has_saved = {"value": False}

    def _callback(image: carla.Image):
        if not has_saved["value"]:
            try:
                save_image_to_disk(image, output_path)
                log_info(f"Image saved -> {output_path}")
                has_saved["value"] = True
            except Exception as e:
                log_error("Failed to save image:", e)
            finally:
                # Stop sensor stream and signal done.
                # 停止传感器流并发出完成信号。
                try:
                    camera.stop()
                except Exception as e:
                    log_warn("Camera stop exception:", e)
                done_event.set()

    camera.listen(_callback)


def spawn_camera(world: carla.World) -> carla.Sensor:
    """
    Spawn the configured camera at the given transform.
    在给定位姿生成已配置相机。

    Returns:
        carla.Sensor: The spawned camera actor / 生成的相机 Actor
    """
    camera_bp = make_camera_blueprint(world)
    transform = camera_transform_from_config()
    camera = world.spawn_actor(camera_bp, transform)
    if CONFIG["debug"]["print_camera_spawn"]:
        log_info("Camera spawned at:", transform)
    return camera


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    """
    Bootstraps CARLA client, loads map, spawns a top-down camera, captures one frame, and cleans up.
    """
    client = None
    world = None
    camera = None
    prev_settings = None
    done = threading.Event()

    try:
        # 1) Connect & load / 连接与载图
        client = connect_client(
            CONFIG["carla"]["host"], CONFIG["carla"]["port"], CONFIG["carla"]["timeout_sec"]
        )
        world = load_town(client, CONFIG["carla"]["town_map"])

        prev_settings = set_sync_mode(world, CONFIG["carla"]["use_sync_mode"])

        # 3) Prepare output / 准备输出
        ensure_dir(CONFIG["output"]["dir"])
        output_path = build_output_path(
            CONFIG["output"]["dir"],
            CONFIG["output"]["filename_pattern"],
            CONFIG["output"]["overwrite_single"],
        )

        # 4) Spawn camera & listen / 创建相机并监听一帧
        camera = spawn_camera(world)
        listen_and_capture_one_frame(camera, output_path, done_event=done)

        # 5) Tick or sleep until done / 同步 tick 或睡眠等待完成
        if CONFIG["carla"]["use_sync_mode"]:
            # Tick a few frames until the callback signals completion.
            for _ in range(200):  # up to ~10s at 20 FPS / 约 10 秒
                if done.is_set():
                    break
                world.tick()
                time.sleep(0.0)
        else:
            done.wait(timeout=10.0)

        if not done.is_set():
            log_warn("No frame captured within timeout window.")

    except Exception as e:
        log_error("Unhandled exception:", e)

    finally:
        try:
            if camera is not None:
                camera.stop()
                camera.destroy()
                log_info("Camera destroyed.")
        except Exception as e:
            log_warn("Camera destruction exception:", e)

        try:
            if world is not None and prev_settings is not None:
                restore_settings(world, prev_settings)
        except Exception as e:
            log_warn("World settings restore exception:", e)


if __name__ == "__main__":
    main()

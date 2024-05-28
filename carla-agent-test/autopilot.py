import carla
import random
import pygame
import datetime as dt
import numpy as np
import cv2
import csv
import time
import json

class CarlaSimulation:
    """
    Class to handle the Carla simulation environment.
    """

    def __init__(self):
        """
        Initialize the Carla simulation environment.
        """
        self.client = carla.Client('3.110.131.43', 2000)
        self.world = self.client.load_world('Town05')
        self.setup_environment()
        self.setup_ego_vehicle()
        self.setup_camera()
        self.autopilot_enabled = False

    def setup_environment(self):
        """
        Set up the simulation environment with weather conditions.
        """
        weather = carla.WeatherParameters(
            cloudiness=0.0,
            precipitation=0.0,
            sun_altitude_angle=10.0,
            sun_azimuth_angle=70.0,
            precipitation_deposits=0.0,
            wind_intensity=0.0,
            fog_density=0.0,
            wetness=0.0,
        )
        self.world.set_weather(weather)

    def setup_ego_vehicle(self):
        """
        Spawn the ego vehicle and additional vehicles.
        """
        bp_lib = self.world.get_blueprint_library()
        spawn_points = self.world.get_map().get_spawn_points()

        vehicle_bp = bp_lib.find('vehicle.audi.etron')
        self.ego_vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_points[79])

        for _ in range(50):
            vehicle_bp = random.choice(bp_lib.filter('vehicle'))
            npc = self.world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))
            if npc is not None:
                npc.set_autopilot(True)

    def setup_camera(self):
        """
        Set up the RGB camera sensor for the ego vehicle.
        """
        bp_lib = self.world.get_blueprint_library()
        camera_bp = bp_lib.find('sensor.camera.rgb')
        camera_init_trans = carla.Transform(carla.Location(x=2.0, z=1.4), carla.Rotation(pitch=0.0))
        self.camera = self.world.spawn_actor(camera_bp, camera_init_trans, attach_to=self.ego_vehicle)
        self.camera.listen(lambda image: self.rgb_callback(image))

    def rgb_callback(self, image):
        """
        Callback function for the RGB camera sensor.
        """
        sensor_data = {
            'rgb_image': 'image_%06d.jpg' % image.frame,
            'angle': self.ego_vehicle.get_control().steer,
            'throttle': self.ego_vehicle.get_control().throttle
        }
        image_name = 'image_%06d.jpg' % image.frame
        image.save_to_disk(f'/app/carla-output/images/{image_name}')
        print(sensor_data)

    def enable_autopilot(self):
        """
        Enable the autopilot mode for the ego vehicle.
        """
        self.ego_vehicle.set_autopilot(True)
        self.autopilot_enabled = True

    def run_simulation(self, duration=10):
        """
        Run the Carla simulation for a specified duration.
        """
        start_time = time.time()
        spectator = self.world.get_spectator()

        while time.time() - start_time < duration:
            self.world.tick()
            transform = self.ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform.location + carla.Location(x=-0, y=-2,z=2), carla.Rotation(pitch=-15, yaw=transform.rotation.yaw)))

if __name__ == "__main__":
    now = dt.datetime.now()
    date_string = now.strftime("%d%m%Y-%H%M")

    simulation = CarlaSimulation()
    simulation.enable_autopilot()
    simulation.run_simulation()
import carla
import random
import datetime as dt
import time

class CarlaSimulation:
    def __init__(self):
        self.client = carla.Client('65.1.109.59', 2000)
        self.world = self.client.load_world('Town03')
        self.setup_environment()
        self.setup_ego_vehicle()
        self.setup_camera()
        self.autopilot_enabled = False

    def setup_environment(self):
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
        bp_lib = self.world.get_blueprint_library()
        spawn_points = self.world.get_map().get_spawn_points()

        vehicle_bp = bp_lib.filter('vehicle.audi.etron')[0]
        vehicle_bp.set_attribute('role_name', 'ego')
        color = vehicle_bp.get_attribute('color').recommended_values[0]
        vehicle_bp.set_attribute('color', '255,0,0')  # Set ego vehicle color to red
        self.ego_vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_points[79])

        for _ in range(100):
            vehicle_bp = random.choice(bp_lib.filter('vehicle'))
            npc = self.world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))
            if npc is not None:
                npc.set_autopilot(True)

    def setup_camera(self):
        bp_lib = self.world.get_blueprint_library()
        camera_bp = bp_lib.find('sensor.camera.rgb')
        camera_init_trans = carla.Transform(carla.Location(x=-0, y=-0, z=2), carla.Rotation(pitch=5))
        self.camera = self.world.spawn_actor(camera_bp, camera_init_trans, attach_to=self.ego_vehicle)
        self.camera.listen(lambda image: self.rgb_callback(image))

    def rgb_callback(self, image):
        image_name = 'image_%06d.jpg' % image.frame
        image.save_to_disk(f'/app/carla-output/images/{image_name}')

    def enable_autopilot(self):
        self.ego_vehicle.set_autopilot(True)
        self.autopilot_enabled = True

    def run_simulation(self, duration=10):
        start_time = time.time()
        spectator = self.world.get_spectator()

        while time.time() - start_time < duration:
            self.world.tick()
            transform = self.ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(transform.location + carla.Location(x=-0, y=-1, z=2), carla.Rotation(pitch=-15, yaw=transform.rotation.yaw)))

if __name__ == "__main__":
    simulation = CarlaSimulation()
    simulation.enable_autopilot()
    simulation.run_simulation()
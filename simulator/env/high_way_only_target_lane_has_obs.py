from highway_env.envs.highway_env import HighwayEnv
from gym.envs.registration import register
from highway_env import utils
from highway_env.utils import near_split
import numpy as np


class OnlyTargetLaneHasObsHighWayEnv(HighwayEnv):
    @classmethod
    def default_config(cls) -> dict:
        config = super().default_config()
        config.update({
            "observation": {
                "type": "Kinematics"
            },
            ''
            "action": {
                "type": "DiscreteMetaAction",
            },
            "other_vehicle_lane_id": 1,
            "lanes_count": 8,
            "vehicles_count": 50,
            "controlled_vehicles": 1,
            "initial_lane_id": None,
            "duration": 40,  # [s]
            "ego_spacing": 2,
            "vehicles_density": 1,
            # The reward received when colliding with a vehicle.
            "collision_reward": -1,
            "reward_speed_range": [20, 30],
            "offroad_terminal": False,
            "average_vehilve_distance": 20,
        })
        return config

    def _create_vehicles(self) -> None:
        """Create some new random vehicles of a given type,
        and add them on the road."""
        other_vehicles_type = utils.class_from_path(
            self.config["other_vehicles_type"])
        other_per_controlled = near_split(
            self.config["vehicles_count"],
            num_bins=self.config["controlled_vehicles"])

        self.controlled_vehicles = []
        for others in other_per_controlled:
            controlled_vehicle = self.action_type.vehicle_class.create_random(
                self.road,
                speed=np.random.uniform(0, 30),
                lane_id=self.config["initial_lane_id"],
                spacing=self.config["ego_spacing"])
            self.controlled_vehicles.append(controlled_vehicle)
            self.road.vehicles.append(controlled_vehicle)
            rear_pos = controlled_vehicle.destination[0] - \
                self.config['average_vehilve_distance']*others/2
            for i in range(others):
                self.road.vehicles.append(
                    other_vehicles_type.make_on_lane(
                        self.road,
                        ['0', '1', self.config["other_vehicle_lane_id"]],
                        longitudinal=rear_pos +
                        i * self.config['average_vehilve_distance'] +
                        np.random.uniform(
                            (-self.config['average_vehilve_distance'] / 2 + 3,
                             self.config['average_vehilve_distance'] / 2 - 3)),
                        speed=15 + np.random.uniform(-4, 4)))


register(
    id='highway-only-target-lane-has-obs-v0',
    entry_point='highway_env.envs:OnlyTargetLaneHasObsHighWayEnv',
)

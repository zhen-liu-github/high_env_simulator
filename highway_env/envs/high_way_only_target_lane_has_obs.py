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
    def _is_terminal(self) -> bool:
        """The episode is over if the ego vehicle crashed or the time is out."""
        return self.vehicle.position[1]>=3.8 or self.vehicle.crashed or \
            self.steps >= self.config["duration"] or \
            (self.config["offroad_terminal"] and not self.vehicle.on_road)
    def _create_vehicles(self) -> None:
        """Create some new random vehicles of a given type, and add them on the road."""
        other_vehicles_type = utils.class_from_path(
            self.config["other_vehicles_type"])
        other_per_controlled = near_split(
            self.config["vehicles_count"],
            num_bins=self.config["controlled_vehicles"])

        self.controlled_vehicles = []
        distance = np.random.uniform(15, 25)
        # Sample ego velocity from a t distribution with df=15.
        ego_speed = np.random.chisquare(15, 1)[0]
        for others in other_per_controlled:
            controlled_vehicle = self.action_type.vehicle_class.create_random(
                self.road,
                speed = ego_speed,
                # speed=25 + np.random.rand(1)[0]*10,
                # speed=25,
                lane_id=self.config["initial_lane_id"],
                spacing=self.config["ego_spacing"])
            self.controlled_vehicles.append(controlled_vehicle)
            self.road.vehicles.append(controlled_vehicle)
            rear_pos = controlled_vehicle.destination[0] - \
                distance * others / 2
            # Sample obs_speed from t distribution.
            obs_speed = np.random.chisquare(15, 1)[0]
            obs_scale = obs_speed**0.5
            for i in range(others):
                # Sample velocity for obs i.
                obs_speed_i = np.random.normal(loc=obs_speed, scale=obs_scale, size=1)[0]
                self.road.vehicles.append(
                    other_vehicles_type.make_on_lane(
                        self.road,
                        ['0', '1', self.config["other_vehicle_lane_id"]],
                        longitudinal=rear_pos +
                        i * distance +
                        np.random.uniform(
                            (-distance / 2 + 3,
                             distance / 2 - 3)),
                        speed=obs_speed_i))


register(
    id='highway-only-target-lane-has-obs-v0',
    entry_point='highway_env.envs:OnlyTargetLaneHasObsHighWayEnv',
)


vehicle_config = {}
method_config = {
    # "type": "rule_based",

}
env_config = {
    "id": "highway-only-target-lane-has-obs-v0",
    # "id":  "highway-v0",
    # "import_module": "high_way_only_target_lane_has_obs",
    "show_trajectories": True,
    "lanes_count": 2,
    "action": {
        "type": "DiscreteMetaAction",
    },
    "observation": {
        "type": "Kinematics",
        "vehicles_count": 20,
        "features": ["presence", "x", "y", "vx", "vy", "cos_h", "sin_h"],
        "normalize": False,
        "absolute": True,
        "order": "sorted",
        "x": [-100, 100],
        "y": [-100, 100],
        "vx": [-20, 20],
        "vy": [-20, 20],
        "clip": False,
    },
    "simulation_frequency": 10,
    "policy_frequency": 10,
    "duration": 200,
    "initial_lane_id": 0,
    "screen_width": 2000,
    "screen_height": 600,
    "vehicles_count": 10,
    "other_vehicles_type": "highway_env.vehicle.behavior.IDMVehicle",
    "centering_position": [0.3, 0.5],
    "other_vehicle_lane_id": 1,
    "average_vehilve_distance": 20,
    "ego_min_a": -5,
    "ego_max_a": 5,
    "vehicle_min_a": -5,
    "vehicle_max_a": 5,
    "T_react": 0.1,

}
exp_config = {
    "episodes": 200,
    "run_dictory": './exp/',

}


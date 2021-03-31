import sys
import os

path = sys.argv[0]
vehicle_config = {}
model_config = {
    "data_save_path":
    'simulator/data/',
    "type":
    "rule-based",
    "model_path":
    os.path.join('/'.join(path.split('/')[:-1]), 'models', 'saved_model',
                 'saved_model'),
    "data-driven": {
        "feature_index": {
            "x": 1,
            "y": 2,
            "vx": 3,
            "vy": 4,
            "cos_h": 5,
            "sin_h": 6,
        },
        "multi-window-display": True,
    },
    "rule-based": {}
}
env_config = {
    "id": "highway-only-target-lane-has-obs-v0",
    # "id":  "highway-v0",
    # "import_module": "high_way_only_target_lane_has_obs",
    "show_trajectories": True,
    "lanes_count": 2,
    "ego_car": {
        "length": 5,
        "width": 2,
    },
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
    "simulation_frequency": 50,
    "policy_frequency": 50,
    "duration": 500,
    "initial_lane_id": 0,
    "screen_width": 2000,
    "screen_height": 800,
    "vehicles_count": 10,
    "other_vehicles_type": "highway_env.vehicle.behavior.IDMVehicle",
    "centering_position": [0.3, 0.5],
    "other_vehicle_lane_id": 1,
    "average_vehicle_distance": 15,
    "ego_min_a": -5,
    "ego_max_a": 5,
    "vehicle_min_a": -5,
    "vehicle_max_a": 5,
    "T_react": 0.3,
}
exp_config = {
    "episodes": 200,
    "run_dictory": './exp/',
}

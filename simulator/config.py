
vehicle_config = {}
env_config = {
    "id": "highway-only-target-lane-has-obs-v0",
    # "id":  "highway-v0",
    # "import_module": "high_way_only_target_lane_has_obs",
    "show_trajectories": False,
    "lanes_count": 2,
    "action": {
        "type": "ContinuousAction",
        "steering_range": [-0.1, 0.1],
    },
    "observation": {
        "type": "Kinematics",
        "vehicles_count": 20,
        "features": ["presence", "x", "y", "vx", "vy", "cos_h", "sin_h"],
        "normalize": False,
        "order": "sorted",
        "x": [-100, 100],
        "y": [-100, 100],
        "vx": [-20, 20],
        "vy": [-20, 20]
    },
    "simulation_frequency": 30,
    "policy_frequency": 10,
    "duration": 100,
    "initial_lane_id": 0,
    "screen_width": 1200,
    "screen_height": 800,
    "vehicles_count": 20,
    "other_vehicles_type": "highway_env.vehicle.behavior.IDMVehicle",
    "centering_position": [0.3, 0.5],
    "other_vehicle_lane_id": 1,
    "average_vehilve_distance": 20,
    
}
exp_config = {
    "episodes": 200,
    "run_dictory": './exp/',

}


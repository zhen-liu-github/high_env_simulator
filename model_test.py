from highway_env.vehicle.behavior import IDMVehicle
from simulator.config import env_config, method_config

if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()

    solver = TimeOptimalSolver(None)

    simulator = simulator(env, solver, 200, True)
    simulator.simulate()
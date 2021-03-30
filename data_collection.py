import argparse

from rl_agents.agents.common.factory import load_environment
from simulator.config import env_config, model_config
from simulator.simulator import simulator
from simulator.solver import solver_config


parser = argparse.ArgumentParser()
parser.add_argument('--type', default='rule-based')
args = parser.parse_args()
if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()
    # method = 'data-driven'
    model_config.update({'type': args.type})
    solver = solver_config[args.type](model_config, None)

    simulator = simulator(env, solver, 200, True)
    simulator.simulate()

import argparse

from rl_agents.agents.common.factory import load_environment

from simulator.config import env_config, model_config
from simulator.simulator import simulator
from simulator.solver import solver_config

parser = argparse.ArgumentParser()
parser.add_argument('--type', default='rule-based')
parser.add_argument('--display_env', action='store_true')
parser.add_argument('--if_render', action='store_true')
parser.add_argument('--draw_v_fig', action='store_true')
args = parser.parse_args()
if __name__ == '__main__':
    env = load_environment(env_config)
    # unknown reason, cannot load config from env_config.
    env.configure(env_config)
    env.reset()
    # method = 'data-driven'
    model_config.update({
        'type': args.type,
        'display_env': args.display_env,
        'if_render': args.if_render,
        'draw_v_fig': args.draw_v_fig,
    })
    solver = solver_config[args.type](model_config, None)

    simulator = simulator(env,
                          solver,
                          0,
                          seed=None,
                          begin_episode=0,
                          display_env=True,
                          if_render=model_config['if_render'],
                          draw_v_fig=model_config['draw_v_fig'],
                          save_data=model_config['display_env'])
    simulator.simulate()

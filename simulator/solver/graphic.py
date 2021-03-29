import numpy as np
from matplotlib import pyplot as plt, gridspec as gridspec
import seaborn as sns
import matplotlib as mpl
import matplotlib.cm as cm

from rl_agents.utils import remap, constrain

from simulator.config import model_config

import pygame


class SolverGraphic(object):
    """
        Graphical visualization of the Solver.
    """
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    MIN_ATTENTION = 0.01

    @classmethod
    def display(cls, solver, surface, sim_surface=None, display_text=True):
        """
            Display the action-values for the current state
        :param solver: the solver
        :param surface: the pygame surface on which the agent is displayed
        :param sim_surface: the pygame surface on which the env is rendered
        :param display_text: whether to display the window values as text
        """
        target_window = solver.target_window
        front = (
            target_window.front_s - sim_surface.origin[0]
        ) * sim_surface.scaling if target_window.front_is_valid else surface.get_width(
        )
        rear = (target_window.rear_s - sim_surface.origin[0]
                ) * sim_surface.scaling if target_window.rear_is_valid else 0
        cell_size = (front - rear, surface.get_height())
        pygame.draw.rect(surface, cls.BLACK,
                         (0, 0, surface.get_width(), surface.get_height()), 0)
        window_rear_list = []
        if solver.model_config['type'] == 'data-driven' and solver.model_config[
                'data-driven']['multi-window-display']:
            # Draw all lane change window.
            for index, window in enumerate(solver.window_list):
                cls.DrawWindow(window, cls.BLUE, surface, sim_surface)
            # Draw target window.
            cmap = cm.jet_r
            norm = mpl.colors.Normalize(vmin=0, vmax=1 / (1 - 0.5))
            color = cmap(norm(0.5), bytes=True)
            cls.DrawWindow(solver.target_window, color, surface, sim_surface)
            # Display all window text
            if display_text:
                for index, window in enumerate(solver.window_list):
                    cls.DrawText(
                        window,
                        'window_s={:.2f}, window_index={}, window_v={:.2f}, w_f:{:.2f}'.format(
                            window.window_s, index, window.window_v,
                            solver.window_confidence[index]),
                        surface.get_height() / len(solver.window_list) * index,
                        surface, sim_surface)

                # Display target window text.
                cls.DrawText(
                    solver.target_window,
                    'window_s={:.2f}, window_v={:.2f}, w_f:{:.2f}'.format(
                        solver.target_window.window_s,
                        solver.target_window.window_v,
                        solver.window_confidence[solver.best_window_index],
                    ),
                    surface.get_height() / 2, surface, sim_surface)

        else:

            best_time = solver.best_time
            # Display node value
            cmap = cm.jet_r
            norm = mpl.colors.Normalize(vmin=0, vmax=1 / (1 - 0.5))
            color = cmap(norm(0.5), bytes=True)
            pygame.draw.rect(surface, color,
                             (rear, 0, cell_size[0], cell_size[1]), 0)
            pygame.draw.rect(
                surface, cls.RED,
                ((target_window.window_s - sim_surface.origin[0]) *
                 sim_surface.scaling - 2, 0, 4, cell_size[1]), 0)
            if display_text:
                font = pygame.font.Font(None, 30)
                text = "a={:.2f}, time={:.2f}, ego_v:{:.2f}, r_v={:.2f} r_s:{:.2f}".format(
                    solver.action['a'], best_time, solver.ego_car[3],
                    target_window.window_v - solver.ego_car[3],
                    target_window.window_s - solver.ego_car[1])
                text = font.render(text, 1, (10, 10, 10), (255, 255, 255))
                surface.blit(text, (rear + cell_size[0] / 2, cell_size[1] / 2))

        # if sim_surface and hasattr(agent.value_net, "get_attention_matrix"):
        #     cls.display_vehicles_attention(agent, sim_surface)
    @classmethod
    def wrapper(cls, solver):
        def inner(surface, sim_surface=None, display_text=True):
            return cls.display(solver, surface, sim_surface, display_text)

        return inner

    @classmethod
    def DrawWindow(cls, window, color, surface, sim_surface):
        window_front = (
            window.front_s - sim_surface.origin[0]
        ) * sim_surface.scaling if window.front_is_valid else surface.get_width(
        )
        window_rear = (window.rear_s - sim_surface.origin[0]
                       ) * sim_surface.scaling if window.rear_is_valid else 0
        cell_size = (window_front - window_rear, surface.get_height())
        pygame.draw.rect(surface, color,
                         (window_rear, 0, cell_size[0], cell_size[1]), 0)
        pygame.draw.rect(
            surface, cls.RED,
            ((window.window_s - sim_surface.origin[0]) * sim_surface.scaling -
             2, 0, 4, cell_size[1]), 0)

    @classmethod
    def DrawText(cls, window, text, pos, surface, sim_surface):
        font = pygame.font.Font(None, 20)
        text = font.render(text, 1, (10, 10, 10), (255, 255, 255))
        window_rear = (window.rear_s - sim_surface.origin[0]
                       ) * sim_surface.scaling if window.rear_is_valid else 0

        surface.blit(text, [window_rear + 5, pos])

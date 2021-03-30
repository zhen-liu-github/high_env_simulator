
from .data_driven_solver import DataDrivenSolver
from .time_optimal_solver import TimeOptimalSolver

solver_config = {
    'rule-based': TimeOptimalSolver,
    'data-driven': DataDrivenSolver,
}

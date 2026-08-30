import numpy as np
from scipy.optimize import minimize
from aeroopt.physics.drag_solver import DragSolver

class AeroOptimizer:
    """Uses gradient-based optimization algorithms to find optimal geometric parameters for minimum drag."""

    def __init__(self, length: float = 0.5, target_radius: float = 0.05):
        self.length = length
        self.target_radius = target_radius
        self.solver = DragSolver(mach_number=1.5)

    def optimize_parabolic_parameter(self) -> float:
        """Finds the optimal parabolic curvature factor K that minimizes wave drag."""

        def objective_function(K_array: np.ndarray) -> float:
            K = K_array[0]
            x = np.linspace(0, self.length, 100)
            # Parabolic equation
            y = self.target_radius * ((2 * (x / self.length) - K * (x / self.length)**2) / (2 - K))
            y = np.maximum(y, 0)
            return self.solver.compute_wave_drag_factor(x, y)

        # Initial guess K = 0.5, bounds (0.0, 0.99)
        res = minimize(objective_function, x0=[0.5], bounds=[(0.0, 0.99)], method='SLSQP')
        return float(res.x[0])

import numpy as np
from scipy.optimize import minimize

from aeroopt.physics.drag_solver import DragSolver


class AeroOptimizer:
    """
    Uses SLSQP optimization to find the parabolic
    nose-cone curvature parameter that minimizes
    the wave-drag factor.
    """

    def __init__(
        self,
        length: float = 0.5,
        target_radius: float = 0.05,
        mach_number: float = 1.5,
        altitude_m: float = 0.0,
        num_points: int = 150
    ):

        self.length = float(length)

        self.target_radius = float(target_radius)

        self.num_points = int(num_points)


        self.solver = DragSolver(
            mach_number=mach_number,
            altitude_m=altitude_m
        )


    def parabolic_profile(
        self,
        K: float
    ):

        x = np.linspace(
            0.0,
            self.length,
            self.num_points
        )


        normalized_x = x / self.length


        denominator = 2.0 - K


        y = (
            self.target_radius
            *
            (
                2.0 * normalized_x
                -
                K * normalized_x ** 2
            )
            /
            denominator
        )


        y = np.maximum(
            y,
            0.0
        )


        return x, y


    def objective_function(
        self,
        K_array: np.ndarray
    ) -> float:

        K = float(K_array[0])


        x, y = self.parabolic_profile(K)


        drag = (
            self.solver
            .compute_wave_drag_factor(
                x,
                y
            )
        )


        return float(drag)


    def optimize_parabolic_parameter(
        self
    ) -> float:

        result = minimize(

            self.objective_function,

            x0=np.array([0.5]),

            method="SLSQP",

            bounds=[
                (0.0, 0.99)
            ],

            options={
                "maxiter": 100,
                "ftol": 1e-10
            }

        )


        if not result.success:

            raise RuntimeError(
                f"Optimization failed: "
                f"{result.message}"
            )


        return float(
            result.x[0]
        )


    def optimize(
        self
    ) -> dict:

        optimal_k = (
            self.optimize_parabolic_parameter()
        )


        optimized_drag = (
            self.objective_function(
                np.array([
                    optimal_k
                ])
            )
        )


        return {

            "optimal_k":
                optimal_k,

            "optimized_drag":
                optimized_drag,

            "method":
                "SciPy SLSQP"

        }
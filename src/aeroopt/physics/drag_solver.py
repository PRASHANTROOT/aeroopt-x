import numpy as np

class DragSolver:
    """Computes skin friction drag, pressure drag, and wave drag factors for aerodynamic shapes."""
    
    def __init__(self, mach_number: float = 1.5, altitude_m: float = 1000.0):
        self.mach = mach_number
        self.alt = altitude_m

    def compute_wave_drag_factor(self, x: np.ndarray, y: np.ndarray) -> float:
        """Approximates supersonic wave drag factor proportional integral."""
        dy_dx = np.gradient(y, x)
        # Integral of (dy/dx)^2 * y * dx
        integrand = (dy_dx ** 2) * y
        wave_drag_factor = float(np.sum(integrand))
        return wave_drag_factor

    def estimate_skin_friction(self, length: float, surface_area: float) -> float:
        """Estimates skin friction coefficient (Cf) using empirical Reynolds scaling."""
        reynolds_num = 1e7 * length
        cf = 0.455 / ((np.log10(reynolds_num)) ** 2.58)
        return float(cf)

import numpy as np

class DroneArmGenerator:
    """Generates aerodynamic cross-sections for drone multirotor arms (Teardrop / Airfoil shapes)."""
    
    def __init__(self, chord_length: float = 0.04, max_thickness: float = 0.015, num_points: int = 100):
        self.c = chord_length
        self.t = max_thickness
        self.n = num_points

    def teardrop_profile(self):
        """Generates a symmetrical teardrop cross-section to minimize motor downwash drag."""
        x = np.linspace(0, self.c, self.n)
        # Empirical teardrop thickness distribution equation
        yt = 5 * self.t * (
            0.2969 * np.sqrt(x / self.c)
            - 0.1260 * (x / self.c)
            - 0.3516 * (x / self.c) ** 2
            + 0.2843 * (x / self.c) ** 3
            - 0.1015 * (x / self.c) ** 4
        )
        return x, yt

    def square_profile(self):
        """Baseline unoptimized square tube profile for drag comparison."""
        x = np.array([0, 0, self.c, self.c, 0])
        y = np.array([0, self.t, self.t, 0, 0])
        return x, y

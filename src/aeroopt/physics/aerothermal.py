import numpy as np

class AeroThermalEngine:
    """Calculates supersonic shock wave angles, stagnation temperatures, and parametric sweeps."""

    # Predefined Vehicle Specifications
    PRESETS = {
        "Custom": {"length": 0.5, "radius": 0.05, "mach": 1.5, "unit": "Meters (m)"},
        "Sounding Rocket (Terrier-Orion)": {"length": 1.2, "radius": 0.17, "mach": 2.5, "unit": "Meters (m)"},
        "Model Rocket (Estes Alpha)": {"length": 0.15, "radius": 0.015, "mach": 0.3, "unit": "Meters (m)"},
        "Hypersonic Penetrator": {"length": 2.5, "radius": 0.12, "mach": 5.2, "unit": "Meters (m)"},
        "FPV Racing Drone Arm": {"length": 0.08, "radius": 0.008, "mach": 0.15, "unit": "Meters (m)"}
    }

    def __init__(self, mach: float = 1.5, altitude_m: float = 0.0):
        self.mach = mach
        self.altitude = altitude_m
        self.gamma = 1.4  # Ratio of specific heats for air

    def compute_stagnation_temperature(self, ambient_temp_k: float = 288.15) -> float:
        """Calculates total stagnation temperature rise at tip: T0 = T_inf * (1 + (gamma-1)/2 * M^2)."""
        return ambient_temp_k * (1.0 + ((self.gamma - 1.0) / 2.0) * (self.mach ** 2))

    def compute_oblique_shock_angle(self, half_angle_rad: float) -> float:
        """Approximates oblique shock wave angle (beta) for attached supersonic shockwaves."""
        if self.mach <= 1.0 or half_angle_rad <= 0:
            return 0.0
        
        # Weak shock approximation angle
        mach_angle = np.arcsin(1.0 / self.mach)
        beta = mach_angle + (self.gamma + 1.0) / 4.0 * half_angle_rad
        return float(np.degrees(beta))

    @staticmethod
    def generate_parametric_sweep(mach_range=(0.5, 4.0), fineness_range=(2.0, 10.0), grid_size=20):
        """Generates 2D array grid mapping Mach Speed vs Fineness Ratio (L/D) against Drag Factor."""
        machs = np.linspace(mach_range[0], mach_range[1], grid_size)
        fineness = np.linspace(fineness_range[0], fineness_range[1], grid_size)
        
        M_grid, F_grid = np.meshgrid(machs, fineness)
        
        # Wave drag factor proxy calculation based on Sears-Haack slenderness
        Drag_grid = (9.0 * (np.pi ** 2) / (128.0 * (F_grid ** 2))) * (1.0 / np.sqrt(np.maximum(0.1, M_grid**2 - 1.0)))
        return machs, fineness, Drag_grid

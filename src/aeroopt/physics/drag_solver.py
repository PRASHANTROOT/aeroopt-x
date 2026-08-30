import numpy as np

class DragSolver:
    """Calculates wave drag and skin friction coefficients across dynamic speed regimes and unit systems."""

    UNITS_LENGTH = {"m": 1.0, "cm": 0.01, "mm": 0.001, "in": 0.0254, "ft": 0.3048}
    UNITS_SPEED = {"m/s": 1.0, "km/h": 0.277778, "mph": 0.44704, "knots": 0.514444}

    def __init__(self, mach_number: float = 1.5, altitude_m: float = 0.0, unit_system: str = "metric"):
        self.mach = np.clip(mach_number, 0.1, 10.0) # Expanded Dynamic Mach Range (Subsonic to Hypersonic)
        self.altitude = altitude_m
        self.unit_system = unit_system

    @classmethod
    def convert_length(cls, val: float, from_unit: str) -> float:
        """Converts length measurements to standard meters."""
        return val * cls.UNITS_LENGTH.get(from_unit.lower(), 1.0)

    @classmethod
    def convert_speed(cls, val: float, from_unit: str) -> float:
        """Converts speed measurements to meters per second."""
        return val * cls.UNITS_SPEED.get(from_unit.lower(), 1.0)

    def get_air_properties(self):
        """Standard Atmosphere Model (ISA) calculation for dynamic air density and speed of sound up to 20 km."""
        if self.altitude <= 11000: # Troposphere
            T = 288.15 - 0.0065 * self.altitude
            p = 101325 * (T / 288.15) ** 5.2561
        else: # Lower Stratosphere
            T = 216.65
            p = 22632 * np.exp(-0.0001576 * (self.altitude - 11000))

        rho = p / (287.058 * T)
        a = np.sqrt(1.4 * 287.058 * T)
        return rho, a

    def compute_wave_drag_factor(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculates wave drag coefficient using numerical derivative area distribution."""
        if len(x) < 2 or len(y) < 2:
            return 0.0
        
        dx = np.diff(x)
        dy = np.diff(y)
        slopes = np.divide(dy, dx, out=np.zeros_like(dy), where=dx!=0)
        
        # Wave drag factor integral approximation
        drag_factor = np.sum(slopes**2 * dx) * (1.0 / (max(x) - min(x)))
        
        # Apply Mach scaling adjustment
        if self.mach > 1.0:
            mach_correction = 1.0 / np.sqrt(self.mach**2 - 1.0)
        else:
            mach_correction = 0.5 # Subsonic wave drag suppression factor

        return float(drag_factor * mach_correction)

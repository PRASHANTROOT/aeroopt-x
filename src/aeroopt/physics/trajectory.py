import numpy as np

class TrajectorySimulator:
    """Simulates 1D vertical rocket flight dynamics to calculate peak altitude (apogee)."""

    def __init__(self, dry_mass: float = 1.5, wet_mass: float = 2.5, thrust: float = 120.0, burn_time: float = 2.0, drag_cd: float = 0.15):
        self.m_dry = dry_mass
        self.m_wet = wet_mass
        self.thrust = thrust
        self.tb = burn_time
        self.cd = drag_cd
        self.g = 9.81
        self.rho = 1.225 # Sea level air density (kg/m^3)
        self.area = np.pi * (0.05 ** 2) # Cross-sectional area reference

    def run_simulation(self, dt: float = 0.01):
        """Integrates vertical flight equations of motion over time."""
        t, y, v = 0.0, 0.0, 0.0
        time_hist, alt_hist, vel_hist = [0.0], [0.0], [0.0]

        while y >= 0.0 and t < 60.0:
            current_mass = self.m_wet - ((self.m_wet - self.m_dry) / self.tb) * t if t <= self.tb else self.m_dry
            current_thrust = self.thrust if t <= self.tb else 0.0
            
            # Drag force: F_drag = 0.5 * rho * v^2 * Cd * A
            f_drag = 0.5 * self.rho * (v ** 2) * self.cd * self.area * np.sign(v)
            f_net = current_thrust - (current_mass * self.g) - f_drag

            a = f_net / current_mass
            v += a * dt
            y += v * dt
            t += dt

            time_hist.append(t)
            alt_hist.append(max(0.0, y))
            vel_hist.append(v)

            if y < 0.0 and t > self.tb:
                break

        return np.array(time_hist), np.array(alt_hist), np.array(vel_hist)

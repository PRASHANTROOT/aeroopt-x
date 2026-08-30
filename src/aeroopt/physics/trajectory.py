import numpy as np

class DynamicTrajectory2DOF:
    """Simulates 2D vertical launch trajectory with pitch degradation (gravity turn) and crosswinds."""

    def __init__(self, dry_mass=1.5, wet_mass=2.5, thrust=120.0, burn_time=2.0, drag_cd=0.15, wind_speed=5.0):
        self.m_dry = dry_mass
        self.m_wet = wet_mass
        self.thrust = thrust
        self.tb = burn_time
        self.cd = drag_cd
        self.wind_speed = wind_speed # Crosswind speed (m/s)
        self.g = 9.81
        self.rho = 1.225
        self.area = np.pi * (0.05 ** 2)

    def run_2d_simulation(self, pitch_kick_time: float = 0.5, dt: float = 0.01):
        """Integrates 2DOF trajectory (x, y, vx, vy, pitch angle)."""
        t, x, y = 0.0, 0.0, 0.0
        vx, vy = 0.0, 0.0
        pitch_deg = 90.0 # Initial vertical launch angle

        t_hist, x_hist, y_hist, vel_hist = [0.0], [0.0], [0.0], [0.0]

        while y >= 0.0 and t < 60.0:
            current_mass = self.m_wet - ((self.m_wet - self.m_dry) / self.tb) * t if t <= self.tb else self.m_dry
            current_thrust = self.thrust if t <= self.tb else 0.0

            # Gravity Turn Pitch Degradation
            if t > pitch_kick_time and pitch_deg > 20.0:
                pitch_deg -= 1.5 * dt # Tilt over time

            pitch_rad = np.radians(pitch_deg)

            # Air relative velocity including wind vector
            v_rel_x = vx - self.wind_speed
            v_rel_y = vy
            v_mag = np.sqrt(v_rel_x**2 + v_rel_y**2)

            # Drag components
            f_drag_mag = 0.5 * self.rho * (v_mag**2) * self.cd * self.area
            f_drag_x = f_drag_mag * (v_rel_x / max(1e-3, v_mag))
            f_drag_y = f_drag_mag * (v_rel_y / max(1e-3, v_mag))

            # Forces
            fx = current_thrust * np.cos(pitch_rad) - f_drag_x
            fy = current_thrust * np.sin(pitch_rad) - (current_mass * self.g) - f_drag_y

            # Acceleration & Integration
            ax = fx / current_mass
            ay = fy / current_mass

            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
            t += dt

            t_hist.append(t)
            x_hist.append(x)
            y_hist.append(max(0.0, y))
            vel_hist.append(np.sqrt(vx**2 + vy**2))

            if y < 0.0 and t > self.tb:
                break

        return np.array(t_hist), np.array(x_hist), np.array(y_hist), np.array(vel_hist)

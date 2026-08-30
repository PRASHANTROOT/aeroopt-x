import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import numpy as np
from aeroopt.geometry.nose_cone import NoseConeGenerator
from aeroopt.geometry.drone_arm import DroneArmGenerator
from aeroopt.physics.drag_solver import DragSolver

class TestAerodynamicMath:

    def test_unit_conversions(self):
        """Verify length and speed unit conversion accuracy."""
        assert np.isclose(DragSolver.convert_length(10, "in"), 0.254, atol=1e-5)
        assert np.isclose(DragSolver.convert_length(1, "ft"), 0.3048, atol=1e-5)
        assert np.isclose(DragSolver.convert_speed(100, "km/h"), 27.7778, atol=1e-3)
        assert np.isclose(DragSolver.convert_speed(100, "knots"), 51.4444, atol=1e-3)

    @pytest.mark.parametrize("length,radius", [
        (0.05, 0.005),  # Micro UAV scale
        (0.5, 0.05),    # Model Rocket scale
        (5.0, 0.4),     # Sounding Rocket scale
        (25.0, 1.5)     # Orbital Booster scale (Extreme Range)
    ])
    def test_nose_cone_dynamic_ranges(self, length, radius):
        """Test Sears-Haack curve generation across multi-scale dimensions."""
        gen = NoseConeGenerator(length=length, base_radius=radius, num_points=100)
        x, y = gen.sears_haack()
        
        assert len(x) == 100
        assert len(y) == 100
        assert np.isclose(x[0], 0.0)
        assert np.isclose(x[-1], length)
        assert np.isclose(y[0], 0.0, atol=1e-3)
        assert np.isclose(y[-1], radius, atol=1e-3)

    @pytest.mark.parametrize("mach", [0.2, 0.9, 1.0, 1.5, 3.0, 5.0, 8.0])
    def test_drag_solver_mach_regimes(self, mach):
        """Verify solver stability from Subsonic to Hypersonic speeds."""
        solver = DragSolver(mach_number=mach, altitude_m=5000)
        x = np.linspace(0, 1.0, 50)
        y = 0.1 * np.sin(x * np.pi / 2)
        
        drag = solver.compute_wave_drag_factor(x, y)
        assert np.isfinite(drag)
        assert drag >= 0.0

    def test_atmosphere_model_altitudes(self):
        """Test air property calculations across troposphere and stratosphere."""
        solver_sea_level = DragSolver(altitude_m=0)
        solver_high_alt = DragSolver(altitude_m=12000)
        
        rho_0, a_0 = solver_sea_level.get_air_properties()
        rho_h, a_h = solver_high_alt.get_air_properties()
        
        assert rho_0 > rho_h  # Air density decreases with altitude
        assert a_0 > a_h      # Speed of sound decreases at higher altitude

import os
import sys
from pathlib import Path

import numpy as np

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)


# ------------------------------------------------------------
# PROJECT PATH SETUP
# ------------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

SRC_PATH = (
    PROJECT_ROOT
    / "src"
)

if str(SRC_PATH) not in sys.path:

    sys.path.insert(
        0,
        str(SRC_PATH),
    )


# ------------------------------------------------------------
# AEROOPT-X CORE MODULES
# ------------------------------------------------------------

from aeroopt.geometry.nose_cone import (
    NoseConeGenerator,
)

from aeroopt.physics.drag_solver import (
    DragSolver,
)

from aeroopt.optimizer.objective import (
    AeroOptimizer,
)

from aeroopt.physics.aerothermal import (
    AeroThermalEngine,
)

from aeroopt.physics.trajectory import (
    DynamicTrajectory2DOF,
)


# ------------------------------------------------------------
# FLASK APPLICATION
# ------------------------------------------------------------

app = Flask(
    __name__,
    template_folder="templates",
)


# ------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------

def to_float_list(values):
    """
    Convert NumPy arrays/scalars into JSON-safe
    Python floats.
    """

    return [
        float(value)
        for value in values
    ]


def get_ambient_temperature(
    altitude_m,
):
    """
    Simple ISA temperature model.

    Valid as a simplified model for the current
    AeroOpt-X analysis.
    """

    altitude_m = max(
        float(altitude_m),
        0.0,
    )

    if altitude_m <= 11000:

        return (
            288.15
            - (
                0.0065
                * altitude_m
            )
        )

    return 216.65


def get_dynamic_pressure(
    density,
    velocity,
):
    """
    Dynamic pressure:

    q = 0.5 * rho * V^2
    """

    return float(
        0.5
        * density
        * velocity ** 2
    )


def json_error(
    message,
    status_code=400,
):

    return jsonify({
        "status": "error",
        "message": message,
    }), status_code


# ------------------------------------------------------------
# FRONTEND ROUTES
# ------------------------------------------------------------

@app.route(
    "/",
    methods=["GET"],
)
def index():

    return render_template(
        "index.html"
    )


@app.route(
    "/documentation",
    methods=["GET"],
)
def documentation():

    return render_template(
        "documentation/documentation.html"
    )


@app.route(
    "/help",
    methods=["GET"],
)
def help_page():

    return render_template(
        "help/help.html"
    )


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.route(
    "/api/health",
    methods=["GET"],
)
def health():

    return jsonify({
        "status": "healthy",
        "service": "AeroOpt-X",
        "engine": (
            "Python Aerodynamics Core"
        ),
    })


# ------------------------------------------------------------
# MAIN AERODYNAMIC ANALYSIS
# ------------------------------------------------------------

@app.route(
    "/api/analyze",
    methods=["POST"],
)
def analyze():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        # ====================================================
        # INPUTS
        # ====================================================

        length = float(
            data.get(
                "length",
                0.5,
            )
        )

        radius = float(
            data.get(
                "radius",
                0.05,
            )
        )

        mach = float(
            data.get(
                "mach",
                1.5,
            )
        )

        altitude = float(
            data.get(
                "altitude",
                0.0,
            )
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if length <= 0:

            return json_error(
                "Length must be greater than zero."
            )

        if radius <= 0:

            return json_error(
                "Radius must be greater than zero."
            )

        if mach <= 0:

            return json_error(
                "Mach number must be greater than zero."
            )

        if altitude < 0:

            return json_error(
                "Altitude cannot be negative."
            )

        # ====================================================
        # 1. GEOMETRY GENERATION
        # ====================================================

        generator = (
            NoseConeGenerator(
                length=length,
                base_radius=radius,
                num_points=150,
            )
        )

        x_sh, y_sh = (
            generator.sears_haack()
        )

        x_vk, y_vk = (
            generator.von_karman()
        )

        x_ogive, y_ogive = (
            generator.ogive()
        )

        # ====================================================
        # 2. DRAG SOLVER
        # ====================================================

        drag_solver = (
            DragSolver(
                mach_number=mach,
                altitude_m=altitude,
            )
        )

        drag_sh = (
            drag_solver
            .compute_wave_drag_factor(
                x_sh,
                y_sh,
            )
        )

        drag_vk = (
            drag_solver
            .compute_wave_drag_factor(
                x_vk,
                y_vk,
            )
        )

        drag_ogive = (
            drag_solver
            .compute_wave_drag_factor(
                x_ogive,
                y_ogive,
            )
        )

        # ====================================================
        # 3. SLSQP OPTIMIZATION
        # ====================================================

        optimizer = (
            AeroOptimizer(
                length=length,
                target_radius=radius,
            )
        )

        optimizer.solver = (
            DragSolver(
                mach_number=mach,
                altitude_m=altitude,
            )
        )

        optimal_k = (
            optimizer
            .optimize_parabolic_parameter()
        )

        x_opt, y_opt = (
            generator.parabolic(
                K=optimal_k,
            )
        )

        drag_opt = (
            drag_solver
            .compute_wave_drag_factor(
                x_opt,
                y_opt,
            )
        )

        # ====================================================
        # 4. ATMOSPHERIC PROPERTIES
        # ====================================================

        air_density, speed_of_sound = (
            drag_solver
            .get_air_properties()
        )

        air_density = float(
            air_density
        )

        speed_of_sound = float(
            speed_of_sound
        )

        # ====================================================
        # 5. FLIGHT VELOCITY
        # ====================================================

        velocity = (
            mach
            * speed_of_sound
        )

        dynamic_pressure = (
            get_dynamic_pressure(
                air_density,
                velocity,
            )
        )

        # ====================================================
        # 6. AEROTHERMAL ANALYSIS
        # ====================================================

        thermal_engine = (
            AeroThermalEngine(
                mach=mach,
                altitude_m=altitude,
            )
        )

        ambient_temperature = (
            get_ambient_temperature(
                altitude
            )
        )

        stagnation_temperature = (
            thermal_engine
            .compute_stagnation_temperature(
                ambient_temp_k=(
                    ambient_temperature
                ),
            )
        )

        half_angle_rad = float(
            np.arctan(
                radius
                / length
            )
        )

        half_angle_deg = float(
            np.degrees(
                half_angle_rad
            )
        )

        # Detailed oblique shock analysis

        shock_analysis = (
            thermal_engine
            .analyze_oblique_shock(
                half_angle_rad=(
                    half_angle_rad
                ),
                ambient_temp_k=(
                    ambient_temperature
                ),
            )
        )

        shock_angle_deg = float(
            shock_analysis[
                "shock_angle_deg"
            ]
        )

        mach_angle_deg = float(
            shock_analysis[
                "mach_angle_deg"
            ]
        )

        post_shock_temperature = float(
            shock_analysis[
                "post_shock_temperature_k"
            ]
        )

        thermal_severity = (
            AeroThermalEngine
            .get_thermal_severity(
                stagnation_temperature
            )
        )

        flow_regime = (
            thermal_engine
            .get_flow_regime()
        )

        # ====================================================
        # 7. ENGINEERING COMPARISONS
        # ====================================================

        baseline_drag = min(
            drag_sh,
            drag_vk,
            drag_ogive,
        )

        if baseline_drag > 0:

            optimization_change_percent = (
                (
                    drag_opt
                    - baseline_drag
                )
                / baseline_drag
            ) * 100.0

        else:

            optimization_change_percent = 0.0

        # ====================================================
        # 8. FINENESS RATIO
        # ====================================================

        diameter = (
            2.0
            * radius
        )

        if diameter > 0:

            fineness_ratio = (
                length
                / diameter
            )

        else:

            fineness_ratio = 0.0

        # ====================================================
        # RESPONSE
        # ====================================================

        return jsonify({

            "status": "success",

            # ------------------------------------------------
            # INPUT
            # ------------------------------------------------

            "input": {

                "length": length,

                "radius": radius,

                "diameter": diameter,

                "mach": mach,

                "altitude": altitude,

                "fineness_ratio": (
                    float(
                        fineness_ratio
                    )
                ),

                "half_angle_deg": (
                    half_angle_deg
                ),
            },

            # ------------------------------------------------
            # ATMOSPHERE
            # ------------------------------------------------

            "atmosphere": {

                "air_density_kg_m3": (
                    air_density
                ),

                "speed_of_sound_m_s": (
                    speed_of_sound
                ),

                "ambient_temperature_k": (
                    float(
                        ambient_temperature
                    )
                ),

                "velocity_m_s": (
                    float(
                        velocity
                    )
                ),

                "dynamic_pressure_pa": (
                    float(
                        dynamic_pressure
                    )
                ),
            },

            # ------------------------------------------------
            # DRAG
            # ------------------------------------------------

            "drag": {

                "sears_haack": (
                    float(
                        drag_sh
                    )
                ),

                "von_karman": (
                    float(
                        drag_vk
                    )
                ),

                "ogive": (
                    float(
                        drag_ogive
                    )
                ),

                "optimized_parabolic": (
                    float(
                        drag_opt
                    )
                ),
            },

            # ------------------------------------------------
            # OPTIMIZATION
            # ------------------------------------------------

            "optimization": {

                "method": (
                    "SciPy SLSQP"
                ),

                "optimal_k": (
                    float(
                        optimal_k
                    )
                ),

                "reference_drag": (
                    float(
                        baseline_drag
                    )
                ),

                "optimized_drag": (
                    float(
                        drag_opt
                    )
                ),

                "change_vs_best_reference_percent": (
                    float(
                        optimization_change_percent
                    )
                ),
            },

            # ------------------------------------------------
            # THERMAL
            # ------------------------------------------------

            "thermal": {

                "flow_regime": (
                    flow_regime
                ),

                "ambient_temperature_k": (
                    float(
                        ambient_temperature
                    )
                ),

                "stagnation_temperature_k": (
                    float(
                        stagnation_temperature
                    )
                ),

                "post_shock_temperature_k": (
                    post_shock_temperature
                ),

                "thermal_severity": (
                    thermal_severity[
                        "level"
                    ]
                ),

                "thermal_message": (
                    thermal_severity[
                        "message"
                    ]
                ),
            },

            # ------------------------------------------------
            # SHOCK ANALYSIS
            # ------------------------------------------------

            "shock": {

                "applicable": (
                    shock_analysis[
                        "applicable"
                    ]
                ),

                "shock_type": (
                    shock_analysis[
                        "shock_type"
                    ]
                ),

                "status": (
                    shock_analysis[
                        "status"
                    ]
                ),

                "shock_angle_deg": (
                    shock_angle_deg
                ),

                "mach_angle_deg": (
                    mach_angle_deg
                ),

                "deflection_angle_deg": (
                    float(
                        shock_analysis[
                            "deflection_angle_deg"
                        ]
                    )
                ),

                "max_attached_deflection_deg": (
                    float(
                        shock_analysis[
                            "max_attached_deflection_deg"
                        ]
                    )
                ),

                "normal_mach_1": (
                    float(
                        shock_analysis[
                            "normal_mach_1"
                        ]
                    )
                ),

                "normal_mach_2": (
                    float(
                        shock_analysis[
                            "normal_mach_2"
                        ]
                    )
                ),

                "post_shock_mach": (
                    float(
                        shock_analysis[
                            "post_shock_mach"
                        ]
                    )
                ),

                "pressure_ratio": (
                    float(
                        shock_analysis[
                            "pressure_ratio"
                        ]
                    )
                ),

                "temperature_ratio": (
                    float(
                        shock_analysis[
                            "temperature_ratio"
                        ]
                    )
                ),

                "density_ratio": (
                    float(
                        shock_analysis[
                            "density_ratio"
                        ]
                    )
                ),
            },

            # ------------------------------------------------
            # BACKWARD COMPATIBILITY
            # ------------------------------------------------

            "geometry": {

                "x": (
                    to_float_list(
                        x_sh
                    )
                ),

                "sears_haack": (
                    to_float_list(
                        y_sh
                    )
                ),

                "von_karman": (
                    to_float_list(
                        y_vk
                    )
                ),

                "ogive": (
                    to_float_list(
                        y_ogive
                    )
                ),

                "optimized_parabolic": (
                    to_float_list(
                        y_opt
                    )
                ),
            },

            # ------------------------------------------------
            # METADATA
            # ------------------------------------------------

            "metadata": {

                "geometry_points": (
                    len(
                        x_sh
                    )
                ),

                "optimizer": (
                    "SLSQP"
                ),

                "analysis_engine": (
                    "AeroOpt-X Python Core"
                ),

                "thermal_engine": (
                    "Theta-Beta-M "
                    "Oblique Shock Solver"
                ),
            },
        })

    except Exception as error:

        app.logger.exception(
            "AeroOpt-X analysis failed"
        )

        return jsonify({
            "status": "error",
            "message": str(
                error
            ),
        }), 500


# ------------------------------------------------------------
# STANDALONE SLSQP OPTIMIZATION API
# ------------------------------------------------------------

@app.route(
    "/api/optimize",
    methods=["POST"],
)
def optimize():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        length = float(
            data.get(
                "length",
                0.5,
            )
        )

        radius = float(
            data.get(
                "radius",
                0.05,
            )
        )

        mach = float(
            data.get(
                "mach",
                1.5,
            )
        )

        altitude = float(
            data.get(
                "altitude",
                0.0,
            )
        )

        if length <= 0:
            return json_error(
                "Length must be greater than zero."
            )

        if radius <= 0:
            return json_error(
                "Radius must be greater than zero."
            )

        if mach <= 0:
            return json_error(
                "Mach number must be greater than zero."
            )

        if altitude < 0:
            return json_error(
                "Altitude cannot be negative."
            )

        generator = (
            NoseConeGenerator(
                length=length,
                base_radius=radius,
                num_points=150,
            )
        )

        drag_solver = (
            DragSolver(
                mach_number=mach,
                altitude_m=altitude,
            )
        )

        optimizer = (
            AeroOptimizer(
                length=length,
                target_radius=radius,
            )
        )

        optimizer.solver = (
            drag_solver
        )

        optimal_k = (
            optimizer
            .optimize_parabolic_parameter()
        )

        x_opt, y_opt = (
            generator.parabolic(
                K=optimal_k
            )
        )

        drag_opt = (
            drag_solver
            .compute_wave_drag_factor(
                x_opt,
                y_opt,
            )
        )

        x_sh, y_sh = (
            generator.sears_haack()
        )

        drag_sh = (
            drag_solver
            .compute_wave_drag_factor(
                x_sh,
                y_sh,
            )
        )

        if drag_sh > 0:

            change_percent = (
                (
                    drag_opt
                    - drag_sh
                )
                / drag_sh
            ) * 100.0

        else:

            change_percent = 0.0

        return jsonify({

            "status": "success",

            "input": {

                "length": length,

                "radius": radius,

                "mach": mach,

                "altitude": altitude,
            },

            "optimal_k": float(
                optimal_k
            ),

            "optimization": {

                "method": (
                    "SciPy SLSQP"
                ),

                "optimal_k": float(
                    optimal_k
                ),

                "optimized_drag": float(
                    drag_opt
                ),

                "reference_drag_sears_haack": (
                    float(
                        drag_sh
                    )
                ),

                "change_vs_sears_haack_percent": (
                    float(
                        change_percent
                    )
                ),
            },

            "geometry": {

                "x": (
                    to_float_list(
                        x_opt
                    )
                ),

                "optimized_parabolic": (
                    to_float_list(
                        y_opt
                    )
                ),
            },

            "metadata": {

                "optimizer": (
                    "SLSQP"
                ),

                "geometry_points": (
                    len(
                        x_opt
                    )
                ),
            },
        })

    except Exception as error:

        app.logger.exception(
            "AeroOpt-X optimization failed"
        )

        return jsonify({
            "status": "error",
            "message": str(
                error
            ),
        }), 500


# ------------------------------------------------------------
# REAL 2DOF TRAJECTORY API
# ------------------------------------------------------------

@app.route(
    "/api/trajectory",
    methods=["POST"],
)
def trajectory():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        thrust = float(
            data.get(
                "thrust",
                150.0,
            )
        )

        burn_time = float(
            data.get(
                "burn_time",
                2.5,
            )
        )

        wind_speed = float(
            data.get(
                "wind_speed",
                5.0,
            )
        )

        dry_mass = float(
            data.get(
                "dry_mass",
                1.5,
            )
        )

        wet_mass = float(
            data.get(
                "wet_mass",
                2.5,
            )
        )

        drag_cd = float(
            data.get(
                "drag_cd",
                0.15,
            )
        )

        pitch_kick_time = float(
            data.get(
                "pitch_kick_time",
                0.5,
            )
        )

        dt = float(
            data.get(
                "dt",
                0.01,
            )
        )

        if thrust < 0:
            return json_error(
                "Thrust cannot be negative."
            )

        if burn_time <= 0:
            return json_error(
                "Burn duration must be greater than zero."
            )

        if wind_speed < 0:
            return json_error(
                "Wind speed cannot be negative."
            )

        if dry_mass <= 0:
            return json_error(
                "Dry mass must be greater than zero."
            )

        if wet_mass <= dry_mass:
            return json_error(
                "Wet mass must be greater than dry mass."
            )

        if dt <= 0:
            return json_error(
                "Simulation time step must be greater than zero."
            )

        simulator = (
            DynamicTrajectory2DOF(
                dry_mass=dry_mass,
                wet_mass=wet_mass,
                thrust=thrust,
                burn_time=burn_time,
                drag_cd=drag_cd,
                wind_speed=wind_speed,
            )
        )

        t, x, y, velocity = (
            simulator.run_2d_simulation(
                pitch_kick_time=(
                    pitch_kick_time
                ),
                dt=dt,
            )
        )

        apogee_index = int(
            np.argmax(
                y
            )
        )

        apogee = float(
            y[
                apogee_index
            ]
        )

        apogee_time = float(
            t[
                apogee_index
            ]
        )

        downrange = float(
            x[-1]
        )

        max_velocity = float(
            np.max(
                velocity
            )
        )

        flight_time = float(
            t[-1]
        )

        return jsonify({

            "status": "success",

            "input": {

                "thrust": thrust,

                "burn_time": burn_time,

                "wind_speed": wind_speed,

                "dry_mass": dry_mass,

                "wet_mass": wet_mass,

                "drag_cd": drag_cd,
            },

            "trajectory": {

                "time_s": (
                    to_float_list(
                        t
                    )
                ),

                "downrange_m": (
                    to_float_list(
                        x
                    )
                ),

                "altitude_m": (
                    to_float_list(
                        y
                    )
                ),

                "velocity_m_s": (
                    to_float_list(
                        velocity
                    )
                ),
            },

            "summary": {

                "apogee_m": apogee,

                "apogee_time_s": (
                    apogee_time
                ),

                "downrange_m": (
                    downrange
                ),

                "max_velocity_m_s": (
                    max_velocity
                ),

                "flight_time_s": (
                    flight_time
                ),
            },

            "metadata": {

                "simulation": (
                    "DynamicTrajectory2DOF"
                ),

                "points": int(
                    len(
                        t
                    )
                ),
            },
        })

    except Exception as error:

        app.logger.exception(
            "Trajectory simulation failed"
        )

        return jsonify({
            "status": "error",
            "message": str(
                error
            ),
        }), 500


# ------------------------------------------------------------
# REAL PARAMETRIC SWEEP API
# ------------------------------------------------------------

@app.route(
    "/api/sweep",
    methods=["POST"],
)
def sweep():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    try:

        mach_min = float(
            data.get(
                "mach_min",
                0.5,
            )
        )

        mach_max = float(
            data.get(
                "mach_max",
                6.0,
            )
        )

        fineness_min = float(
            data.get(
                "fineness_min",
                2.0,
            )
        )

        fineness_max = float(
            data.get(
                "fineness_max",
                10.0,
            )
        )

        grid_size = int(
            data.get(
                "grid_size",
                30,
            )
        )

        if mach_min <= 0:
            return json_error(
                "Minimum Mach must be greater than zero."
            )

        if mach_max <= mach_min:
            return json_error(
                "Maximum Mach must be greater than minimum Mach."
            )

        if fineness_min <= 0:
            return json_error(
                "Minimum fineness ratio must be greater than zero."
            )

        if fineness_max <= fineness_min:
            return json_error(
                "Maximum fineness ratio must be greater than minimum."
            )

        grid_size = max(
            5,
            min(
                grid_size,
                100,
            ),
        )

        machs, fineness, drag_grid = (
            AeroThermalEngine
            .generate_parametric_sweep(
                mach_range=(
                    mach_min,
                    mach_max,
                ),

                fineness_range=(
                    fineness_min,
                    fineness_max,
                ),

                grid_size=grid_size,
            )
        )

        return jsonify({

            "status": "success",

            "input": {

                "mach_min": (
                    mach_min
                ),

                "mach_max": (
                    mach_max
                ),

                "fineness_min": (
                    fineness_min
                ),

                "fineness_max": (
                    fineness_max
                ),

                "grid_size": (
                    grid_size
                ),
            },

            "sweep": {

                "mach": (
                    to_float_list(
                        machs
                    )
                ),

                "fineness_ratio": (
                    to_float_list(
                        fineness
                    )
                ),

                "drag_factor": (
                    np.asarray(
                        drag_grid,
                        dtype=float,
                    )
                    .tolist()
                ),
            },

            "metadata": {

                "engine": (
                    "AeroThermalEngine "
                    "Parametric Sweep"
                ),

                "grid_size": (
                    grid_size
                ),
            },
        })

    except Exception as error:

        app.logger.exception(
            "Parametric sweep failed"
        )

        return jsonify({
            "status": "error",
            "message": str(
                error
            ),
        }), 500


# ------------------------------------------------------------
# LOCAL DEVELOPMENT SERVER
# ------------------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000",
        )
    )

    debug = (
        os.getenv(
            "FLASK_DEBUG",
            "1",
        )
        == "1"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
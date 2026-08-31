import numpy as np


class AeroThermalEngine:
    """
    AeroOpt-X aerothermal analysis engine.

    Provides:

    - Stagnation temperature
    - Oblique shock analysis using the theta-beta-M relation
    - Weak attached shock solution
    - Detached shock detection
    - Mach angle
    - Normal Mach number
    - Post-shock Mach number
    - Pressure, temperature and density ratios
    - Engineering interpretation data
    - Parametric drag sweeps
    """

    # ------------------------------------------------------------
    # PREDEFINED VEHICLE SPECIFICATIONS
    # ------------------------------------------------------------

    PRESETS = {
        "Custom": {
            "length": 0.5,
            "radius": 0.05,
            "mach": 1.5,
            "unit": "Meters (m)",
        },

        "Sounding Rocket (Terrier-Orion)": {
            "length": 1.2,
            "radius": 0.17,
            "mach": 2.5,
            "unit": "Meters (m)",
        },

        "Model Rocket (Estes Alpha)": {
            "length": 0.15,
            "radius": 0.015,
            "mach": 0.3,
            "unit": "Meters (m)",
        },

        "Hypersonic Penetrator": {
            "length": 2.5,
            "radius": 0.12,
            "mach": 5.2,
            "unit": "Meters (m)",
        },

        "FPV Racing Drone Arm": {
            "length": 0.08,
            "radius": 0.008,
            "mach": 0.15,
            "unit": "Meters (m)",
        },
    }

    # ------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------

    def __init__(
        self,
        mach: float = 1.5,
        altitude_m: float = 0.0,
    ):

        self.mach = float(mach)
        self.altitude = float(altitude_m)

        # Air properties for a calorically perfect gas
        self.gamma = 1.4
        self.gas_constant = 287.05

    # ------------------------------------------------------------
    # STAGNATION TEMPERATURE
    # ------------------------------------------------------------

    def compute_stagnation_temperature(
        self,
        ambient_temp_k: float = 288.15,
    ) -> float:
        """
        Calculate ideal adiabatic stagnation temperature.

        T0 = T_inf * (1 + ((gamma - 1) / 2) * M^2)

        This is useful as an ideal aerodynamic heating indicator.
        """

        ambient_temp_k = float(ambient_temp_k)

        return float(
            ambient_temp_k
            * (
                1.0
                + (
                    (self.gamma - 1.0)
                    / 2.0
                )
                * (
                    self.mach ** 2
                )
            )
        )

    # ------------------------------------------------------------
    # MACH ANGLE
    # ------------------------------------------------------------

    def compute_mach_angle(self) -> float:
        """
        Calculate Mach angle.

        mu = asin(1 / M)

        Returns degrees.

        A Mach angle only exists for supersonic flow.
        """

        if self.mach <= 1.0:
            return 0.0

        mach_angle_rad = np.arcsin(
            1.0 / self.mach
        )

        return float(
            np.degrees(
                mach_angle_rad
            )
        )

    # ------------------------------------------------------------
    # THETA-BETA-M RELATION
    # ------------------------------------------------------------

    def _theta_from_beta(
        self,
        beta_rad: float,
    ) -> float:
        """
        Calculate flow deflection angle theta from
        the theta-beta-M relation.

        tan(theta) =
            2 cot(beta)
            *
            (
                M^2 sin^2(beta) - 1
            )
            /
            (
                M^2 (gamma + cos(2 beta)) + 2
            )
        """

        M = self.mach
        gamma = self.gamma

        sin_beta = np.sin(beta_rad)
        cos_beta = np.cos(beta_rad)

        numerator = (
            2.0
            * (
                cos_beta / sin_beta
            )
            * (
                (
                    M ** 2
                    * sin_beta ** 2
                )
                - 1.0
            )
        )

        denominator = (
            M ** 2
            * (
                gamma
                + np.cos(
                    2.0 * beta_rad
                )
            )
            + 2.0
        )

        if abs(denominator) < 1e-12:
            return np.nan

        tan_theta = (
            numerator
            / denominator
        )

        return float(
            np.arctan(
                tan_theta
            )
        )

    # ------------------------------------------------------------
    # MAXIMUM ATTACHED DEFLECTION ANGLE
    # ------------------------------------------------------------

    def compute_max_deflection_angle(self) -> float:
        """
        Estimate the maximum flow deflection angle for
        an attached oblique shock.

        Returns degrees.
        """

        if self.mach <= 1.0:
            return 0.0

        mach_angle = np.arcsin(
            1.0 / self.mach
        )

        beta_values = np.linspace(
            mach_angle + 1e-6,
            np.pi / 2.0 - 1e-6,
            5000,
        )

        theta_values = []

        for beta in beta_values:

            theta = self._theta_from_beta(
                beta
            )

            if np.isfinite(theta):
                theta_values.append(
                    theta
                )

        if not theta_values:
            return 0.0

        theta_max = max(
            theta_values
        )

        return float(
            np.degrees(
                theta_max
            )
        )

    # ------------------------------------------------------------
    # OBLIQUE SHOCK ANALYSIS
    # ------------------------------------------------------------

    def analyze_oblique_shock(
        self,
        half_angle_rad: float,
        ambient_temp_k: float = 288.15,
    ) -> dict:
        """
        Perform a detailed oblique shock analysis.

        The vehicle half-angle is treated as the local
        flow deflection angle theta.
        """

        M1 = float(
            self.mach
        )

        gamma = float(
            self.gamma
        )

        theta_rad = max(
            float(
                half_angle_rad
            ),
            0.0,
        )

        theta_deg = float(
            np.degrees(
                theta_rad
            )
        )

        ambient_temp_k = float(
            ambient_temp_k
        )

        # --------------------------------------------------------
        # SUBSONIC / SONIC FLOW
        # --------------------------------------------------------

        if M1 <= 1.0:

            return {
                "applicable": False,
                "shock_type": "No oblique shock",

                "shock_angle_deg": 0.0,
                "mach_angle_deg": 0.0,

                "deflection_angle_deg": theta_deg,
                "max_attached_deflection_deg": 0.0,

                "normal_mach_1": 0.0,
                "normal_mach_2": 0.0,

                "post_shock_mach": M1,

                "pressure_ratio": 1.0,
                "temperature_ratio": 1.0,
                "density_ratio": 1.0,

                "post_shock_temperature_k": (
                    ambient_temp_k
                ),

                "status": (
                    "Oblique shock relations are only "
                    "applicable to supersonic flow."
                ),
            }

        # --------------------------------------------------------
        # MACH ANGLE
        # --------------------------------------------------------

        mach_angle_rad = np.arcsin(
            1.0 / M1
        )

        mach_angle_deg = float(
            np.degrees(
                mach_angle_rad
            )
        )

        # --------------------------------------------------------
        # MAX ATTACHED DEFLECTION
        # --------------------------------------------------------

        max_theta_deg = (
            self.compute_max_deflection_angle()
        )

        # --------------------------------------------------------
        # DETACHED SHOCK CHECK
        # --------------------------------------------------------

        if theta_deg > max_theta_deg:

            return {
                "applicable": True,
                "shock_type": "Detached shock",

                "shock_angle_deg": 90.0,
                "mach_angle_deg": mach_angle_deg,

                "deflection_angle_deg": theta_deg,
                "max_attached_deflection_deg": (
                    max_theta_deg
                ),

                "normal_mach_1": M1,
                "normal_mach_2": 0.0,

                "post_shock_mach": 0.0,

                "pressure_ratio": 0.0,
                "temperature_ratio": 0.0,
                "density_ratio": 0.0,

                "post_shock_temperature_k": 0.0,

                "status": (
                    "The requested flow deflection exceeds "
                    "the maximum attached-shock deflection. "
                    "A detached bow shock is expected."
                ),
            }

        # --------------------------------------------------------
        # ZERO DEFLECTION
        # --------------------------------------------------------

        if theta_rad <= 1e-8:

            return {
                "applicable": True,
                "shock_type": "Mach wave",

                "shock_angle_deg": mach_angle_deg,
                "mach_angle_deg": mach_angle_deg,

                "deflection_angle_deg": theta_deg,
                "max_attached_deflection_deg": (
                    max_theta_deg
                ),

                "normal_mach_1": 1.0,
                "normal_mach_2": 1.0,

                "post_shock_mach": M1,

                "pressure_ratio": 1.0,
                "temperature_ratio": 1.0,
                "density_ratio": 1.0,

                "post_shock_temperature_k": (
                    ambient_temp_k
                ),

                "status": (
                    "Zero flow deflection produces a Mach wave."
                ),
            }

        # --------------------------------------------------------
        # FIND WEAK SHOCK SOLUTION
        # --------------------------------------------------------

        beta_values = np.linspace(
            mach_angle_rad + 1e-7,
            np.pi / 2.0 - 1e-7,
            10000,
        )

        target = theta_rad

        previous_beta = None
        previous_value = None

        root_low = None
        root_high = None

        for beta in beta_values:

            theta_beta = (
                self._theta_from_beta(
                    beta
                )
            )

            if not np.isfinite(
                theta_beta
            ):
                continue

            current_value = (
                theta_beta
                - target
            )

            if (
                previous_value is not None
                and current_value
                * previous_value
                <= 0.0
            ):

                root_low = previous_beta
                root_high = beta

                break

            previous_beta = beta
            previous_value = current_value

        # --------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------

        if (
            root_low is None
            or root_high is None
        ):

            return {
                "applicable": True,
                "shock_type": "Detached shock",

                "shock_angle_deg": 90.0,
                "mach_angle_deg": mach_angle_deg,

                "deflection_angle_deg": theta_deg,
                "max_attached_deflection_deg": (
                    max_theta_deg
                ),

                "normal_mach_1": M1,
                "normal_mach_2": 0.0,

                "post_shock_mach": 0.0,

                "pressure_ratio": 0.0,
                "temperature_ratio": 0.0,
                "density_ratio": 0.0,

                "post_shock_temperature_k": 0.0,

                "status": (
                    "No attached weak-shock solution "
                    "was found."
                ),
            }

        # --------------------------------------------------------
        # BISECTION ROOT SOLVER
        # --------------------------------------------------------

        for _ in range(80):

            beta_mid = (
                root_low
                + root_high
            ) / 2.0

            theta_mid = (
                self._theta_from_beta(
                    beta_mid
                )
            )

            value_low = (
                self._theta_from_beta(
                    root_low
                )
                - target
            )

            value_mid = (
                theta_mid
                - target
            )

            if (
                value_low
                * value_mid
                <= 0.0
            ):
                root_high = beta_mid

            else:
                root_low = beta_mid

        beta_rad = (
            root_low
            + root_high
        ) / 2.0

        beta_deg = float(
            np.degrees(
                beta_rad
            )
        )

        # --------------------------------------------------------
        # NORMAL MACH NUMBER BEFORE SHOCK
        # --------------------------------------------------------

        M1n = (
            M1
            * np.sin(
                beta_rad
            )
        )

        # --------------------------------------------------------
        # NORMAL SHOCK RELATIONS
        # --------------------------------------------------------

        M2n_squared = (
            (
                1.0
                + (
                    (
                        gamma - 1.0
                    )
                    / 2.0
                )
                * M1n ** 2
            )
            /
            (
                gamma
                * M1n ** 2
                - (
                    (
                        gamma - 1.0
                    )
                    / 2.0
                )
            )
        )

        M2n = np.sqrt(
            max(
                M2n_squared,
                0.0,
            )
        )

        # --------------------------------------------------------
        # POST SHOCK MACH
        # --------------------------------------------------------

        denominator = np.sin(
            beta_rad
            - theta_rad
        )

        if abs(denominator) < 1e-10:
            M2 = 0.0
        else:
            M2 = (
                M2n
                / denominator
            )

        # --------------------------------------------------------
        # PRESSURE RATIO
        # --------------------------------------------------------

        pressure_ratio = (
            1.0
            + (
                (
                    2.0
                    * gamma
                )
                /
                (
                    gamma + 1.0
                )
            )
            * (
                M1n ** 2
                - 1.0
            )
        )

        # --------------------------------------------------------
        # DENSITY RATIO
        # --------------------------------------------------------

        density_ratio = (
            (
                (
                    gamma + 1.0
                )
                * M1n ** 2
            )
            /
            (
                (
                    gamma - 1.0
                )
                * M1n ** 2
                + 2.0
            )
        )

        # --------------------------------------------------------
        # TEMPERATURE RATIO
        # --------------------------------------------------------

        if density_ratio > 0:
            temperature_ratio = (
                pressure_ratio
                / density_ratio
            )
        else:
            temperature_ratio = 0.0

        post_shock_temperature = (
            ambient_temp_k
            * temperature_ratio
        )

        return {
            "applicable": True,
            "shock_type": "Attached weak oblique shock",

            "shock_angle_deg": float(
                beta_deg
            ),

            "mach_angle_deg": float(
                mach_angle_deg
            ),

            "deflection_angle_deg": float(
                theta_deg
            ),

            "max_attached_deflection_deg": float(
                max_theta_deg
            ),

            "normal_mach_1": float(
                M1n
            ),

            "normal_mach_2": float(
                M2n
            ),

            "post_shock_mach": float(
                M2
            ),

            "pressure_ratio": float(
                pressure_ratio
            ),

            "temperature_ratio": float(
                temperature_ratio
            ),

            "density_ratio": float(
                density_ratio
            ),

            "post_shock_temperature_k": float(
                post_shock_temperature
            ),

            "status": (
                "Attached weak oblique shock solution computed."
            ),
        }

    # ------------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # ------------------------------------------------------------

    def compute_oblique_shock_angle(
        self,
        half_angle_rad: float,
    ) -> float:
        """
        Backward-compatible method used by the existing
        AeroOpt-X backend.

        Returns only the shock angle in degrees.
        """

        result = self.analyze_oblique_shock(
            half_angle_rad=half_angle_rad
        )

        return float(
            result[
                "shock_angle_deg"
            ]
        )

    # ------------------------------------------------------------
    # FLOW REGIME
    # ------------------------------------------------------------

    def get_flow_regime(self) -> str:
        """
        Return a user-friendly flight regime.
        """

        M = self.mach

        if M < 0.8:
            return "Subsonic"

        if M < 1.2:
            return "Transonic"

        if M < 5.0:
            return "Supersonic"

        return "Hypersonic"

    # ------------------------------------------------------------
    # THERMAL SEVERITY
    # ------------------------------------------------------------

    @staticmethod
    def get_thermal_severity(
        stagnation_temperature_k: float,
    ) -> dict:
        """
        Provide a simple engineering interpretation
        of ideal stagnation temperature.
        """

        temperature = float(
            stagnation_temperature_k
        )

        if temperature < 400:

            return {
                "level": "Low",
                "message": (
                    "Relatively low aerodynamic heating "
                    "for preliminary analysis."
                ),
            }

        if temperature < 700:

            return {
                "level": "Moderate",
                "message": (
                    "Aerodynamic heating is becoming "
                    "an important design consideration."
                ),
            }

        if temperature < 1200:

            return {
                "level": "High",
                "message": (
                    "High aerodynamic heating. Thermal "
                    "materials and insulation should be "
                    "considered."
                ),
            }

        return {
            "level": "Extreme",
            "message": (
                "Extreme ideal stagnation temperature. "
                "Advanced thermal protection and high-"
                "temperature materials may be required."
            ),
        }

    # ------------------------------------------------------------
    # PARAMETRIC SWEEP
    # ------------------------------------------------------------

    @staticmethod
    def generate_parametric_sweep(
        mach_range=(0.5, 4.0),
        fineness_range=(2.0, 10.0),
        grid_size=20,
    ):
        """
        Generate a 2D engineering drag-factor proxy.

        Axes:
        - Mach number
        - Fineness ratio L/D
        """

        machs = np.linspace(
            mach_range[0],
            mach_range[1],
            grid_size,
        )

        fineness = np.linspace(
            fineness_range[0],
            fineness_range[1],
            grid_size,
        )

        M_grid, F_grid = np.meshgrid(
            machs,
            fineness,
        )

        # Keep the existing engineering proxy stable
        # near Mach 1.

        supersonic_term = np.sqrt(
            np.maximum(
                0.1,
                M_grid ** 2 - 1.0,
            )
        )

        drag_grid = (
            (
                9.0
                * (
                    np.pi ** 2
                )
            )
            /
            (
                128.0
                * (
                    F_grid ** 2
                )
            )
        ) * (
            1.0
            / supersonic_term
        )

        return (
            machs,
            fineness,
            drag_grid,
        )
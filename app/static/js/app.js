/* ============================================================
   AEROOPT-X APPLICATION CONTROLLER
   app/static/js/app.js
   ============================================================ */

"use strict";

/* ============================================================
   STATE
   ============================================================ */

const state = {
  length: 0.5,
  radius: 0.05,
  mach: 1.5,
  altitude: 0,

  thrust: 150,
  burn: 2.5,
  wind: 5,

  unit: "m",
  mode: "sliders",
  preset: "Custom",

  analysis: null,
  trajectory: null,
  sweep: null,
  optimization: null,

  backendHealthy: false,
  backendError: null,

  lastAnalysisId: 0,
  lastTrajectoryId: 0,
  lastSweepId: 0,
};

/* ============================================================
   PRESETS
   ============================================================ */

const presets = {
  Custom: {
    length: 0.5,
    radius: 0.05,
    mach: 1.5,
    thrust: 150,
    burn: 2.5,
    wind: 5,
  },

  "Sounding Rocket (Terrier-Orion)": {
    length: 1.2,
    radius: 0.17,
    mach: 2.5,
    thrust: 1800,
    burn: 6,
    wind: 8,
  },

  "Model Rocket (Estes Alpha)": {
    length: 0.15,
    radius: 0.015,
    mach: 0.3,
    thrust: 15,
    burn: 0.8,
    wind: 3,
  },

  "Hypersonic Penetrator": {
    length: 2.5,
    radius: 0.12,
    mach: 5.2,
    thrust: 800,
    burn: 4,
    wind: 10,
  },

  "FPV Racing Drone Arm": {
    length: 0.08,
    radius: 0.008,
    mach: 0.15,
    thrust: 5,
    burn: 0.2,
    wind: 2,
  },
};

/* ============================================================
   TIMERS
   ============================================================ */

const REALTIME_DEBOUNCE_MS = 450;

let realtimeTimer = null;
let resizeTimer = null;
let toastTimer = null;

/* ============================================================
   HELPERS
   ============================================================ */

const $ = (id) =>
  document.getElementById(id);

function setText(
  id,
  value,
) {
  const element = $(id);

  if (element) {
    element.textContent = value;
  }
}

function fmt(
  value,
  decimals = 2,
) {
  const number =
    Number(value);

  return Number.isFinite(number)
    ? number.toFixed(decimals)
    : "—";
}

function clamp(
  value,
  min,
  max,
) {
  return Math.min(
    Math.max(value, min),
    max,
  );
}

function css(
  variable,
  fallback,
) {
  return (
    getComputedStyle(
      document.documentElement,
    )
      .getPropertyValue(variable)
      .trim() ||
    fallback
  );
}

function svgEl(
  tag,
  attributes = {},
) {
  const element =
    document.createElementNS(
      "http://www.w3.org/2000/svg",
      tag,
    );

  Object.entries(
    attributes,
  ).forEach(
    ([key, value]) => {
      element.setAttribute(
        key,
        value,
      );
    },
  );

  return element;
}

function isAbort(error) {
  return (
    error?.name ===
      "AbortError" ||
    error?.name ===
      "StaleResponseError"
  );
}

function getApi(
  name,
  fallback,
) {
  return (
    window.AeroOptXAPI?.[
      name
    ] ||
    window[fallback] ||
    null
  );
}

function analyzeApi() {
  return getApi(
    "analyze",
    "analyzeAeroOptX",
  );
}

function optimizeApi() {
  return getApi(
    "optimize",
    "optimizeAeroOptX",
  );
}

function trajectoryApi() {
  return getApi(
    "trajectory",
    "runTrajectoryAeroOptX",
  );
}

function sweepApi() {
  return getApi(
    "sweep",
    "runSweepAeroOptX",
  );
}

function healthApi() {
  return getApi(
    "health",
    "checkAeroOptXHealth",
  );
}

/* ============================================================
   TOAST
   ============================================================ */

function showToast(
  message,
) {
  const toast =
    $("toast");

  const toastMsg =
    $("toastMsg");

  if (
    !toast ||
    !toastMsg
  ) {
    return;
  }

  toastMsg.textContent =
    message;

  toast.classList.add(
    "show",
  );

  clearTimeout(
    toastTimer,
  );

  toastTimer =
    setTimeout(
      () => {
        toast.classList.remove(
          "show",
        );
      },
      3200,
    );
}

/* ============================================================
   SLIDER UI
   ============================================================ */

function syncSliderFill(
  slider,
) {
  if (!slider) {
    return;
  }

  const min =
    Number(slider.min);

  const max =
    Number(slider.max);

  const value =
    Number(slider.value);

  if (
    !Number.isFinite(min) ||
    !Number.isFinite(max) ||
    max <= min
  ) {
    return;
  }

  const percent =
    clamp(
      (
        (value - min) /
        (max - min)
      ) * 100,
      0,
      100,
    );

  slider.style.backgroundImage =
    `linear-gradient(
      to right,
      var(--accent) 0%,
      var(--accent) ${percent}%,
      var(--border-strong) ${percent}%,
      var(--border-strong) 100%
    )`;
}

function syncControls() {
  const controls = [
    [
      "length",
      "lengthVal",
      2,
      " m",
    ],

    [
      "radius",
      "radiusVal",
      3,
      " m",
    ],

    [
      "mach",
      "machVal",
      2,
      "",
    ],

    [
      "thrust",
      "thrustVal",
      2,
      " N",
    ],

    [
      "burn",
      "burnVal",
      2,
      " s",
    ],

    [
      "wind",
      "windVal",
      2,
      " m/s",
    ],
  ];

  controls.forEach(
    ([
      key,
      label,
      decimals,
      suffix,
    ]) => {
      const slider =
        $(key);

      if (slider) {
        slider.value =
          clamp(
            Number(
              state[key],
            ),
            Number(
              slider.min,
            ),
            Number(
              slider.max,
            ),
          );

        syncSliderFill(
          slider,
        );
      }

      const exact =
        $(
          `${key}Exact`,
        );

      if (exact) {
        exact.value =
          state[key];
      }

      setText(
        label,
        `${fmt(
          state[key],
          decimals,
        )}${suffix}`,
      );
    },
  );

  const altitude =
    $("altitude");

  if (altitude) {
    altitude.value =
      state.altitude;
  }

  setText(
    "presetLabel",
    state.preset,
  );

  setText(
    "crumbPreset",
    state.preset,
  );

  setText(
    "in-preset",
    state.preset,
  );
}

/* ============================================================
   CLEAR RESULTS
   ============================================================ */

function clearResults() {
  [
    "val-sh",
    "val-vk",
    "val-to",
    "in-fr",
    "val-temp",
    "val-shock",
    "val-apogee",
    "val-downrange",
    "val-flight-time",
    "val-max-velocity",
    "val-ambient-temp",
    "val-air-density",
    "val-speed-sound",
  ].forEach(
    (id) =>
      setText(
        id,
        "—",
      ),
  );

  setText(
    "in-eff",
    "Awaiting analysis.",
  );

  setText(
    "thermalStatus",
    "Awaiting backend analysis.",
  );

  setText(
    "thermalInterpretation",
    "Run an aerodynamic analysis to calculate atmospheric and aerothermal results.",
  );

  setText(
    "badge-temp-k",
    "Awaiting analysis",
  );

  setText(
    "badge-shock",
    "Awaiting analysis",
  );

  setText(
    "badge-downrange",
    "Awaiting simulation",
  );

  const shockView =
    $("shockView");

  if (shockView) {
    shockView.innerHTML =
      "";
  }

  window.drawHeatmapEmpty?.();
}

/* ============================================================
   METRICS
   ============================================================ */

function setMetricLoading() {
  [
    "val-sh",
    "val-vk",
    "val-to",
  ].forEach(
    (id) =>
      setText(
        id,
        "…",
      ),
  );
}

function renderMetrics() {
  const drag =
    state.analysis?.drag;

  if (!drag) {
    return;
  }

  const values = {
    sh:
      Number(
        drag.sears_haack,
      ),

    vk:
      Number(
        drag.von_karman,
      ),

    to:
      Number(
        drag.ogive,
      ),
  };

  setText(
    "val-sh",
    fmt(
      values.sh,
      6,
    ),
  );

  setText(
    "val-vk",
    fmt(
      values.vk,
      6,
    ),
  );

  setText(
    "val-to",
    fmt(
      values.to,
      6,
    ),
  );

  [
    "sh",
    "vk",
    "to",
  ].forEach(
    (key) => {
      $(
        `tile-${key}`,
      )?.classList.remove(
        "best",
      );
    },
  );

  const valid =
    Object.keys(
      values,
    ).filter(
      (key) =>
        Number.isFinite(
          values[key],
        ),
    );

  if (valid.length) {
    const bestKey =
      valid.reduce(
        (
          best,
          key,
        ) =>
          values[key] <
          values[best]
            ? key
            : best,
      );

    $(
      `tile-${bestKey}`,
    )?.classList.add(
      "best",
    );

    const names = {
      sh:
        "Sears-Haack",

      vk:
        "Von Kármán",

      to:
        "Tangent Ogive",
    };

    const best =
      values[bestKey];

    const worst =
      Math.max(
        ...valid.map(
          (key) =>
            values[key],
        ),
      );

    const improvement =
      worst > 0
        ? (
            (
              worst -
              best
            ) /
            worst
          ) *
          100
        : 0;

    setText(
      "in-eff",
      `${names[bestKey]} has ${fmt(
        improvement,
        1,
      )}% lower drag than the highest-drag profile.`,
    );
  }

  const fineness =
    state.length /
    Math.max(
      2 *
        state.radius,
      1e-12,
    );

  setText(
    "in-fr",
    fmt(
      fineness,
      2,
    ),
  );
}

/* ============================================================
   THERMAL ANALYSIS
   ============================================================ */

function getThermalStatus(
  temperatureK,
  mach,
) {
  if (
    !Number.isFinite(
      temperatureK,
    )
  ) {
    return {
      label:
        "No data",

      text:
        "No aerothermal result is available.",
    };
  }

  if (
    mach < 1
  ) {
    return {
      label:
        "Subsonic / low thermal loading",

      text:
        "The current Mach number is below the supersonic regime, so strong shock heating is not expected from this simplified model.",
    };
  }

  if (
    temperatureK <
    500
  ) {
    return {
      label:
        "Moderate thermal loading",

      text:
        "Thermal loading is present but the predicted stagnation temperature remains in a comparatively moderate range.",
    };
  }

  if (
    temperatureK <
    1000
  ) {
    return {
      label:
        "High thermal loading",

      text:
        "The predicted stagnation temperature is elevated. Material selection and thermal protection become important design considerations.",
    };
  }

  if (
    temperatureK <
    1500
  ) {
    return {
      label:
        "Very high thermal loading",

      text:
        "The vehicle nose is operating in a severe heating regime. High-temperature structural and thermal-protection materials should be evaluated.",
    };
  }

  return {
    label:
      "Extreme thermal loading",

    text:
      "The simplified analysis predicts an extreme stagnation-temperature environment. Detailed real-gas, material, and heat-transfer analysis is recommended.",
  };
}

function renderThermal() {
  const thermal =
    state.analysis?.thermal;

  const atmosphere =
    state.analysis?.atmosphere;

  if (!thermal) {
    return;
  }

  const temperatureK =
    Number(
      thermal.stagnation_temperature_k,
    );

  const shockAngle =
    Number(
      thermal.shock_angle_deg,
    );

  const ambientK =
    Number(
      atmosphere?.ambient_temperature_k ??
      thermal.ambient_temperature_k,
    );

  const density =
    Number(
      atmosphere?.air_density_kg_m3,
    );

  const speedSound =
    Number(
      atmosphere?.speed_of_sound_m_s,
    );

  setText(
    "val-temp",
    Number.isFinite(
      temperatureK,
    )
      ? `${fmt(
          temperatureK -
            273.15,
          1,
        )} °C`
      : "—",
  );

  setText(
    "val-shock",
    Number.isFinite(
      shockAngle,
    ) &&
    state.mach > 1
      ? `${fmt(
          shockAngle,
          1,
        )}°`
      : "No attached shock",
  );

  setText(
    "val-ambient-temp",
    Number.isFinite(
      ambientK,
    )
      ? `${fmt(
          ambientK -
            273.15,
          1,
        )} °C`
      : "—",
  );

  setText(
    "val-air-density",
    Number.isFinite(
      density,
    )
      ? `${fmt(
          density,
          4,
        )} kg/m³`
      : "—",
  );

  setText(
    "val-speed-sound",
    Number.isFinite(
      speedSound,
    )
      ? `${fmt(
          speedSound,
          1,
        )} m/s`
      : "—",
  );

  const status =
    getThermalStatus(
      temperatureK,
      state.mach,
    );

  setText(
    "thermalStatus",
    status.label,
  );

  setText(
    "thermalInterpretation",
    status.text,
  );

  const tempBadge =
    $("badge-temp-k");

  if (tempBadge) {
    tempBadge.textContent =
      Number.isFinite(
        temperatureK,
      )
        ? `${fmt(
            temperatureK,
            1,
          )} K`
        : "—";
  }

  const shockBadge =
    $("badge-shock");

  if (shockBadge) {
    shockBadge.textContent =
      state.mach > 1 &&
      Number.isFinite(
        shockAngle,
      )
        ? "Supersonic shock solution"
        : "Subsonic regime";
  }

  renderShockView(
    shockAngle,
  );
}

function renderShockView(
  shockAngle,
) {
  const svg =
    $("shockView");

  if (!svg) {
    return;
  }

  svg.innerHTML =
    "";

  const W = 900;
  const H = 280;

  const noseX = 390;
  const noseY = 140;

  const border =
    css(
      "--border",
      "#26303D",
    );

  const accent =
    css(
      "--accent",
      "#FF6A3D",
    );

  const teal =
    css(
      "--teal",
      "#33D6C0",
    );

  for (
    let y = 30;
    y < H;
    y += 30
  ) {
    svg.appendChild(
      svgEl(
        "line",
        {
          x1: 25,
          y1: y,

          x2: W - 25,
          y2: y,

          stroke:
            border,

          opacity:
            0.3,

          "stroke-width":
            1,
        },
      ),
    );
  }

  /* Incoming flow */

  for (
    let y = 60;
    y <= 220;
    y += 40
  ) {
    svg.appendChild(
      svgEl(
        "line",
        {
          x1: 40,
          y1: y,

          x2: 260,
          y2: y,

          stroke:
            teal,

          opacity:
            0.45,

          "stroke-width":
            2,

          "stroke-dasharray":
            "8 8",
        },
      ),
    );
  }

  /* Nose cone */

  svg.appendChild(
    svgEl(
      "path",
      {
        d:
          `M ${noseX} ${noseY}
           L 680 85
           L 680 195
           Z`,

        fill:
          accent,

        opacity:
          0.9,
      },
    ),
  );

  if (
    state.mach > 1 &&
    Number.isFinite(
      shockAngle,
    ) &&
    shockAngle > 0
  ) {
    const beta =
      (
        shockAngle *
        Math.PI
      ) /
      180;

    const run = 260;

    const spread =
      Math.min(
        125,
        Math.tan(
          beta,
        ) *
          90,
      );

    svg.appendChild(
      svgEl(
        "path",
        {
          d:
            `M ${noseX} ${noseY}
             L ${noseX - run} ${noseY - spread}
             M ${noseX} ${noseY}
             L ${noseX - run} ${noseY + spread}`,

          fill:
            "none",

          stroke:
            teal,

          "stroke-width":
            3,

          "stroke-dasharray":
            "9 7",
        },
      ),
    );

    const label =
      svgEl(
        "text",
        {
          x:
            noseX - 180,

          y:
            noseY - spread - 12,

          fill:
            teal,

          "font-size":
            16,

          "font-family":
            "Inter, sans-serif",
        },
      );

    label.textContent =
      `β = ${fmt(
        shockAngle,
        1,
      )}°`;

    svg.appendChild(
      label,
    );
  } else {
    const label =
      svgEl(
        "text",
        {
          x: 60,
          y: 40,

          fill:
            css(
              "--text-muted",
              "#8E9AAF",
            ),

          "font-size":
            16,
        },
      );

    label.textContent =
      "No attached oblique shock is predicted below Mach 1.";

    svg.appendChild(
      label,
    );
  }
}

/* ============================================================
   VIEWPORT
   ============================================================ */

function renderViewport() {
  const geometry =
    state.analysis?.geometry;

  if (!geometry) {
    return;
  }

  window.renderNoseCone3D?.(
    geometry.x,
    geometry.sears_haack,
  );
}

/* ============================================================
   TRAJECTORY
   ============================================================ */

function renderTrajectory() {
  const result =
    state.trajectory;

  const summary =
    result?.summary;

  if (!summary) {
    return;
  }

  setText(
    "val-apogee",
    `${fmt(
      summary.apogee_m,
      1,
    )} m`,
  );

  setText(
    "val-downrange",
    `${fmt(
      summary.downrange_m,
      1,
    )} m`,
  );

  setText(
    "val-flight-time",
    `${fmt(
      summary.flight_time_s,
      2,
    )} s`,
  );

  setText(
    "val-max-velocity",
    `${fmt(
      summary.max_velocity_m_s,
      1,
    )} m/s`,
  );

  const badge =
    $("badge-downrange");

  if (badge) {
    badge.textContent =
      `Apogee at ${fmt(
        summary.apogee_time_s,
        2,
      )} s`;
  }

  window.renderTrajectoryChart?.(
    result.trajectory,
  );
}

/* ============================================================
   SWEEP
   ============================================================ */

function renderSweep() {
  const sweep =
    state.sweep?.sweep;

  if (!sweep) {
    return;
  }

  window.renderBackendHeatmap?.(
    sweep,
  );

  const grid =
    sweep.drag_factor;

  if (
    !Array.isArray(grid)
  ) {
    return;
  }

  const values =
    grid
      .flat()
      .map(Number)
      .filter(
        Number.isFinite,
      );

  if (!values.length) {
    return;
  }

  const minimum =
    Math.min(
      ...values,
    );

  const maximum =
    Math.max(
      ...values,
    );

  setText(
    "sweepMin",
    fmt(
      minimum,
      6,
    ),
  );

  setText(
    "sweepMax",
    fmt(
      maximum,
      6,
    ),
  );
}

/* ============================================================
   FULL RENDER
   ============================================================ */

function renderAll() {
  renderMetrics();

  renderThermal();

  renderViewport();

  renderTrajectory();

  renderSweep();

  if (
    state.analysis?.geometry
  ) {
    window.renderBackendProfile?.(
      state.analysis.geometry,
    );
  }
}

/* ============================================================
   BACKEND JOBS
   ============================================================ */

async function runAnalysis(
  {
    silent = true,
  } = {},
) {
  const api =
    analyzeApi();

  if (
    typeof api !==
    "function"
  ) {
    if (!silent) {
      showToast(
        "Analysis API is unavailable.",
      );
    }

    return null;
  }

  const requestId =
    ++state.lastAnalysisId;

  setMetricLoading();

  try {
    const result =
      await api({
        length:
          Number(
            state.length,
          ),

        radius:
          Number(
            state.radius,
          ),

        mach:
          Number(
            state.mach,
          ),

        altitude:
          Number(
            state.altitude,
          ),
      });

    if (
      requestId !==
      state.lastAnalysisId
    ) {
      return null;
    }

    state.analysis =
      result;

    state.optimization =
      result.optimization ||
      null;

    state.backendHealthy =
      true;

    state.backendError =
      null;

    renderAll();

    if (!silent) {
      showToast(
        "AeroOpt-X analysis completed.",
      );
    }

    return result;
  } catch (error) {
    if (
      isAbort(
        error,
      )
    ) {
      return null;
    }

    state.backendHealthy =
      false;

    state.backendError =
      error;

    console.error(
      "Analysis failed:",
      error,
    );

    if (!silent) {
      showToast(
        error.message ||
          "Analysis failed.",
      );
    }

    return null;
  }
}

async function runOptimization(
  {
    silent = false,
  } = {},
) {
  const api =
    optimizeApi();

  if (
    typeof api !==
    "function"
  ) {
    return runAnalysis({
      silent,
    });
  }

  try {
    const result =
      await api({
        length:
          state.length,

        radius:
          state.radius,

        mach:
          state.mach,

        altitude:
          state.altitude,
      });

    state.optimization =
      result.optimization ||
      result;

    if (
      result.geometry &&
      state.analysis
    ) {
      state.analysis.geometry =
        {
          ...state.analysis
            .geometry,

          ...result.geometry,
        };
    }

    if (!silent) {
      showToast(
        `Optimization complete — K = ${fmt(
          result.optimal_k ??
            result.optimization
              ?.optimal_k,
          5,
        )}`,
      );
    }

    return result;
  } catch (error) {
    if (
      isAbort(
        error,
      )
    ) {
      return null;
    }

    if (!silent) {
      showToast(
        error.message ||
          "Optimization failed.",
      );
    }

    return null;
  }
}

async function runTrajectory(
  {
    silent = true,
  } = {},
) {
  const api =
    trajectoryApi();

  if (
    typeof api !==
    "function"
  ) {
    return null;
  }

  const requestId =
    ++state.lastTrajectoryId;

  try {
    const result =
      await api({
        thrust:
          state.thrust,

        burn:
          state.burn,

        wind:
          state.wind,
      });

    if (
      requestId !==
      state.lastTrajectoryId
    ) {
      return null;
    }

    state.trajectory =
      result;

    renderTrajectory();

    if (!silent) {
      showToast(
        "Trajectory simulation completed.",
      );
    }

    return result;
  } catch (error) {
    if (
      isAbort(
        error,
      )
    ) {
      return null;
    }

    if (!silent) {
      showToast(
        error.message ||
          "Trajectory simulation failed.",
      );
    }

    return null;
  }
}

async function runSweep(
  {
    silent = true,
  } = {},
) {
  const api =
    sweepApi();

  if (
    typeof api !==
    "function"
  ) {
    return null;
  }

  const requestId =
    ++state.lastSweepId;

  try {
    const result =
      await api({
        mach_min:
          0.3,

        mach_max:
          Math.max(
            6,
            state.mach,
          ),

        fineness_min:
          2,

        fineness_max:
          12,

        grid_size:
          50,
      });

    if (
      requestId !==
      state.lastSweepId
    ) {
      return null;
    }

    state.sweep =
      result;

    renderSweep();

    if (!silent) {
      showToast(
        "Parametric sweep completed.",
      );
    }

    return result;
  } catch (error) {
    if (
      isAbort(
        error,
      )
    ) {
      return null;
    }

    if (!silent) {
      showToast(
        error.message ||
          "Parametric sweep failed.",
      );
    }

    return null;
  }
}

/* ============================================================
   REALTIME SCHEDULING
   ============================================================ */

function scheduleRealtime(
  {
    analysis = false,
    trajectory = false,
    sweep = false,
  } = {},
) {
  clearTimeout(
    realtimeTimer,
  );

  realtimeTimer =
    setTimeout(
      async () => {
        const jobs = [];

        if (analysis) {
          jobs.push(
            runAnalysis(),
          );
        }

        if (trajectory) {
          jobs.push(
            runTrajectory(),
          );
        }

        if (sweep) {
          jobs.push(
            runSweep(),
          );
        }

        await Promise.all(
          jobs,
        );
      },
      REALTIME_DEBOUNCE_MS,
    );
}

/* ============================================================
   INPUTS
   ============================================================ */

function readInput(
  key,
  value,
) {
  const number =
    Number(value);

  if (
    !Number.isFinite(
      number,
    )
  ) {
    return false;
  }

  state[key] =
    number;

  if (
    [
      "length",
      "radius",
      "mach",
    ].includes(
      key,
    )
  ) {
    state.preset =
      "Custom";
  }

  syncControls();

  return true;
}

[
  "length",
  "radius",
  "mach",
].forEach(
  (key) => {
    $(key)?.addEventListener(
      "input",
      (event) => {
        if (
          readInput(
            key,
            event.target
              .value,
          )
        ) {
          scheduleRealtime({
            analysis:
              true,

            sweep:
              true,
          });
        }
      },
    );
  },
);

[
  "thrust",
  "burn",
  "wind",
].forEach(
  (key) => {
    $(key)?.addEventListener(
      "input",
      (event) => {
        if (
          readInput(
            key,
            event.target
              .value,
          )
        ) {
          scheduleRealtime({
            trajectory:
              true,
          });
        }
      },
    );
  },
);

[
  "length",
  "radius",
  "mach",
].forEach(
  (key) => {
    const exact =
      $(
        `${key}Exact`,
      );

    exact?.addEventListener(
      "change",
      (event) => {
        if (
          readInput(
            key,
            event.target
              .value,
          )
        ) {
          scheduleRealtime({
            analysis:
              true,

            sweep:
              true,
          });
        }
      },
    );
  },
);

$("altitude")?.addEventListener(
  "input",
  (event) => {
    if (
      readInput(
        "altitude",
        event.target
          .value,
      )
    ) {
      scheduleRealtime({
        analysis:
          true,
      });
    }
  },
);

$("altPlus")?.addEventListener(
  "click",
  () => {
    state.altitude =
      Math.max(
        0,
        Number(
          state.altitude,
        ) + 10,
      );

    syncControls();

    scheduleRealtime({
      analysis:
        true,
    });
  },
);

$("altMinus")?.addEventListener(
  "click",
  () => {
    state.altitude =
      Math.max(
        0,
        Number(
          state.altitude,
        ) - 10,
      );

    syncControls();

    scheduleRealtime({
      analysis:
        true,
    });
  },
);

/* ============================================================
   BUTTON LOADING
   ============================================================ */

function setButtonLoading(
  button,
  loading,
  text = "Working…",
) {
  if (!button) {
    return () => {};
  }

  if (
    !button.dataset
      .originalHtml
  ) {
    button.dataset.originalHtml =
      button.innerHTML;
  }

  button.disabled =
    loading;

  button.innerHTML =
    loading
      ? `<svg class="icon sm">
           <use href="#i-zap"></use>
         </svg>
         ${text}`
      : button.dataset
          .originalHtml;

  return () =>
    setButtonLoading(
      button,
      false,
    );
}

/* ============================================================
   MAIN BUTTONS
   ============================================================ */

$("analyzeBtn")?.addEventListener(
  "click",
  async function () {
    clearTimeout(
      realtimeTimer,
    );

    const restore =
      setButtonLoading(
        this,
        true,
        "Analyzing…",
      );

    try {
      await Promise.all([
        runAnalysis({
          silent: false,
        }),

        runTrajectory({
          silent: true,
        }),

        runSweep({
          silent: true,
        }),
      ]);
    } finally {
      restore();
    }
  },
);

$("runOptBtn")?.addEventListener(
  "click",
  async function () {
    const restore =
      setButtonLoading(
        this,
        true,
        "Optimizing…",
      );

    try {
      await runOptimization({
        silent: false,
      });

      await runAnalysis({
        silent: true,
      });
    } finally {
      restore();
    }
  },
);

/* ============================================================
   PRESETS
   ============================================================ */

function renderPresetMenu() {
  const menu =
    $("presetMenu");

  if (!menu) {
    return;
  }

  menu.innerHTML =
    "";

  Object.keys(
    presets,
  ).forEach(
    (name) => {
      const button =
        document.createElement(
          "button",
        );

      button.type =
        "button";

      button.textContent =
        name;

      button.classList.toggle(
        "active",
        name ===
          state.preset,
      );

      button.addEventListener(
        "click",
        () =>
          applyPreset(
            name,
          ),
      );

      menu.appendChild(
        button,
      );
    },
  );
}

function applyPreset(
  name,
) {
  const preset =
    presets[name];

  if (!preset) {
    return;
  }

  Object.assign(
    state,
    preset,
  );

  state.preset =
    name;

  state.analysis =
    null;

  state.trajectory =
    null;

  state.sweep =
    null;

  state.optimization =
    null;

  syncControls();

  clearResults();

  renderPresetMenu();

  const menu =
    $("presetMenu");

  if (menu) {
    menu.style.display =
      "none";
  }

  scheduleRealtime({
    analysis:
      true,

    trajectory:
      true,

    sweep:
      true,
  });

  showToast(
    `Loaded preset — ${name}`,
  );
}

$("presetToggle")?.addEventListener(
  "click",
  () => {
    const menu =
      $("presetMenu");

    if (!menu) {
      return;
    }

    menu.style.display =
      menu.style.display ===
        "block"
        ? "none"
        : "block";
  },
);

/* ============================================================
   TABS
   ============================================================ */

function activateTab(
  tabName,
) {
  document
    .querySelectorAll(
      ".tab, .nav-item",
    )
    .forEach(
      (element) => {
        element.classList.toggle(
          "active",
          element.dataset
            .tab ===
            tabName,
        );
      },
    );

  document
    .querySelectorAll(
      ".panel",
    )
    .forEach(
      (element) => {
        element.classList.toggle(
          "active",
          element.id ===
            `panel-${tabName}`,
        );
      },
    );

  if (
    tabName ===
      "sweeps" &&
    !state.sweep
  ) {
    runSweep();
  }

  requestAnimationFrame(
    renderAll,
  );
}

document
  .querySelectorAll(
    ".tab, .nav-item",
  )
  .forEach(
    (button) => {
      button.addEventListener(
        "click",
        () =>
          activateTab(
            button.dataset
              .tab,
          ),
      );
    },
  );

/* ============================================================
   INPUT MODE
   ============================================================ */

document
  .querySelectorAll(
    "#modeSeg button",
  )
  .forEach(
    (button) => {
      button.addEventListener(
        "click",
        () => {
          state.mode =
            button.dataset
              .mode;

          document
            .querySelectorAll(
              "#modeSeg button",
            )
            .forEach(
              (
                item,
              ) => {
                item.classList.toggle(
                  "active",
                  item ===
                    button,
                );
              },
            );

          const sliders =
            $("sliderInputs");

          const exact =
            $("exactInputs");

          if (
            sliders
          ) {
            sliders.style.display =
              state.mode ===
              "sliders"
                ? "block"
                : "none";
          }

          if (
            exact
          ) {
            exact.style.display =
              state.mode ===
              "exact"
                ? "grid"
                : "none";
          }
        },
      );
    },
);

/* ============================================================
   THEME
   ============================================================ */

$("themeSwitch")?.addEventListener(
  "click",
  () => {
    const html =
      document.documentElement;

    const next =
      html.getAttribute(
        "data-theme",
      ) === "dark"
        ? "light"
        : "dark";

    html.setAttribute(
      "data-theme",
      next,
    );

    const icon =
      $("themeIcon");

    if (icon) {
      icon.innerHTML =
        `<use href="#i-${next === "dark"
          ? "moon"
          : "sun"}"></use>`;
    }

    setTimeout(
      renderAll,
      50,
    );
  },
);

/* ============================================================
   DOCUMENTATION / HELP
   ============================================================ */

$("documentationBtn")?.addEventListener(
  "click",
  () => {
    window.location.href =
      "/documentation";
  },
);

$("helpBtn")?.addEventListener(
  "click",
  () => {
    window.location.href =
      "/help";
  },
);

/* ============================================================
   SIDEBAR
   ============================================================ */

function closeSidebarMobile() {
  const sidebar =
    $("sidebar");

  const overlay =
    $("overlay");

  const hamburger =
    $("hamburger");

  sidebar?.classList.remove(
    "open",
  );

  overlay?.classList.remove(
    "show",
  );

  hamburger?.setAttribute(
    "aria-expanded",
    "false",
  );
}

$("hamburger")?.addEventListener(
  "click",
  () => {
    const sidebar =
      $("sidebar");

    const overlay =
      $("overlay");

    const open =
      sidebar?.classList.toggle(
        "open",
      );

    overlay?.classList.toggle(
      "show",
      Boolean(
        open,
      ),
    );

    $("hamburger")?.setAttribute(
      "aria-expanded",
      String(
        Boolean(
          open,
        ),
      ),
    );
  },
);

$("overlay")?.addEventListener(
  "click",
  closeSidebarMobile,
);

/* ============================================================
   EXPORT / DOWNLOAD
   ============================================================ */

function download(
  filename,
  content,
  type,
) {
  const blob =
    new Blob(
      [content],
      {
        type,
      },
    );

  const url =
    URL.createObjectURL(
      blob,
    );

  const anchor =
    document.createElement(
      "a",
    );

  anchor.href =
    url;

  anchor.download =
    filename;

  anchor.click();

  URL.revokeObjectURL(
    url,
  );
}

$("dlStl")?.addEventListener(
  "click",
  () => {
    showToast(
      "STL export is not yet generated by the current backend.",
    );
  },
);

$("dlCsv")?.addEventListener(
  "click",
  () => {
    const sweep =
      state.sweep?.sweep;

    if (!sweep) {
      showToast(
        "Run the backend sweep first.",
      );

      return;
    }

    const rows = [
      "fineness_ratio,mach,drag_factor",
    ];

    sweep.fineness_ratio
      .forEach(
        (
          fineness,
          row,
        ) => {
          sweep.mach.forEach(
            (
              mach,
              column,
            ) => {
              rows.push(
                `${fineness},${mach},${sweep.drag_factor[row][column]}`,
              );
            },
          );
        },
      );

    download(
      "aeroopt-x-sweep.csv",
      rows.join(
        "\n",
      ),
      "text/csv",
    );

    showToast(
      "Downloaded sweep data.",
    );
  },
);

$("dlReport")?.addEventListener(
  "click",
  () => {
    if (
      !state.analysis
    ) {
      showToast(
        "Run analysis before generating a report.",
      );

      return;
    }

    const analysis =
      state.analysis;

    const thermal =
      analysis.thermal ||
      {};

    const atmosphere =
      analysis.atmosphere ||
      {};

    const trajectory =
      state.trajectory
        ?.summary ||
      {};

    const report =
      `AEROOPT-X ENGINE REPORT
Generated by AeroOpt-X

PRESET
${state.preset}

INPUT CONFIGURATION
Length: ${fmt(state.length, 4)} m
Base Radius: ${fmt(state.radius, 5)} m
Mach Number: ${fmt(state.mach, 3)}
Altitude: ${fmt(state.altitude, 1)} m
Fineness Ratio: ${fmt(state.length / Math.max(2 * state.radius, 1e-12), 3)}

ATMOSPHERE
Ambient Temperature: ${fmt(atmosphere.ambient_temperature_k, 2)} K
Air Density: ${fmt(atmosphere.air_density_kg_m3, 5)} kg/m³
Speed of Sound: ${fmt(atmosphere.speed_of_sound_m_s, 2)} m/s

AERODYNAMICS
Sears-Haack Drag Factor: ${fmt(analysis.drag?.sears_haack, 8)}
Von Kármán Drag Factor: ${fmt(analysis.drag?.von_karman, 8)}
Tangent Ogive Drag Factor: ${fmt(analysis.drag?.ogive, 8)}
Optimized Parabolic Drag Factor: ${fmt(analysis.drag?.optimized_parabolic, 8)}

OPTIMIZATION
Method: ${analysis.optimization?.method || "—"}
Optimal K: ${fmt(analysis.optimization?.optimal_k, 8)}
Change vs Best Reference: ${fmt(analysis.optimization?.change_vs_best_reference_percent, 3)} %

AEROTHERMAL
Stagnation Temperature: ${fmt(thermal.stagnation_temperature_k, 2)} K
Oblique Shock Angle: ${fmt(thermal.shock_angle_deg, 2)} degrees

TRAJECTORY
Apogee: ${fmt(trajectory.apogee_m, 2)} m
Apogee Time: ${fmt(trajectory.apogee_time_s, 2)} s
Downrange: ${fmt(trajectory.downrange_m, 2)} m
Flight Time: ${fmt(trajectory.flight_time_s, 2)} s
Maximum Velocity: ${fmt(trajectory.max_velocity_m_s, 2)} m/s

BACKEND STATUS
Backend Available: ${state.backendHealthy ? "Yes" : "No"}
`;

    download(
      "aeroopt-x-report.txt",
      report,
      "text/plain",
    );

    showToast(
      "Downloaded AeroOpt-X report.",
    );
  },
);

/* ============================================================
   RESIZE
   ============================================================ */

window.addEventListener(
  "resize",
  () => {
    clearTimeout(
      resizeTimer,
    );

    resizeTimer =
      setTimeout(
        renderAll,
        150,
      );
  },
);

/* ============================================================
   STARTUP
   ============================================================ */

async function initializeBackend() {
  const api =
    healthApi();

  if (
    typeof api !==
    "function"
  ) {
    return false;
  }

  try {
    const health =
      await api();

    state.backendHealthy =
      health?.status ===
        "healthy" ||
      health?.healthy ===
        true;

    return state.backendHealthy;
  } catch (
    error
  ) {
    state.backendHealthy =
      false;

    state.backendError =
      error;

    console.warn(
      "Backend unavailable:",
      error,
    );

    return false;
  }
}

async function initializeApp() {
  renderPresetMenu();

  syncControls();

  clearResults();

  const healthy =
    await initializeBackend();

  if (!healthy) {
    showToast(
      "Backend unavailable. Start Flask to load real results.",
    );

    return;
  }

  await Promise.all([
    runAnalysis(),

    runTrajectory(),

    runSweep(),
  ]);
}

initializeApp();

/* ============================================================
   DEBUG ACCESS
   ============================================================ */

window.AeroOptXState =
  state;

window.AeroOptXApp = {
  state,

  analyze:
    runAnalysis,

  optimize:
    runOptimization,

  trajectory:
    runTrajectory,

  sweep:
    runSweep,

  redraw:
    renderAll,

  health:
    initializeBackend,
};
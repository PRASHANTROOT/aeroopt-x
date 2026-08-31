/* ============================================================
   AEROOPT-X API CLIENT
   app/static/js/api.js
   ============================================================ */

"use strict";

const API_BASE_URL = window.location.origin;
const API_TIMEOUT_MS = 30000;

const API_ENDPOINTS = {
  health: "/api/health",
  analyze: "/api/analyze",
  optimize: "/api/optimize",
  trajectory: "/api/trajectory",
  sweep: "/api/sweep",
};

/* ============================================================
   ACTIVE REQUESTS
   ============================================================ */

const activeControllers = {
  analysis: null,
  optimization: null,
  trajectory: null,
  sweep: null,
};

/* ============================================================
   REQUEST VERSIONS
   Prevent stale responses from overwriting newer responses.
   ============================================================ */

const requestVersions = {
  analysis: 0,
  optimization: 0,
  trajectory: 0,
  sweep: 0,
};

/* ============================================================
   VALIDATION
   ============================================================ */

function requireFiniteNumber(value, name, options = {}) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    throw new Error(`${name} must be a valid finite number.`);
  }

  if (options.minimum !== undefined && number < options.minimum) {
    throw new Error(
      `${name} must be greater than or equal to ${options.minimum}.`,
    );
  }

  if (options.maximum !== undefined && number > options.maximum) {
    throw new Error(
      `${name} must be less than or equal to ${options.maximum}.`,
    );
  }

  if (options.greaterThan !== undefined && number <= options.greaterThan) {
    throw new Error(`${name} must be greater than ${options.greaterThan}.`);
  }

  return number;
}

/* ============================================================
   CANCELLATION
   ============================================================ */

function cancelRequest(type) {
  const controller = activeControllers[type];

  if (!controller) {
    return;
  }

  try {
    controller.abort();
  } catch (error) {
    console.warn(`Unable to cancel ${type} request:`, error);
  }

  activeControllers[type] = null;
}

function cancelAllAeroOptXRequests() {
  Object.keys(activeControllers).forEach(cancelRequest);
}

/* ============================================================
   FETCH HELPER
   ============================================================ */

async function fetchJson(
  url,
  options = {},
  timeout = API_TIMEOUT_MS,
  channel = null,
) {
  if (channel) {
    cancelRequest(channel);
  }

  const controller = new AbortController();

  if (channel) {
    activeControllers[channel] = controller;
  }

  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    const contentType = response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();

      throw new Error(text || `Backend returned HTTP ${response.status}.`);
    }

    if (!response.ok) {
      throw new Error(
        data?.message ||
          data?.error ||
          `Request failed with HTTP ${response.status}.`,
      );
    }

    if (data?.status === "error") {
      throw new Error(
        data?.message || data?.error || "AeroOpt-X backend returned an error.",
      );
    }

    return data;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw error;
    }

    if (error instanceof TypeError) {
      throw new Error(
        "Cannot connect to AeroOpt-X backend. Make sure Flask is running.",
      );
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);

    if (channel && activeControllers[channel] === controller) {
      activeControllers[channel] = null;
    }
  }
}

/* ============================================================
   ANALYSIS API
   ============================================================ */

async function analyzeAeroOptX(payload = {}) {
  const body = {
    length: requireFiniteNumber(payload.length, "Length", {
      greaterThan: 0,
    }),

    radius: requireFiniteNumber(payload.radius, "Radius", {
      greaterThan: 0,
    }),

    mach: requireFiniteNumber(payload.mach, "Mach number", {
      greaterThan: 0,
    }),

    altitude: requireFiniteNumber(payload.altitude ?? 0, "Altitude", {
      minimum: 0,
    }),
  };

  requestVersions.analysis += 1;

  return fetchJson(
    `${API_BASE_URL}${API_ENDPOINTS.analyze}`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        Accept: "application/json",
      },

      body: JSON.stringify(body),
    },
    API_TIMEOUT_MS,
    "analysis",
  );
}

/* ============================================================
   OPTIMIZATION API
   ============================================================ */

async function optimizeAeroOptX(payload = {}) {
  const body = {
    length: requireFiniteNumber(payload.length, "Length", {
      greaterThan: 0,
    }),

    radius: requireFiniteNumber(payload.radius, "Radius", {
      greaterThan: 0,
    }),

    mach: requireFiniteNumber(payload.mach, "Mach number", {
      greaterThan: 0,
    }),

    altitude: requireFiniteNumber(payload.altitude ?? 0, "Altitude", {
      minimum: 0,
    }),
  };

  requestVersions.optimization += 1;

  return fetchJson(
    `${API_BASE_URL}${API_ENDPOINTS.optimize}`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        Accept: "application/json",
      },

      body: JSON.stringify(body),
    },
    API_TIMEOUT_MS,
    "optimization",
  );
}

/* ============================================================
   TRAJECTORY API
   ============================================================ */

async function simulateAeroOptXTrajectory(payload = {}) {
  const body = {
    thrust: requireFiniteNumber(payload.thrust ?? 150, "Thrust", {
      minimum: 0,
    }),

    burn_time: requireFiniteNumber(
      payload.burn_time ?? payload.burn ?? 2.5,
      "Burn duration",
      {
        greaterThan: 0,
      },
    ),

    wind_speed: requireFiniteNumber(
      payload.wind_speed ?? payload.wind ?? 0,
      "Wind speed",
      {
        minimum: 0,
      },
    ),

    dry_mass: requireFiniteNumber(payload.dry_mass ?? 1.5, "Dry mass", {
      greaterThan: 0,
    }),

    wet_mass: requireFiniteNumber(payload.wet_mass ?? 2.5, "Wet mass", {
      greaterThan: 0,
    }),

    drag_cd: requireFiniteNumber(payload.drag_cd ?? 0.15, "Drag coefficient", {
      minimum: 0,
    }),

    pitch_kick_time: requireFiniteNumber(
      payload.pitch_kick_time ?? 0.5,
      "Pitch kick time",
      {
        minimum: 0,
      },
    ),

    dt: requireFiniteNumber(payload.dt ?? 0.01, "Simulation time step", {
      greaterThan: 0,
    }),
  };

  if (body.wet_mass <= body.dry_mass) {
    throw new Error("Wet mass must be greater than dry mass.");
  }

  requestVersions.trajectory += 1;

  return fetchJson(
    `${API_BASE_URL}${API_ENDPOINTS.trajectory}`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        Accept: "application/json",
      },

      body: JSON.stringify(body),
    },
    API_TIMEOUT_MS,
    "trajectory",
  );
}

/* ============================================================
   PARAMETRIC SWEEP API
   ============================================================ */

async function runAeroOptXSweep(payload = {}) {
  const body = {
    mach_min: requireFiniteNumber(payload.mach_min ?? 0.5, "Minimum Mach", {
      greaterThan: 0,
    }),

    mach_max: requireFiniteNumber(payload.mach_max ?? 6, "Maximum Mach", {
      greaterThan: 0,
    }),

    fineness_min: requireFiniteNumber(
      payload.fineness_min ?? 2,
      "Minimum fineness ratio",
      {
        greaterThan: 0,
      },
    ),

    fineness_max: requireFiniteNumber(
      payload.fineness_max ?? 10,
      "Maximum fineness ratio",
      {
        greaterThan: 0,
      },
    ),

    grid_size: Math.round(
      requireFiniteNumber(payload.grid_size ?? 50, "Grid size", {
        minimum: 5,
        maximum: 100,
      }),
    ),
  };

  if (body.mach_max <= body.mach_min) {
    throw new Error("Maximum Mach must be greater than minimum Mach.");
  }

  if (body.fineness_max <= body.fineness_min) {
    throw new Error(
      "Maximum fineness ratio must be greater than minimum fineness ratio.",
    );
  }

  requestVersions.sweep += 1;

  return fetchJson(
    `${API_BASE_URL}${API_ENDPOINTS.sweep}`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",

        Accept: "application/json",
      },

      body: JSON.stringify(body),
    },
    API_TIMEOUT_MS,
    "sweep",
  );
}

/* ============================================================
   HEALTH
   ============================================================ */

async function checkAeroOptXHealth() {
  return fetchJson(
    `${API_BASE_URL}${API_ENDPOINTS.health}`,
    {
      method: "GET",

      headers: {
        Accept: "application/json",
      },
    },
    5000,
  );
}

async function isAeroOptXBackendAvailable() {
  try {
    await checkAeroOptXHealth();

    return true;
  } catch {
    return false;
  }
}

/* ============================================================
   PUBLIC API
   ============================================================ */

window.AeroOptXAPI = {
  analyze: analyzeAeroOptX,

  optimize: optimizeAeroOptX,

  trajectory: simulateAeroOptXTrajectory,

  sweep: runAeroOptXSweep,

  health: checkAeroOptXHealth,

  available: isAeroOptXBackendAvailable,

  cancel: {
    analysis: () => cancelRequest("analysis"),

    optimization: () => cancelRequest("optimization"),

    trajectory: () => cancelRequest("trajectory"),

    sweep: () => cancelRequest("sweep"),

    all: cancelAllAeroOptXRequests,
  },
};

/* ============================================================
   BACKWARD COMPATIBILITY
   ============================================================ */

window.analyzeAeroOptX = analyzeAeroOptX;

window.optimizeAeroOptX = optimizeAeroOptX;

window.runTrajectoryAeroOptX = simulateAeroOptXTrajectory;

window.simulateAeroOptXTrajectory = simulateAeroOptXTrajectory;

window.runSweepAeroOptX = runAeroOptXSweep;

window.runAeroOptXSweep = runAeroOptXSweep;

window.checkAeroOptXHealth = checkAeroOptXHealth;

window.cancelAeroOptXRequest = cancelRequest;

window.cancelAllAeroOptXRequests = cancelAllAeroOptXRequests;

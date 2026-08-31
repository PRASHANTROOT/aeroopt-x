/* ============================================================
   AEROOPT-X CHART ENGINE
   app/static/js/charts.js
   ============================================================ */

"use strict";

/* ============================================================
   HELPERS
   ============================================================ */

function chartColor(
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

function chartArray(values) {
  if (!Array.isArray(values)) {
    return [];
  }

  return values
    .map(Number)
    .filter(Number.isFinite);
}

function plotlyReady() {
  return (
    typeof window.Plotly !==
    "undefined"
  );
}

function plotConfig() {
  return {
    responsive: true,

    displaylogo: false,

    scrollZoom: true,

    displayModeBar: true,

    modeBarButtonsToRemove: [
      "lasso2d",
      "select2d",
    ],
  };
}

function baseLayout(height = 420) {
  const text =
    chartColor(
      "--text",
      "#E8EDF7",
    );

  const muted =
    chartColor(
      "--text-muted",
      "#8E9AAF",
    );

  const border =
    chartColor(
      "--border",
      "#26303D",
    );

  return {
    autosize: true,

    height,

    paper_bgcolor:
      "rgba(0,0,0,0)",

    plot_bgcolor:
      "rgba(0,0,0,0)",

    font: {
      family:
        "Inter, Arial, sans-serif",

      color: text,
    },

    margin: {
      l: 65,
      r: 30,
      t: 35,
      b: 60,
    },

    hoverlabel: {
      bgcolor:
        chartColor(
          "--panel",
          "#171D26",
        ),

      bordercolor:
        border,

      font: {
        color: text,
      },
    },

    xaxis: {
      color: muted,

      gridcolor:
        border,

      zerolinecolor:
        border,
    },

    yaxis: {
      color: muted,

      gridcolor:
        border,

      zerolinecolor:
        border,
    },
  };
}

/* ============================================================
   PROFILE COMPARISON
   ============================================================ */

function renderBackendProfile(
  geometry,
) {
  const chart =
    document.getElementById(
      "profileChart",
    );

  if (
    !chart ||
    !plotlyReady()
  ) {
    return;
  }

  const x =
    chartArray(
      geometry?.x,
    );

  if (!x.length) {
    return;
  }

  const profiles = [
    {
      name:
        "Sears-Haack",

      key:
        "sears_haack",
    },

    {
      name:
        "Von Kármán",

      key:
        "von_karman",
    },

    {
      name:
        "Tangent Ogive",

      key:
        "ogive",
    },

    {
      name:
        "Optimized Parabolic",

      key:
        "optimized_parabolic",
    },
  ];

  const traces =
    profiles
      .map(
        (
          profile,
          index,
        ) => {
          const y =
            chartArray(
              geometry[
                profile.key
              ],
            );

          if (
            y.length !==
            x.length
          ) {
            return null;
          }

          return {
            x,
            y,

            type:
              "scatter",

            mode:
              "lines",

            name:
              profile.name,

            line: {
              width:
                index === 3
                  ? 3
                  : 2,
            },

            hovertemplate:
              "<b>%{fullData.name}</b><br>" +
              "Length: %{x:.4f} m<br>" +
              "Radius: %{y:.5f} m" +
              "<extra></extra>",
          };
        },
      )
      .filter(Boolean);

  const layout =
    baseLayout(420);

  layout.hovermode =
    "x unified";

  layout.legend = {
    orientation:
      "h",

    y:
      1.08,

    x:
      0,
  };

  layout.xaxis.title =
    "Length (m)";

  layout.yaxis.title =
    "Radius (m)";

  Plotly.react(
    chart,
    traces,
    layout,
    plotConfig(),
  );
}

/* ============================================================
   3D NOSE CONE
   ============================================================ */

function renderNoseCone3D(
  xValues,
  radiusValues,
) {
  const chart =
    document.getElementById(
      "viewport3d",
    );

  if (
    !chart ||
    !plotlyReady()
  ) {
    return;
  }

  const x =
    chartArray(xValues);

  const radius =
    chartArray(radiusValues);

  if (
    x.length < 2 ||
    radius.length !== x.length
  ) {
    return;
  }

  const thetaCount = 50;

  const theta =
    Array.from(
      {
        length:
          thetaCount,
      },
      (_, i) =>
        (
          i /
          (thetaCount - 1)
        ) *
        Math.PI *
        2,
    );

  const X = [];
  const Y = [];
  const Z = [];

  for (
    let i = 0;
    i < theta.length;
    i++
  ) {
    const rowX = [];
    const rowY = [];
    const rowZ = [];

    for (
      let j = 0;
      j < x.length;
      j++
    ) {
      rowX.push(
        x[j],
      );

      rowY.push(
        radius[j] *
          Math.cos(
            theta[i],
          ),
      );

      rowZ.push(
        radius[j] *
          Math.sin(
            theta[i],
          ),
      );
    }

    X.push(rowX);
    Y.push(rowY);
    Z.push(rowZ);
  }

  const trace = {
    type:
      "surface",

    x: X,
    y: Y,
    z: Z,

    showscale: false,

    opacity:
      0.95,

    hovertemplate:
      "Length: %{x:.4f} m<br>" +
      "Y: %{y:.4f} m<br>" +
      "Z: %{z:.4f} m" +
      "<extra></extra>",
  };

  const text =
    chartColor(
      "--text",
      "#E8EDF7",
    );

  const layout = {
    autosize: true,

    height: 420,

    margin: {
      l: 0,
      r: 0,
      t: 20,
      b: 0,
    },

    paper_bgcolor:
      "rgba(0,0,0,0)",

    font: {
      color: text,
    },

    scene: {
      xaxis: {
        title:
          "Length (m)",
      },

      yaxis: {
        title:
          "Radius Y (m)",
      },

      zaxis: {
        title:
          "Radius Z (m)",
      },

      aspectmode:
        "data",

      camera: {
        eye: {
          x: 1.6,
          y: 1.4,
          z: 1.0,
        },
      },

      bgcolor:
        "rgba(0,0,0,0)",
    },
  };

  Plotly.react(
    chart,
    [trace],
    layout,
    plotConfig(),
  );
}

/* ============================================================
   TRAJECTORY
   ============================================================ */

function renderTrajectoryChart(
  trajectory,
) {
  const chart =
    document.getElementById(
      "trajChart",
    );

  if (
    !chart ||
    !plotlyReady()
  ) {
    return;
  }

  const x =
    chartArray(
      trajectory?.downrange_m,
    );

  const y =
    chartArray(
      trajectory?.altitude_m,
    );

  const velocity =
    chartArray(
      trajectory?.velocity_m_s,
    );

  const time =
    chartArray(
      trajectory?.time_s,
    );

  if (
    !x.length ||
    !y.length
  ) {
    return;
  }

  const traces = [
    {
      x,
      y,

      type:
        "scatter",

      mode:
        "lines",

      name:
        "Flight Path",

      line: {
        width: 3,
      },

      hovertemplate:
        "Downrange: %{x:.1f} m<br>" +
        "Altitude: %{y:.1f} m" +
        "<extra></extra>",
    },
  ];

  if (
    velocity.length ===
      x.length &&
    time.length ===
      x.length
  ) {
    traces.push({
      x,
      y,

      mode:
        "markers",

      type:
        "scatter",

      name:
        "Velocity Samples",

      marker: {
        size: 4,

        color:
          velocity,

        colorscale:
          "Turbo",

        showscale:
          true,

        colorbar: {
          title:
            "Velocity<br>m/s",
        },
      },

      customdata:
        time,

      hovertemplate:
        "Time: %{customdata:.2f} s<br>" +
        "Velocity: %{marker.color:.1f} m/s<br>" +
        "Altitude: %{y:.1f} m" +
        "<extra></extra>",
    });
  }

  const layout =
    baseLayout(430);

  layout.xaxis.title =
    "Downrange (m)";

  layout.yaxis.title =
    "Altitude (m)";

  layout.legend = {
    orientation:
      "h",

    y:
      1.08,
  };

  Plotly.react(
    chart,
    traces,
    layout,
    plotConfig(),
  );
}

/* ============================================================
   PARAMETRIC HEATMAP
   ============================================================ */

function renderBackendHeatmap(
  sweep,
) {
  const chart =
    document.getElementById(
      "heatmap",
    );

  if (
    !chart ||
    !plotlyReady()
  ) {
    return;
  }

  const mach =
    chartArray(
      sweep?.mach,
    );

  const fineness =
    chartArray(
      sweep?.fineness_ratio,
    );

  const drag =
    Array.isArray(
      sweep?.drag_factor,
    )
      ? sweep.drag_factor
      : [];

  if (
    !mach.length ||
    !fineness.length ||
    !drag.length
  ) {
    return;
  }

  const trace = {
    type:
      "heatmap",

    x:
      mach,

    y:
      fineness,

    z:
      drag,

    colorscale:
      "Turbo",

    colorbar: {
      title:
        "Drag Factor",
    },

    hovertemplate:
      "Mach: %{x:.2f}<br>" +
      "Fineness Ratio: %{y:.2f}<br>" +
      "Drag Factor: %{z:.6f}" +
      "<extra></extra>",
  };

  const layout =
    baseLayout(500);

  layout.xaxis.title =
    "Mach Number";

  layout.yaxis.title =
    "Fineness Ratio (L/D)";

  layout.margin = {
    l: 80,
    r: 70,
    t: 30,
    b: 65,
  };

  Plotly.react(
    chart,
    [trace],
    layout,
    plotConfig(),
  );
}

/* ============================================================
   EMPTY STATES
   ============================================================ */

function drawHeatmapEmpty() {
  const chart =
    document.getElementById(
      "heatmap",
    );

  if (
    !chart ||
    !plotlyReady()
  ) {
    return;
  }

  Plotly.purge(chart);

  const layout =
    baseLayout(500);

  layout.annotations = [
    {
      text:
        "Waiting for backend sweep data",

      x: 0.5,
      y: 0.5,

      xref:
        "paper",

      yref:
        "paper",

      showarrow:
        false,

      font: {
        size: 16,
      },
    },
  ];

  Plotly.react(
    chart,
    [],
    layout,
    {
      responsive: true,
      displayModeBar: false,
    },
  );
}

/* ============================================================
   EXPORTS
   ============================================================ */

window.renderBackendProfile =
  renderBackendProfile;

window.renderNoseCone3D =
  renderNoseCone3D;

window.renderTrajectoryChart =
  renderTrajectoryChart;

window.renderBackendHeatmap =
  renderBackendHeatmap;

window.drawHeatmapEmpty =
  drawHeatmapEmpty;
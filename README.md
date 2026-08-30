@"
# AeroOpt-X 🚀

> Automated 3D Aerodynamic Shape & Trajectory Optimization Engine for Aerospace Vehicles.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
![CI Status](https://github.com/PRASHANTROOT/aeroopt-x/actions/workflows/ci.yml/badge.svg)

## 📌 Overview

**AeroOpt-X** is an aerodynamic engineering toolkit built to parametrically design, analyze, and optimize high-speed rocket nose cones and multirotor drone arm profiles. By coupling **Barrowman Drag Equations**, **Sears-Haack distribution curves**, and **SciPy gradient minimization**, AeroOpt-X reduces wave and downwash drag while exporting ready-to-print 3D CAD (.STL) files.

---

## ✨ Core Features

- **🚀 Rocket Nose Cone Optimization:** Compares Sears-Haack, Von Kármán, and Tangent Ogive profiles to minimize supersonic wave drag.
- **🛸 Drone Arm Aerodynamics:** Evaluates symmetric teardrop cross-sections against baseline square tubes to reduce motor downwash drag.
- **⚡ SciPy Optimization Engine:** Uses gradient-based SLSQP optimization to compute ideal curvature parameters automatically.
- **📦 3D CAD (.STL) Generator:** Generates watertight 3D models of optimized nose cones for instant export to 3D slicers (Cura/PrusaSlicer) or CAD tools.
- **📊 Interactive Web UI:** Real-time parameter tuning via Streamlit and dark-mode Plotly visualizations.

---

## ⚙️ Architecture Pipeline

```text
[ Parametric Input ] ──► [ Aerodynamic Solver ] ──► [ SciPy Optimizer ]
 (Length, Radius)         (Wave Drag Factor)       (Gradient SLSQP)
         │                         │                       │
         ▼                         ▼                       ▼
  (Interactive Graph)       (Drag Comparison)       (3D CAD .STL Export)
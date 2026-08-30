@"
# AeroOpt-X 🚀

> **Automated 3D Aerodynamic Shape, CFD Streamline & Trajectory Optimization Engine for Aerospace Vehicles.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)
![CI Status](https://github.com/PRASHANTROOT/aeroopt-x/actions/workflows/ci.yml/badge.svg)

---

## 📌 Project Overview

**AeroOpt-X** is an end-to-end aerodynamic engineering suite designed to parametrically analyze, optimize, visualize, and simulate supersonic rocket nose cones and multirotor drone arm cross-sections. 

By bridging classical aerodynamic math (**Sears-Haack equations**, **Barrowman drag models**) with numerical solvers (**SciPy SLSQP minimization**) and real-time visualization tools, AeroOpt-X bridges the gap between theoretical fluid dynamics and physical CAD manufacturing.

---

## ✨ Key Capabilities & Modules

### 1. 🚀 Supersonic Rocket Nose Cone Drag Optimization
- Compares theoretical drag coefficients ($C_d$) across three primary geometry types: **Sears-Haack** (minimum wave drag), **Von Kármán**, and **Tangent Ogive**.
- Evaluates wave drag reduction across varying Mach numbers ($0.5 \le M \le 3.0$).

### 2. 🧊 Interactive In-Browser 3D Solid Mesh Viewport
- Renders fully rotational, zoomable 3D solid surface geometries directly inside the Streamlit web browser using Plotly parameterization.
- **3D CAD (.STL) Export:** Generates solid binary `.stl` mesh files for 3D printing (Cura, PrusaSlicer, Bambu Studio) or importing into CAD packages (SolidWorks, Fusion 360).

### 3. 🌊 CFD Streamline & Velocity Vector Field Visualizer
- Calculates flow field deflection, velocity gradients, and free-stream displacement around nose cone profiles.
- Generates 2D flow contour heatmaps demonstrating airflow behavior at subsonic ($M < 1.0$) and supersonic ($M > 1.0$) conditions.

### 4. 🛸 Multirotor Drone Arm Downwash Drag Reduction
- Analyzes motor downwash drag penalty on drone arms.
- Evaluates custom **symmetric teardrop airfoils** against standard unoptimized square tubes to maximize multirotor hover efficiency.

### 5. 📈 Flight Dynamics & Trajectory Simulator
- Simulates 1D vertical launch trajectories by solving time-dependent flight equations of motion ($F_{\text{net}} = F_{\text{thrust}} - F_{\text{gravity}} - F_{\text{drag}}$).
- Directly demonstrates how shape optimization translates to real-world performance gains by comparing **Peak Altitude (Apogee)** and velocity curves over time.

### 6. ⚡ Automated SciPy Optimization Loop
- Utilizes Sequential Least Squares Programming (SLSQP) to iteratively discover optimal parabolic curvature factors ($K$) for minimum wave drag.

---

## 🏗️ System Architecture

```text
                                  ┌───────────────────────────┐
                                  │   User Input Parameters   │
                                  │ (Length, Radius, Mach, etc)│
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │      AeroOpt-X Core Physics & Math            │
                        ├───────────────────────┬───────────────────────┤
                        │  NoseConeGenerator()  │  DroneArmGenerator()  │
                        │    DragSolver()       │  FlowVisualizer()     │
                        │  AeroOptimizer()      │ TrajectorySimulator() │
                        └───────────┬───────────┴───────────┬───────────┘
                                    │                       │
                                    ▼                       ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
│       Interactive Visualizations     │  │          Engineering Outputs         │
├──────────────────────────────────────┤  ├──────────────────────────────────────┤
│ • 3D Surface Mesh Viewport           │  │ • Mach Drag Coefficients (Cd)        │
│ • 2D Airflow CFD Streamlines         │  │ • Binary 3D Mesh STL Downloads       │
│ • Flight Altitude (Apogee) Trajectory│  │ • SLSQP Optimized Curvature Factor K │
└──────────────────────────────────────┘  └──────────────────────────────────────┘
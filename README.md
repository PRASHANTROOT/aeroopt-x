# AeroOpt-X 🚀

> **Interactive Aerodynamic Analysis, Optimization, Aerothermal Estimation and Flight Simulation Platform for Aerospace Engineering.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask-black?logo=flask)
![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75?logo=plotly)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Copyright](https://img.shields.io/badge/Copyright-All%20Rights%20Reserved-red)
---

# 📌 AeroOpt-X Overview

**AeroOpt-X** is an interactive aerospace engineering workspace designed for aerodynamic geometry analysis, drag estimation, numerical optimization, aerothermal calculations, shockwave estimation, flight trajectory simulation, and engineering visualization.

The application combines a Python-based engineering backend with an interactive browser-based dashboard.

AeroOpt-X currently provides tools for:

- Parametric nose cone generation
- Aerodynamic drag comparison
- Supersonic and hypersonic analysis
- Stagnation temperature estimation
- Shockwave angle estimation
- SciPy SLSQP optimization
- 2DOF flight trajectory simulation
- Parametric engineering sweeps
- Interactive Plotly visualizations
- Vehicle parameter presets
- Documentation and Help pages

The platform is intended primarily for:

- Educational exploration
- Aerospace engineering learning
- Conceptual vehicle design
- Numerical experimentation
- Engineering visualization
- Software development and research

---

# 1️⃣ Main UI / Dashboard Features

The AeroOpt-X dashboard provides a centralized workspace for configuring engineering parameters and viewing analysis results.

Main dashboard capabilities include:

- Vehicle preset selection
- Geometry parameter inputs
- Mach number configuration
- Altitude configuration
- Aerodynamic analysis controls
- Optimization controls
- Thermal analysis
- Shockwave analysis
- Flight trajectory simulation
- Parametric sweeps
- Interactive engineering charts
- Documentation navigation
- Help navigation

The dashboard is designed to allow users to move from engineering inputs to visual engineering results without requiring direct interaction with the backend API.

---

# 2️⃣ Nose Cone & Aerodynamic Analysis

AeroOpt-X generates and compares multiple nose cone geometries.

The current geometry engine includes profiles such as:

- Sears-Haack
- Von Kármán
- Ogive
- Optimized parabolic profile

The system generates coordinate-based geometry profiles that can be used for drag analysis and visualization.

The aerodynamic workflow generally consists of:

1. Defining vehicle geometry
2. Generating nose cone coordinates
3. Applying atmospheric conditions
4. Evaluating drag factors
5. Comparing geometry families
6. Optimizing the parabolic geometry parameter
7. Displaying the resulting engineering data

The geometry calculations are handled by:

```text
NoseConeGenerator
```

The aerodynamic drag calculations are handled by:

```text
DragSolver
```

---

# 3️⃣ Thermal & Hypersonics Analysis

AeroOpt-X includes an aerothermal analysis module for exploring high-speed flight conditions.

The thermal analysis considers factors such as:

- Mach number
- Ambient temperature
- Altitude
- Compressibility effects
- Stagnation temperature rise
- Shockwave angle estimation

The current aerothermal engine is implemented through:

```text
AeroThermalEngine
```

The thermal module provides engineering estimates that help visualize how increasing flight speed affects thermal loading.

The hypersonic analysis section is intended to provide users with an interactive understanding of:

- High-speed aerodynamic heating
- Temperature rise near stagnation regions
- Shockwave formation
- Flow effects associated with increasing Mach number

---

# 4️⃣ Stagnation Temperature and Shockwave Calculations

AeroOpt-X estimates stagnation temperature using an idealized compressible-flow relationship:

```text
T₀ = T∞ × (1 + ((γ - 1) / 2) × M²)
```

Where:

- `T₀` = stagnation temperature
- `T∞` = ambient temperature
- `γ` = ratio of specific heats
- `M` = Mach number

For air, the current model uses:

```text
γ = 1.4
```

The application also estimates an oblique shockwave angle for applicable supersonic conditions.

The current implementation is intended as an engineering approximation for interactive exploration rather than a complete high-fidelity CFD or shock-expansion solver.

---

# 5️⃣ 2DOF Flight Trajectory Simulation

AeroOpt-X includes a dynamic two-degree-of-freedom trajectory simulation.

The trajectory module evaluates flight behavior based on parameters such as:

- Thrust
- Burn time
- Wind speed
- Dry mass
- Wet mass
- Drag coefficient
- Pitch kick time
- Simulation time step

The trajectory simulation is handled by:

```text
DynamicTrajectory2DOF
```

The simulation generates engineering data including:

- Time
- Downrange distance
- Altitude
- Velocity
- Apogee
- Time to apogee
- Maximum velocity
- Total simulated flight time

The primary trajectory visualization displays the relationship between:

```text
Altitude ↔ Downrange Distance
```

This allows users to explore the resulting flight path interactively.

---

# 6️⃣ Parametric Sweeps and Engineering Exploration

AeroOpt-X includes a parametric sweep system for exploring the effect of multiple engineering variables.

The current sweep system evaluates:

- Mach number
- Fineness ratio
- Drag factor

Users can configure ranges such as:

```text
Mach Minimum
Mach Maximum

Fineness Ratio Minimum
Fineness Ratio Maximum

Grid Size
```

The backend generates a numerical grid representing combinations of the selected parameters.

This allows users to visually explore engineering trends rather than analyzing only one configuration at a time.

The parametric sweep engine is currently implemented through:

```text
AeroThermalEngine.generate_parametric_sweep()
```

---

# 7️⃣ Optimization Using SciPy SLSQP

AeroOpt-X uses numerical optimization to search for improved parabolic nose cone geometry parameters.

The optimization engine uses:

```text
SciPy SLSQP
```

SLSQP stands for:

```text
Sequential Least Squares Programming
```

The optimization process evaluates a parabolic geometry parameter and attempts to minimize the associated drag proxy.

The optimization workflow is:

```text
Initial Geometry
      │
      ▼
Generate Parabolic Profile
      │
      ▼
Evaluate Drag
      │
      ▼
SciPy SLSQP Optimization
      │
      ▼
Optimal Parameter K
      │
      ▼
Generate Optimized Geometry
      │
      ▼
Compare Engineering Results
```

The optimization engine is implemented through:

```text
AeroOptimizer
```

The optimization API provides values such as:

- Optimal `K`
- Optimized drag
- Reference drag
- Percentage change relative to the reference

---

# 8️⃣ Interactive Charts & Visualizations

AeroOpt-X uses Plotly for interactive engineering visualizations.

The interface includes visualizations such as:

- Nose cone profile comparison
- Interactive 3D geometry
- Thermal and shock analysis visualization
- Altitude versus downrange trajectory
- Parametric sweep heatmap

Interactive chart capabilities include:

- Zooming
- Panning
- Hover information
- Resetting views
- Interactive camera controls for 3D charts

These visualizations allow users to inspect engineering data dynamically instead of relying only on static graphs.

The frontend chart system is primarily handled through:

```text
app/static/js/charts.js
```

---

# 9️⃣ Vehicle Presets

Vehicle presets provide a convenient way to load representative parameter configurations.

The current backend preset system includes examples such as:

- Custom
- Sounding Rocket (Terrier-Orion)
- Model Rocket (Estes Alpha)
- Hypersonic Penetrator
- FPV Racing Drone Arm

Each preset provides baseline values such as:

- Length
- Radius
- Mach number
- Measurement unit

Users can modify preset values after loading them.

The preset definitions are currently maintained within:

```text
AeroThermalEngine.PRESETS
```

---

# 🔟 Documentation Page

AeroOpt-X includes a dedicated Documentation page.

The documentation is intended to explain:

- Dashboard modules
- Input parameters
- Aerodynamic profiles
- Thermal calculations
- Shockwave analysis
- Trajectory simulation
- Optimization
- Parametric sweeps
- API concepts
- Engineering assumptions

The documentation page provides an accessible reference for understanding how the AeroOpt-X workflow operates.

Current documentation files include:

```text
app/templates/documentation/documentation.html
app/static/css/documentation.css
app/static/js/documentation.js
```

---

# 1️⃣1️⃣ Help Page

The Help page provides contextual guidance for using the application.

It is intended to assist users with:

- Understanding the dashboard
- Selecting vehicle presets
- Entering parameters
- Running analyses
- Interpreting charts
- Using optimization
- Understanding trajectory outputs
- Exporting available data

The Help system is designed to make the application more approachable for users with different levels of aerospace engineering experience.

Current Help page files include:

```text
app/templates/help/help.html
app/static/css/help.css
app/static/js/help.js
```

---

# 🏗️ Project Architecture

```text
                           ┌─────────────────────────────┐
                           │       User / Browser        │
                           └──────────────┬──────────────┘
                                          │
                                          ▼
                           ┌─────────────────────────────┐
                           │      AeroOpt-X Frontend     │
                           │                             │
                           │ HTML + CSS + JavaScript     │
                           │ Plotly Interactive Charts   │
                           └──────────────┬──────────────┘
                                          │
                              REST API / JSON Requests
                                          │
                                          ▼
                    ┌────────────────────────────────────────┐
                    │            Flask Application           │
                    │              app/main.py               │
                    └───────────────┬────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
     ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
     │ Geometry Engine│    │ Physics Engine │    │ Optimization   │
     │                │    │                │    │ Engine         │
     └────────────────┘    └────────────────┘    └────────────────┘
              │                     │                     │
              ▼                     ▼                     ▼
     NoseConeGenerator       DragSolver          AeroOptimizer
                             AeroThermalEngine
                             DynamicTrajectory2DOF
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────────┐
                    │        JSON Engineering Results        │
                    └────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────────┐
                    │       Plotly / Dashboard Output        │
                    └────────────────────────────────────────┘
```

---

# 📁 Project Structure

```text
aeroopt-x/
│
├── app/
│   ├── main.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   ├── documentation.css
│   │   │   └── help.css
│   │   │
│   │   └── js/
│   │       ├── api.js
│   │       ├── app.js
│   │       ├── charts.js
│   │       ├── documentation.js
│   │       └── help.js
│   │
│   └── templates/
│       ├── index.html
│       │
│       ├── documentation/
│       │   └── documentation.html
│       │
│       └── help/
│           └── help.html
│
├── src/
│   └── aeroopt/
│       ├── geometry/
│       │   └── nose_cone.py
│       │
│       ├── physics/
│       │   ├── drag_solver.py
│       │   ├── aerothermal.py
│       │   └── trajectory.py
│       │
│       └── optimizer/
│           └── objective.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# ⚡ Installation Instructions

## 1. Clone the Repository

```bash
git clone https://github.com/PRASHANTROOT/aeroopt-x.git
```

```bash
cd aeroopt-x
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate the environment:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running AeroOpt-X Locally

Start the Flask application:

```bash
python app/main.py
```

The development server should start at:

```text
http://127.0.0.1:5000
```

Open this address in your browser.

The application includes routes for:

```text
/
```

Main dashboard.

```text
/documentation
```

Documentation page.

```text
/help
```

Help page.

---

# 🐳 Docker Instructions

AeroOpt-X includes Docker support.

## Build and Start Using Docker Compose

```bash
docker-compose up --build
```

To run in detached mode:

```bash
docker-compose up --build -d
```

Stop the containers:

```bash
docker-compose down
```

After the container starts, open the configured application address in your browser.

---

# 🔌 API Endpoints

AeroOpt-X exposes a Flask-based JSON API.

---

## Health Check

### `GET /api/health`

Returns the status of the backend.

Example response:

```json
{
  "status": "healthy",
  "service": "AeroOpt-X",
  "engine": "Python Aerodynamics Core"
}
```

---

## Main Aerodynamic Analysis

### `POST /api/analyze`

Performs:

- Geometry generation
- Drag analysis
- SLSQP optimization
- Aerothermal analysis
- Atmospheric property evaluation

Example request:

```json
{
  "length": 0.5,
  "radius": 0.05,
  "mach": 1.5,
  "altitude": 0
}
```

The response includes data related to:

- Input parameters
- Atmospheric conditions
- Drag comparisons
- Optimization
- Thermal analysis
- Shock angle
- Geometry coordinates

---

## Geometry Optimization

### `POST /api/optimize`

Runs the standalone SciPy SLSQP optimization process.

Example request:

```json
{
  "length": 0.5,
  "radius": 0.05,
  "mach": 1.5,
  "altitude": 0
}
```

---

## Flight Trajectory Simulation

### `POST /api/trajectory`

Runs the 2DOF trajectory simulation.

Example request:

```json
{
  "thrust": 150,
  "burn_time": 2.5,
  "wind_speed": 5,
  "dry_mass": 1.5,
  "wet_mass": 2.5,
  "drag_cd": 0.15,
  "pitch_kick_time": 0.5,
  "dt": 0.01
}
```

---

## Parametric Sweep

### `POST /api/sweep`

Generates a Mach number and fineness-ratio sweep.

Example request:

```json
{
  "mach_min": 0.5,
  "mach_max": 6.0,
  "fineness_min": 2.0,
  "fineness_max": 10.0,
  "grid_size": 30
}
```

---

# 🧰 Technology Stack

## Backend

- Python
- Flask
- NumPy
- SciPy

## Engineering Modules

- Parametric nose cone generation
- Aerodynamic drag calculations
- Aerothermal calculations
- Atmospheric modeling
- Numerical optimization
- Dynamic trajectory simulation

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Plotly.js

## Deployment

- Docker
- Docker Compose

---

# 🖼️ Screenshots

Screenshots can be added to this section as the AeroOpt-X interface continues to evolve.

## Main Dashboard

```text
screenshots/dashboard.png
```

> Add an image showing the main AeroOpt-X workspace, vehicle presets, engineering controls, and navigation.

---

## Nose Cone & Aerodynamic Analysis

```text
screenshots/aerodynamic-analysis.png
```

> Add an image showing aerodynamic drag metrics and profile comparison.

---

## Interactive 3D Geometry

```text
screenshots/geometry-3d.png
```

> Add an image showing the interactive 3D nose cone visualization.

---

## Thermal & Hypersonics

```text
screenshots/thermal-analysis.png
```

> Add an image showing the thermal and shockwave analysis workspace.

---

## Flight Trajectory

```text
screenshots/trajectory.png
```

> Add an image showing the altitude versus downrange trajectory visualization.

---

## Parametric Sweep

```text
screenshots/sweep.png
```

> Add an image showing the Mach/fineness-ratio parametric heatmap.

---

# ⚠️ Current Limitations & Disclaimer

AeroOpt-X is currently intended for:

- Educational use
- Engineering experimentation
- Conceptual design exploration
- Software and numerical modeling development

It should **not currently be treated as a replacement for**:

- Validated production CFD software
- Wind tunnel testing
- Flight certification analysis
- Structural certification
- Thermal protection certification
- Professional flight safety analysis

Several calculations use simplified engineering models and approximations.

For example:

- Drag values are model-based proxies and are not full Navier-Stokes CFD solutions.
- Atmospheric modeling is simplified.
- Stagnation temperature calculations assume an idealized compressible-flow relationship.
- Shock-angle calculations use simplified approximations.
- The trajectory model is a simplified 2DOF simulation.
- Parametric sweep results are intended for comparative engineering exploration.

Real aerospace design decisions should be validated using appropriate high-fidelity simulation tools, experimental testing, and qualified engineering review.

---

# 🛣️ Future Roadmap

Future AeroOpt-X development may include the following areas.

## Aerodynamics

- Higher-fidelity CFD integration
- Pressure coefficient visualization
- Flow velocity field visualization
- Streamline visualization
- Boundary-layer estimation
- Transonic drag modeling
- More advanced wave-drag methods

## Thermal & Hypersonics

- Interactive 3D thermal visualization
- Surface temperature mapping
- Temperature gradients across geometry
- Heat-flux estimation
- Improved oblique shock solver
- Detached bow shock modeling
- Altitude-dependent atmospheric layers

## Geometry

- Additional nose cone families
- Custom parametric geometry editor
- Fins and body sections
- Complete rocket vehicle geometry
- Improved STL and CAD export

## Flight Dynamics

- Higher-fidelity 3DOF simulation
- 6DOF flight dynamics
- Variable thrust curves
- Wind profiles
- Launch rail simulation
- Atmospheric density variation during flight

## Optimization

- Multi-objective optimization
- Genetic algorithms
- Bayesian optimization
- Drag versus structural tradeoff optimization
- Thermal and aerodynamic co-optimization

## User Experience

- Project save/load functionality
- Simulation history
- User-defined presets
- Comparison workspace
- Automated engineering report generation
- PDF report export
- More interactive 3D analysis tools

---

# 🤝 Contributing

Contributions are welcome.

Possible contribution areas include:

- Aerospace engineering models
- Numerical optimization
- CFD integration
- Flight dynamics
- Visualization
- Frontend improvements
- Documentation
- Testing

A typical contribution workflow is:

```bash
git checkout -b feature/your-feature-name
```

Make changes and test the application.

Stage the changes:

```bash
git add .
```

Create a commit:

```bash
git commit -m "Add your feature"
```

Push the branch:

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request.

---

# 📜 License

# © Copyright

Copyright © 2026 Prashant. All rights reserved.

AeroOpt-X, including its source code, software architecture, engineering models, documentation, visual interface, graphics, and other project materials, is the intellectual property of the project owner.

No part of this repository may be copied, reproduced, modified, distributed, sublicensed, sold, or used for commercial purposes without prior written permission from the copyright owner.

The source code is made publicly visible for reference and demonstration purposes only. Public availability of this repository does not grant permission to reuse, redistribute, or create derivative works from the project.

For licensing, collaboration, or permission requests, please contact the repository owner.

---

# 🚀 AeroOpt-X

**From aerodynamic geometry to engineering insight — AeroOpt-X brings aerodynamic analysis, optimization, thermal estimation, shockwave analysis, and flight simulation into one interactive aerospace engineering workspace.**
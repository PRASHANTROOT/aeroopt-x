import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from aeroopt.geometry.nose_cone import NoseConeGenerator
from aeroopt.geometry.drone_arm import DroneArmGenerator
from aeroopt.geometry.stl_exporter import STLExporter
from aeroopt.geometry.flow_visualizer import FlowVisualizer
from aeroopt.physics.drag_solver import DragSolver
from aeroopt.physics.trajectory import TrajectorySimulator
from aeroopt.optimizer.objective import AeroOptimizer

st.set_page_config(page_title="AeroOpt-X Engine", page_icon="🚀", layout="wide")

st.title("🚀 AeroOpt-X: Aerodynamic Shape & Trajectory Suite")
st.markdown("Automated 3D aerodynamic optimization, CFD airflow analysis, and launch trajectory simulation.")

tab1, tab2, tab3 = st.tabs(["🚀 Rocket Nose Cone & 3D CFD", "🛸 Drone Arm Aerodynamics", "📈 Launch Trajectory & Apogee"])

with tab1:
    st.header("Rocket Nose Cone Drag Optimization")
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        st.subheader("⚙️ Input Parameters & Units")
        
        # 1. Unit Selection Dropdown
        unit_choice = st.selectbox("Select Measurement Unit", ["Meters (m)", "Centimeters (cm)", "Inches (in)", "Feet (ft)"], index=0)
        
        # Unit conversion multipliers to Standard SI Meters
        unit_scale = {"Meters (m)": 1.0, "Centimeters (cm)": 0.01, "Inches (in)": 0.0254, "Feet (ft)": 0.3048}[unit_choice]
        unit_label = unit_choice.split(" ")[1].replace("(", "").replace(")", "")

        # 2. Custom Input Mode Toggle (Sliders vs. Manual Input)
        input_type = st.radio("Input Mode", ["Sliders", "Custom Exact Value"], horizontal=True)
        
        if input_type == "Sliders":
            raw_length = st.slider(f"Length ({unit_label})", 0.1, 10.0, 0.5, 0.05, key="r_len_s")
            raw_radius = st.slider(f"Base Radius ({unit_label})", 0.01, 1.0, 0.05, 0.01, key="r_rad_s")
        else:
            raw_length = st.number_input(f"Custom Length ({unit_label})", min_value=0.01, max_value=100.0, value=0.5, step=0.01, key="r_len_n")
            raw_radius = st.number_input(f"Custom Base Radius ({unit_label})", min_value=0.001, max_value=10.0, value=0.05, step=0.005, key="r_rad_n")

        mach = st.slider("Mach Speed", 0.1, 5.0, 1.5, 0.1, key="r_mach")
        altitude = st.number_input("Target Altitude (m)", min_value=0, max_value=30000, value=0, step=500, key="r_alt")

        # Convert user input to standard meters for internal physics solver
        length_m = raw_length * unit_scale
        radius_m = raw_radius * unit_scale

        if st.button("⚡ Run SciPy Optimization Loop"):
            optimizer = AeroOptimizer(length=length_m, target_radius=radius_m)
            best_k = optimizer.optimize_parabolic_parameter()
            st.success(f"Optimized Parabolic Curve Factor K: {best_k:.4f}")

    # Compute Profiles in meters
    gen = NoseConeGenerator(length=length_m, base_radius=radius_m)
    x_sh, y_sh = gen.sears_haack()
    x_vk, y_vk = gen.von_karman()
    x_og, y_og = gen.ogive()

    # Solve Drag Factor
    solver = DragSolver(mach_number=mach, altitude_m=altitude)
    drag_sh = solver.compute_wave_drag_factor(x_sh, y_sh)
    drag_vk = solver.compute_wave_drag_factor(x_vk, y_vk)
    drag_og = solver.compute_wave_drag_factor(x_og, y_og)

    with col_viz:
        m1, m2, m3 = st.columns(3)
        m1.metric("Sears-Haack Drag Factor", f"{drag_sh:.5f}", "Optimal Wave Drag")
        m2.metric("Von Kármán Drag Factor", f"{drag_vk:.5f}")
        m3.metric("Tangent Ogive Drag Factor", f"{drag_og:.5f}")

        # 3. Automated Engineering Conclusion Box
        st.subheader("📋 Engineering Analysis & Conclusion")
        fineness_ratio = length_m / (2 * radius_m) if radius_m > 0 else 0
        drag_diff_pct = ((drag_og - drag_sh) / drag_og * 100) if drag_og > 0 else 0

        st.info(f"""
        **Nose Cone Performance Analysis:**
        * **Fineness Ratio (/D$):** {fineness_ratio:.2f} (Optimal supersonic efficiency range is typically 3.0 to 6.0).
        * **Percentage Drag Reduction:** The **Sears-Haack** body reduces wave drag by **{drag_diff_pct:.1f}%** compared to the baseline Tangent Ogive at Mach **{mach:.1f}**.
        * **Flight Regime Analysis:** Operating in **{"Supersonic ( > 1.0$)" if mach > 1.0 else "Subsonic/Transonic ( \le 1.0$)"}** regime. {"Sears-Haack profile minimizes wave pressure shockwaves at high velocity." if mach > 1.0 else "Wave drag is minimal at subsonic speeds; surface skin friction dominates flight performance."}
        """)

        # 3D Viewport
        st.subheader("Interactive 3D Solid Surface Viewport")
        flow_viz = FlowVisualizer(x_sh, y_sh, mach=mach)
        fig_3d = flow_viz.create_3d_mesh_figure()
        st.plotly_chart(fig_3d, use_container_width=True)

        # 2D Flow Streamlines
        st.subheader("Velocity Field & Airflow Streamlines")
        gx, gy, u, v, v_mag = flow_viz.generate_flow_field()
        fig_flow = go.Figure(data=go.Contour(z=v_mag, x=gx[0], y=gy[:, 0], colorscale='Jet', contours_coloring='heatmap'))
        fig_flow.add_trace(go.Scatter(x=x_sh / unit_scale, y=y_sh / unit_scale, mode='lines', line=dict(color='white', width=3), name='Nose Cone'))
        fig_flow.add_trace(go.Scatter(x=x_sh / unit_scale, y=-y_sh / unit_scale, mode='lines', line=dict(color='white', width=3), showlegend=False))
        fig_flow.update_layout(template="plotly_dark", height=350, xaxis_title=f"X ({unit_label})", yaxis_title=f"Y ({unit_label})")
        st.plotly_chart(fig_flow, use_container_width=True)

        # 3D STL CAD Model Download
        exporter = STLExporter(x_sh, y_sh)
        stl_bytes = exporter.export_stl_bytes()
        st.download_button(
            label="📦 Download Sears-Haack 3D Model (.STL)",
            data=stl_bytes,
            file_name="sears_haack_nosecone.stl",
            mime="model/stl"
        )

with tab2:
    st.header("Drone Multirotor Arm Downwash Drag Reduction")
    col_d_in, col_d_viz = st.columns([1, 2])
    
    with col_d_in:
        chord = st.slider("Arm Chord Length (m)", 0.02, 0.10, 0.04, 0.005)
        thickness = st.slider("Arm Thickness (m)", 0.005, 0.030, 0.015, 0.001)

    drone_gen = DroneArmGenerator(chord_length=chord, max_thickness=thickness)
    x_td, y_td = drone_gen.teardrop_profile()
    x_sq, y_sq = drone_gen.square_profile()

    with col_d_viz:
        st.markdown("**Downwash Profile Comparison:** Teardrop vs Baseline Square Tube")
        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(x=x_td, y=y_td, mode='lines', name='Optimized Teardrop', line=dict(color='#00E676', width=3)))
        fig_d.add_trace(go.Scatter(x=x_td, y=-y_td, mode='lines', showlegend=False, line=dict(color='#00E676', width=3)))
        fig_d.add_trace(go.Scatter(x=x_sq, y=y_sq, mode='lines', name='Baseline Square Tube', line=dict(color='#FF5252', dash='dash')))
        fig_d.update_layout(xaxis_title="Chord (m)", yaxis_title="Height (m)", template="plotly_dark", height=400)
        st.plotly_chart(fig_d, use_container_width=True)

with tab3:
    st.header("Rocket Launch Trajectory & Apogee Simulator")
    col_t_in, col_t_viz = st.columns([1, 2])
    
    with col_t_in:
        thrust = st.slider("Motor Thrust (N)", 50.0, 300.0, 120.0, 10.0)
        burn_time = st.slider("Burn Duration (s)", 1.0, 5.0, 2.0, 0.5)
        dry_mass = st.slider("Dry Mass (kg)", 0.5, 5.0, 1.5, 0.1)

    sim_opt = TrajectorySimulator(dry_mass=dry_mass, thrust=thrust, burn_time=burn_time, drag_cd=drag_sh * 10)
    sim_base = TrajectorySimulator(dry_mass=dry_mass, thrust=thrust, burn_time=burn_time, drag_cd=drag_og * 10)

    t_opt, y_opt, v_opt = sim_opt.run_simulation()
    t_base, y_base, v_base = sim_base.run_simulation()

    with col_t_viz:
        st.metric("Peak Altitude Gain", f"{max(y_opt):.1f} m", f"+{max(y_opt) - max(y_base):.1f} m vs Baseline Ogive")
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=t_opt, y=y_opt, mode='lines', name='Optimized Sears-Haack Flight', line=dict(color='#00E676', width=3)))
        fig_traj.add_trace(go.Scatter(x=t_base, y=y_base, mode='lines', name='Standard Ogive Flight', line=dict(color='#FF5252', dash='dash')))
        fig_traj.update_layout(xaxis_title="Time (s)", yaxis_title="Altitude (m)", template="plotly_dark", height=400)
        st.plotly_chart(fig_traj, use_container_width=True)

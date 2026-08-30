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
from aeroopt.physics.drag_solver import DragSolver
from aeroopt.optimizer.objective import AeroOptimizer

st.set_page_config(page_title="AeroOpt-X Engine", page_icon="🚀", layout="wide")

st.title("🚀 AeroOpt-X: Aerodynamic Shape & Trajectory Engine")
st.markdown("Automated 3D aerodynamic profile optimization for rockets and multirotor drone arms.")

# Create tabs for Rocket vs Drone Arm optimization
tab1, tab2 = st.tabs(["🚀 Rocket Nose Cone & CFD", "🛸 Drone Arm Aerodynamics"])

with tab1:
    st.header("Rocket Nose Cone Drag Optimization")
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        length = st.slider("Length (m)", 0.1, 2.0, 0.5, 0.05, key="r_len")
        radius = st.slider("Base Radius (m)", 0.01, 0.3, 0.05, 0.01, key="r_rad")
        mach = st.slider("Mach Speed", 0.5, 3.0, 1.5, 0.1, key="r_mach")
        
        # Run SciPy Optimization
        if st.button("⚡ Run SciPy Optimization Loop"):
            optimizer = AeroOptimizer(length=length, target_radius=radius)
            best_k = optimizer.optimize_parabolic_parameter()
            st.success(f"Optimized Parabolic Curve Factor K: {best_k:.4f}")

    gen = NoseConeGenerator(length=length, base_radius=radius)
    x_sh, y_sh = gen.sears_haack()
    x_vk, y_vk = gen.von_karman()
    x_og, y_og = gen.ogive()

    solver = DragSolver(mach_number=mach)
    drag_sh = solver.compute_wave_drag_factor(x_sh, y_sh)
    drag_vk = solver.compute_wave_drag_factor(x_vk, y_vk)
    drag_og = solver.compute_wave_drag_factor(x_og, y_og)

    with col_viz:
        m1, m2, m3 = st.columns(3)
        m1.metric("Sears-Haack Drag Factor", f"{drag_sh:.5f}", "Optimal Wave Drag")
        m2.metric("Von Kármán Drag Factor", f"{drag_vk:.5f}")
        m3.metric("Tangent Ogive Drag Factor", f"{drag_og:.5f}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_sh, y=y_sh, mode='lines', name='Sears-Haack', line=dict(color='#E60012', width=3)))
        fig.add_trace(go.Scatter(x=x_vk, y=y_vk, mode='lines', name='Von Kármán', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=x_og, y=y_og, mode='lines', name='Tangent Ogive', line=dict(dash='dot')))
        fig.update_layout(xaxis_title="Length (m)", yaxis_title="Radius (m)", template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # 3D STL Download
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

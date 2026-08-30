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
from aeroopt.physics.trajectory import DynamicTrajectory2DOF
from aeroopt.physics.aerothermal import AeroThermalEngine
from aeroopt.optimizer.objective import AeroOptimizer

st.set_page_config(page_title="AeroOpt-X Suite", page_icon="🚀", layout="wide")

st.title("🚀 AeroOpt-X: Aerodynamic Shape, Thermal & Trajectory Suite")
st.markdown("Automated 3D aerodynamic shape optimization, hypersonic thermal shocks, 2DOF trajectory modeling, and parametric sweeps.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Rocket Nose Cone & CFD", 
    "🌡️ Thermal Shock & Hypersonics", 
    "📈 2DOF Flight Trajectory", 
    "🌐 Parametric Sweeps & Reports"
])

# Sidebar Presets
st.sidebar.header("🛩️ Multi-Geometry Vehicle Presets")
preset_choice = st.sidebar.selectbox("Load Real-World Vehicle Profile", list(AeroThermalEngine.PRESETS.keys()))
preset_data = AeroThermalEngine.PRESETS[preset_choice]

with tab1:
    st.header("Rocket Nose Cone Drag Optimization")
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        st.subheader("⚙️ Input Parameters & Units")
        unit_choice = st.selectbox("Select Measurement Unit", ["Meters (m)", "Centimeters (cm)", "Inches (in)", "Feet (ft)"], index=0)
        unit_scale = {"Meters (m)": 1.0, "Centimeters (cm)": 0.01, "Inches (in)": 0.0254, "Feet (ft)": 0.3048}[unit_choice]
        unit_label = unit_choice.split(" ")[1].replace("(", "").replace(")", "")

        input_type = st.radio("Input Mode", ["Sliders", "Custom Exact Value"], horizontal=True)
        
        default_len = preset_data["length"] / unit_scale
        default_rad = preset_data["radius"] / unit_scale
        default_mach = preset_data["mach"]

        if input_type == "Sliders":
            raw_length = st.slider(f"Length ({unit_label})", 0.01, 50.0, float(default_len), key="r_len_s")
            raw_radius = st.slider(f"Base Radius ({unit_label})", 0.001, 5.0, float(default_rad), key="r_rad_s")
        else:
            raw_length = st.number_input(f"Custom Length ({unit_label})", min_value=0.001, value=float(default_len), step=0.01, key="r_len_n")
            raw_radius = st.number_input(f"Custom Base Radius ({unit_label})", min_value=0.0001, value=float(default_rad), step=0.005, key="r_rad_n")

        mach = st.slider("Mach Speed", 0.1, 8.0, float(default_mach), 0.1, key="r_mach")
        altitude = st.number_input("Target Altitude (m)", min_value=0, max_value=50000, value=0, step=500, key="r_alt")

        length_m = raw_length * unit_scale
        radius_m = raw_radius * unit_scale

        if st.button("⚡ Run SciPy Optimization Loop"):
            optimizer = AeroOptimizer(length=length_m, target_radius=radius_m)
            best_k = optimizer.optimize_parabolic_parameter()
            st.success(f"Optimized Parabolic Curve Factor K: {best_k:.4f}")

    gen = NoseConeGenerator(length=length_m, base_radius=radius_m)
    x_sh, y_sh = gen.sears_haack()
    x_vk, y_vk = gen.von_karman()
    x_og, y_og = gen.ogive()

    solver = DragSolver(mach_number=mach, altitude_m=altitude)
    drag_sh = solver.compute_wave_drag_factor(x_sh, y_sh)
    drag_vk = solver.compute_wave_drag_factor(x_vk, y_vk)
    drag_og = solver.compute_wave_drag_factor(x_og, y_og)

    with col_viz:
        m1, m2, m3 = st.columns(3)
        m1.metric("Sears-Haack Drag Factor", f"{drag_sh:.5f}", "Optimal Wave Drag")
        m2.metric("Von Kármán Drag Factor", f"{drag_vk:.5f}")
        m3.metric("Tangent Ogive Drag Factor", f"{drag_og:.5f}")

        st.subheader("📋 Engineering Analysis & Conclusion")
        fineness_ratio = length_m / (2 * radius_m) if radius_m > 0 else 0
        drag_diff_pct = ((drag_og - drag_sh) / drag_og * 100) if drag_og > 0 else 0

        st.info(f"""
        **Nose Cone Performance Summary:**
        * **Fineness Ratio (/D$):** {fineness_ratio:.2f} (Optimal supersonic efficiency: 3.0 - 6.0).
        * **Percentage Drag Reduction:** **Sears-Haack** reduces wave drag by **{drag_diff_pct:.1f}%** vs Ogive profile at Mach {mach:.1f}.
        * **Active Vehicle Preset:** {preset_choice}
        """)

        # 3D Solid Surface Viewport
        flow_viz = FlowVisualizer(x_sh, y_sh, mach=mach)
        fig_3d = flow_viz.create_3d_mesh_figure()
        st.plotly_chart(fig_3d, use_container_width=True)

        # 3D STL Download
        exporter = STLExporter(x_sh, y_sh)
        st.download_button("📦 Download 3D STL CAD File", exporter.export_stl_bytes(), "sears_haack_nosecone.stl", "model/stl")

with tab2:
    st.header("🌡️ Hypersonic Thermal & Oblique Shockwave Visualizer")
    col_th1, col_th2 = st.columns([1, 2])
    
    thermal_engine = AeroThermalEngine(mach=mach, altitude_m=altitude)
    stagnation_temp_k = thermal_engine.compute_stagnation_temperature()
    stagnation_temp_c = stagnation_temp_k - 273.15
    half_angle = np.arctan(radius_m / length_m) if length_m > 0 else 0
    shock_angle = thermal_engine.compute_oblique_shock_angle(half_angle)

    with col_th1:
        st.metric("Tip Stagnation Temperature", f"{stagnation_temp_c:.1f} °C", f"{stagnation_temp_k:.1f} K")
        st.metric("Oblique Shock Angle (β)", f"{shock_angle:.1f}°" if mach > 1.0 else "N/A (Subsonic)", "Attached Shockwave Angle")
        st.warning(f"Thermal Boundary Regime: {'🔥 High Aerodynamic Heating' if mach >= 3.0 else '❄️ Nominal Heating'}")

    with col_th2:
        st.subheader("Flow Velocity Contours & Shock Wave Boundary")
        gx, gy, u, v, v_mag = flow_viz.generate_flow_field()
        fig_flow = go.Figure(data=go.Contour(z=v_mag, x=gx[0], y=gy[:, 0], colorscale='Jet'))
        fig_flow.add_trace(go.Scatter(x=x_sh / unit_scale, y=y_sh / unit_scale, mode='lines', line=dict(color='white', width=3)))
        fig_flow.add_trace(go.Scatter(x=x_sh / unit_scale, y=-y_sh / unit_scale, mode='lines', line=dict(color='white', width=3), showlegend=False))
        fig_flow.update_layout(template="plotly_dark", height=400, xaxis_title=f"X ({unit_label})", yaxis_title=f"Y ({unit_label})")
        st.plotly_chart(fig_flow, use_container_width=True)

with tab3:
    st.header("📈 2DOF Flight Trajectory & Gravity Turn Simulator")
    col_tr1, col_tr2 = st.columns([1, 2])
    
    with col_tr1:
        thrust = st.slider("Motor Thrust (N)", 50.0, 500.0, 150.0, 10.0)
        burn_time = st.slider("Burn Duration (s)", 1.0, 10.0, 2.5, 0.5)
        wind_speed = st.slider("Crosswind Speed (m/s)", 0.0, 25.0, 5.0, 1.0)

    sim_2d = DynamicTrajectory2DOF(dry_mass=1.5, thrust=thrust, burn_time=burn_time, drag_cd=drag_sh * 10, wind_speed=wind_speed)
    t_2d, x_2d, y_2d, v_2d = sim_2d.run_2d_simulation()

    with col_tr2:
        st.metric("Apogee (Max Altitude)", f"{max(y_2d):.1f} m", f"Downrange Distance: {x_2d[-1]:.1f} m")
        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=x_2d, y=y_2d, mode='lines', name='2DOF Trajectory (Gravity Turn)', line=dict(color='#00E676', width=3)))
        fig_traj.update_layout(xaxis_title="Downrange X (m)", yaxis_title="Altitude Y (m)", template="plotly_dark", height=400)
        st.plotly_chart(fig_traj, use_container_width=True)

with tab4:
    st.header("🌐 Parametric Sweeps & Technical Report Export")
    
    # 2D Parametric Heatmap Plot
    st.subheader("Wave Drag Factor Sensitivity (Mach Speed vs Fineness Ratio)")
    m_arr, f_arr, drag_grid = AeroThermalEngine.generate_parametric_sweep()
    fig_heat = go.Figure(data=go.Heatmap(z=drag_grid, x=m_arr, y=f_arr, colorscale='Viridis'))
    fig_heat.update_layout(xaxis_title="Mach Speed (M)", yaxis_title="Fineness Ratio (L/D)", template="plotly_dark", height=400)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Printable HTML Report Summary
    st.subheader("📊 Executive Technical Summary Report")
    report_html = f"""
    <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333;">
        <h2>AeroOpt-X Analysis Report</h2>
        <p><b>Vehicle Profile:</b> {preset_choice}</p>
        <p><b>Length:</b> {raw_length:.3f} {unit_label} | <b>Base Radius:</b> {raw_radius:.3f} {unit_label}</p>
        <p><b>Target Mach:</b> {mach:.2f} | <b>Fineness Ratio (L/D):</b> {fineness_ratio:.2f}</p>
        <hr>
        <h4>Aerodynamic Performance Metrics</h4>
        <ul>
            <li><b>Sears-Haack Drag Factor:</b> {drag_sh:.5f}</li>
            <li><b>Von Kármán Drag Factor:</b> {drag_vk:.5f}</li>
            <li><b>Tangent Ogive Drag Factor:</b> {drag_og:.5f}</li>
            <li><b>Stagnation Temperature:</b> {stagnation_temp_c:.1f} °C ({stagnation_temp_k:.1f} K)</li>
            <li><b>Apogee Height:</b> {max(y_2d):.1f} m</li>
        </ul>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)

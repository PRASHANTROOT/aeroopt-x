import streamlit as st
import numpy as np
import plotly.graph_objects as go
from aeroopt.geometry.nose_cone import NoseConeGenerator
from aeroopt.physics.drag_solver import DragSolver

st.set_page_config(page_title="AeroOpt-X Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 AeroOpt-X: Aerodynamic Shape & Drag Optimization")
st.markdown("Automated 3D aerodynamic profile and drag evaluation engine for aerospace vehicles.")

# Sidebar controls
st.sidebar.header("Vehicle Parameters")
length = st.sidebar.slider("Length (m)", 0.1, 2.0, 0.5, 0.05)
radius = st.sidebar.slider("Base Radius (m)", 0.01, 0.3, 0.05, 0.01)
mach = st.sidebar.slider("Mach Speed", 0.5, 3.0, 1.5, 0.1)

# Generate Profiles
gen = NoseConeGenerator(length=length, base_radius=radius)
x_sh, y_sh = gen.sears_haack()
x_vk, y_vk = gen.von_karman()
x_og, y_og = gen.ogive()

# Physics Evaluation
solver = DragSolver(mach_number=mach)
drag_sh = solver.compute_wave_drag_factor(x_sh, y_sh)
drag_vk = solver.compute_wave_drag_factor(x_vk, y_vk)
drag_og = solver.compute_wave_drag_factor(x_og, y_og)

# Layout Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Sears-Haack Drag Factor", f"{drag_sh:.5f}", "Optimal Wave Drag")
col2.metric("Von Kármán Drag Factor", f"{drag_vk:.5f}")
col3.metric("Tangent Ogive Drag Factor", f"{drag_og:.5f}")

# Plotly 2D/3D visualization
st.subheader("Profile Geometry Comparison")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x_sh, y=y_sh, mode='lines', name='Sears-Haack', line=dict(color='#E60012', width=3)))
fig.add_trace(go.Scatter(x=x_vk, y=y_vk, mode='lines', name='Von Kármán', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=x_og, y=y_og, mode='lines', name='Tangent Ogive', line=dict(dash='dot')))

fig.update_layout(xaxis_title="Length (m)", yaxis_title="Radius (m)", template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

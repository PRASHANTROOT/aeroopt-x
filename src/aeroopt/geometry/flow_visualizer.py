import numpy as np
import plotly.graph_objects as go

class FlowVisualizer:
    """Generates 2D airflow streamlines and interactive 3D surface meshes."""

    def __init__(self, x_coords: np.ndarray, y_coords: np.ndarray, mach: float = 1.5):
        self.x = x_coords
        self.y = y_coords
        self.mach = mach

    def generate_flow_field(self):
        """Calculates flow field streamlines around the nose cone geometry."""
        grid_x, grid_y = np.meshgrid(
            np.linspace(-0.1, max(self.x) + 0.2, 30),
            np.linspace(-max(self.y) * 2, max(self.y) * 2, 30)
        )
        
        # Free-stream velocity vector components
        u = np.full_like(grid_x, self.mach * 343.0)
        v = np.zeros_like(grid_y)
        
        # Deflect flow near the body surface
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                px, py = grid_x[i, j], grid_y[i, j]
                if 0 <= px <= max(self.x):
                    # Find closest surface profile point
                    idx = np.argmin(np.abs(self.x - px))
                    body_r = self.y[idx]
                    if abs(py) < body_r:
                        u[i, j] = 0.0 # Zero velocity inside body
                    elif abs(py) < body_r * 2.0:
                        deflection = (1.0 - (abs(py) - body_r) / body_r)
                        v[i, j] = np.sign(py) * u[i, j] * 0.3 * deflection
                        u[i, j] *= (1.0 - 0.2 * deflection)

        velocity_magnitude = np.sqrt(u**2 + v**2)
        return grid_x, grid_y, u, v, velocity_magnitude

    def create_3d_mesh_figure(self, num_slices: int = 36) -> go.Figure:
        """Constructs an interactive 3D rotational mesh plot using Plotly."""
        angles = np.linspace(0, 2 * np.pi, num_slices)
        
        # Generate 3D surface grid
        X = np.outer(self.x, np.ones(num_slices))
        Y = np.outer(self.y, np.cos(angles))
        Z = np.outer(self.y, np.sin(angles))

        fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis', showscale=False)])
        fig.update_layout(
            scene=dict(
                xaxis_title='Length (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)',
                aspectmode='data'
            ),
            template="plotly_dark",
            margin=dict(l=0, r=0, b=0, t=0),
            height=450
        )
        return fig

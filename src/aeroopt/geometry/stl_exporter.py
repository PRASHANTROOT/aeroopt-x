import numpy as np
import trimesh

class STLExporter:
    """Revolves a 2D aerodynamic profile around the X-axis to construct a 3D STL mesh."""
    
    def __init__(self, x_coords: np.ndarray, y_coords: np.ndarray, num_slices: int = 36):
        self.x = x_coords
        self.y = y_coords
        self.slices = num_slices

    def generate_mesh(self) -> trimesh.Trimesh:
        """Constructs a 3D surface mesh using rotational sweep."""
        angles = np.linspace(0, 2 * np.pi, self.slices, endpoint=False)
        vertices = []
        
        # Build 3D vertex points along revolution
        for i in range(len(self.x)):
            r = self.y[i]
            x_val = self.x[i]
            for theta in angles:
                y_val = r * np.cos(theta)
                z_val = r * np.sin(theta)
                vertices.append([x_val, y_val, z_val])
                
        vertices = np.array(vertices)
        faces = []
        
        # Build triangular mesh faces
        for i in range(len(self.x) - 1):
            for j in range(self.slices):
                next_j = (j + 1) % self.slices
                
                v1 = i * self.slices + j
                v2 = i * self.slices + next_j
                v3 = (i + 1) * self.slices + next_j
                v4 = (i + 1) * self.slices + j
                
                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])
                
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        return mesh

    def export_stl_bytes(self) -> bytes:
        """Exports the 3D mesh as binary STL bytes for browser download."""
        mesh = self.generate_mesh()
        return mesh.export(file_type='stl')

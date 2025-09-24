import numpy as np
from stl import mesh

class GeometryAgent:
    def __init__(self):
        print("GeometryAgent initialized.")

    def create_block(self, output_path, width, depth, height):
        # Define the 8 corners of the block
        vertices = np.array([
            [0, 0, 0],
            [width, 0, 0],
            [width, depth, 0],
            [0, depth, 0],
            [0, 0, height],
            [width, 0, height],
            [width, depth, height],
            [0, depth, height]])

        # Define the 12 triangles for the 6 faces
        faces = np.array([
            [0, 3, 1], [1, 3, 2],
            [0, 4, 7], [0, 7, 3],
            [4, 5, 6], [4, 6, 7],
            [5, 1, 2], [5, 2, 6],
            [2, 3, 7], [2, 7, 6],
            [0, 1, 5], [0, 5, 4]])

        # Create the mesh
        block = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                block.vectors[i][j] = vertices[f[j],:]
        
        block.save(output_path)
        print(f"Block geometry saved to {output_path}")
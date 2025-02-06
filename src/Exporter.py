import os
import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh.creation as creation
from trimesh.creation import box
from typing import List
from src.SpatialObject import SpatialObject
from PIL import Image
import io

class Exporter:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def exportScene(self, SpatialObjects: List[SpatialObject], filename: str):
        """
        Export the scene to an OBJ file with an accompanying MTL file that includes
        transparency (dissolve) information.
        
        Args:
            SpatialObjects (list): A list of SpatialObject instances.
            filename (str): The base filename for the OBJ file (should end with '.obj').
        """
        # Create a scene and add each spatial object's cube
        scene = trimesh.scene.Scene()
        for obj in SpatialObjects:
            size = (obj.width, obj.height, obj.depth)
            position = obj.position.array
            # Generate a random RGB color
            color = (np.random.randint(0, 255),
                     np.random.randint(0, 255),
                     np.random.randint(0, 255))
            cube = self._createCube(position, size, color)
            scene.add_geometry(cube)
        
        # Merge all geometries into a single mesh for simpler export.
        # (For more complex scenes with separate objects, you would need to handle per-object materials.)
        merged = trimesh.util.concatenate(list(scene.geometry.values()))
        
        # Build full file paths
        obj_filepath = os.path.join(self.root_dir, filename)
        # Ensure the filename ends with .obj
        if not obj_filepath.endswith('.obj'):
            obj_filepath += '.obj'
        mtl_filepath = obj_filepath.replace('.obj', '.mtl')
        
        # Export the merged mesh as an OBJ with an accompanying MTL file.
        self._exportOBJ(merged, obj_filepath, mtl_filepath)
        print(f"Exported OBJ to: {obj_filepath}")
        print(f"Exported MTL to: {mtl_filepath}")

    def _createCube(self, position, size=(1, 1, 1), color=(0, 0, 0)):
        """
        Create a cube mesh at a given position with the specified size,
        and set its face colors and material properties (including transparency).
        
        Parameters:
          - position: (3,) array‐like; the translation of the cube.
          - size: tuple (width, height, depth) (default (1,1,1)).
          - color: tuple of 3 or 4 integers in the range 0–255.
                   If only 3 values are provided, alpha is assumed to be 255.
        
        Returns:
          - cube: a trimesh.Trimesh instance with visual face colors and a material.
        """
        w, h, d = size
        cube = box(extents=(w, h, d))
        cube.apply_translation(position)
        
        # If only RGB is provided, use 128 (about 50% transparency) for alpha
        if len(color) == 3:
            rgba = color + (128,)
        else:
            rgba = color

        # Ensure visuals are defined
        if cube.visual is None or not hasattr(cube.visual, 'face_colors'):
            cube.visual = trimesh.visual.ColorVisuals(cube)

        # Set face colors (one color per face)
        face_count = len(cube.faces)
        cube.visual.face_colors = np.tile(np.array(rgba, dtype=np.uint8), (face_count, 1))
        
        # Set material with diffuse, ambient, and dissolve (transparency) values.
        cube.visual.material = trimesh.visual.material.SimpleMaterial(
            diffuse=[c / 255.0 for c in rgba[:3]],
            ambient=[c / 255.0 for c in rgba[:3]],
            dissolve=rgba[3] / 255.0  # 0: fully transparent, 1: opaque
        )
        return cube

    def _exportOBJ(self, mesh, obj_filepath, mtl_filepath):
        """
        Custom exporter to write an OBJ file and an accompanying MTL file with transparency info.
        
        Parameters:
          - mesh: a trimesh.Trimesh instance (merged geometry).
          - obj_filepath: full path to the OBJ file.
          - mtl_filepath: full path to the MTL file.
        """
        # Get the base name of the MTL file to reference in the OBJ file.
        mtl_basename = os.path.basename(mtl_filepath)
        lines = []
        # OBJ header referencing the MTL file.
        lines.append(f"mtllib {mtl_basename}")
        
        # Write out vertices
        for v in mesh.vertices:
            lines.append("v {:.8f} {:.8f} {:.8f}".format(*v))
        
        # For simplicity, we ignore normals and texture coordinates.
        # Use a single material for the entire mesh.
        material_name = "material0"
        lines.append(f"usemtl {material_name}")
        
        # Write faces (OBJ is 1-indexed)
        for face in mesh.faces:
            indices = face + 1
            lines.append("f {} {} {}".format(*indices))
        
        # Write the OBJ file.
        with open(obj_filepath, 'w') as f:
            f.write("\n".join(lines))
        
        # Build the MTL file.
        # Retrieve material properties from mesh.visual.material if available.
        if hasattr(mesh.visual, 'material') and mesh.visual.material is not None:
            mat = mesh.visual.material
            # Use dissolve if available; default to 1.0 (opaque) otherwise.
            d = getattr(mat, 'dissolve', 1.0)
            diffuse = getattr(mat, 'diffuse', [1.0, 1.0, 1.0])
        else:
            d = 1.0
            diffuse = [1.0, 1.0, 1.0]
        
        mtl_lines = []
        mtl_lines.append(f"newmtl {material_name}")
        mtl_lines.append("Ka {:.4f} {:.4f} {:.4f}".format(*diffuse))  # Ambient color
        mtl_lines.append("Kd {:.4f} {:.4f} {:.4f}".format(*diffuse))  # Diffuse color
        mtl_lines.append("Ks 0.0000 0.0000 0.0000")                    # Specular color (optional)
        mtl_lines.append("d {:.4f}".format(d))                          # Dissolve (transparency)
        mtl_lines.append("illum 2")                                     # Illumination model
        with open(mtl_filepath, 'w') as f:
            f.write("\n".join(mtl_lines))

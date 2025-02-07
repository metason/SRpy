import os
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh.creation as creation
from trimesh.creation import box
from typing import List
from .SpatialObject import SpatialObject
import math
import copy
import subprocess
from pxr.UsdGeom import Xform, Cube
from pxr import Usd, UsdGeom, Gf, Sdf

import random  # For generating uniform random colors

from pxr.UsdGeom import Xform, Cube
from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade

class SceneExporter:
    def __init__(self, root_dir: str):
        """
        :param root_dir: Directory where temporary USD and final USDZ files will be stored.
        """
        self.root_dir = root_dir
        # Define file paths for the final USD file and a temporary one for packaging.
        self.usd_file_path = os.path.join(root_dir, "scene.usd")
        self.temp_usd_path = os.path.join(self.root_dir, "temp_scene.usd")
        self.stage = None

    def add_object(self, spatial_object: SpatialObject) -> None:
        """
        Adds a SpatialObject to the USD scene.
        This method:
        - Creates a transform (Xform) for the object.
        - Creates a cube under that transform and scales it to match the object's dimensions.
        - Creates a material (using UsdPreviewSurface) that assigns a random uniform color and an opacity 
            based on the object's transparency (opacity = 1.0 - transparency).
        - Binds the material to the cube so that renderers interpret the transparency and color.
        
        :param spatial_object: An object with attributes: id, position (with x, y, z),
                            width, height, depth, and transparency.
        """
        # Define a unique prim path for the object.
        prim_path = f"/{spatial_object.id}"
        
        # Create a transform node for the spatial object.
        xform = UsdGeom.Xform.Define(self.stage, prim_path)
        xform.AddTranslateOp().Set(
            Gf.Vec3d(
                spatial_object.position.x,
                spatial_object.position.y,
                spatial_object.position.z
            )
        )
        
        # Create a cube under the transform. The default cube has a size of 1.0.
        cube_path = f"{prim_path}/Cube"
        cube = UsdGeom.Cube.Define(self.stage, cube_path)
        
        # Scale the cube to match the spatial object's dimensions.
        xform.AddScaleOp().Set(
            Gf.Vec3f(
                spatial_object.width,
                spatial_object.height,
                spatial_object.depth
            )
        )
        
        # -----------------------------
        # Create a material for the cube.
        # -----------------------------
        # Create a unique material path.
        material_path = f"{prim_path}/Material"
        material = UsdShade.Material.Define(self.stage, material_path)
        
        # Generate a random uniform color.
        r = random.random()
        g = random.random()
        b = random.random()
        
        # Compute opacity from transparency.
        # (Assuming transparency: 0.0 = opaque, 1.0 = fully transparent)
        opacity = 1.0 - spatial_object.transparency
        
        # Create a shader (using the UsdPreviewSurface).
        shader_path = f"{material_path}/Shader"
        shader = UsdShade.Shader.Define(self.stage, shader_path)
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(r, g, b))
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(opacity)
        
        # **Create the output explicitly so that it isn’t null.**
        shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        shaderSurfaceOutput = shader.GetOutput("surface")
        
        # Connect the material’s surface output to the shader’s surface output.
        material.CreateSurfaceOutput().ConnectToSource(shaderSurfaceOutput)
        
        # Bind the material to the cube's prim.
        UsdShade.MaterialBindingAPI(xform.GetPrim()).Bind(material)
        
        # (Optional) Also store the raw values as custom attributes if needed.
        prim = cube.GetPrim()
        trans_attr = prim.CreateAttribute("user:transparency", Sdf.ValueTypeNames.Float)
        trans_attr.Set(spatial_object.transparency)
        color_attr = prim.CreateAttribute("user:color", Sdf.ValueTypeNames.Color3f)
        color_attr.Set(Gf.Vec3f(r, g, b))


    def exportUSDZ(self, spatial_objects: List[SpatialObject], filename: str) -> None:
        """
        Exports the scene to a USDZ file.
        This method:
          1. Deletes any preexisting USD/temporary files.
          2. Creates a new USD stage.
          3. Adds geometry for each SpatialObject to the stage.
          4. Exports the stage to a temporary USD file.
          5. Uses the external 'usdzip' tool to convert the USD file to a USDZ package.
        
        :param spatial_objects: A list of SpatialObject instances.
        :param filename: The final USDZ file name (including path).
        """
        # Delete existing USD files if they exist.
        if os.path.exists(self.usd_file_path):
            os.remove(self.usd_file_path)
            print(f"Deleted existing file {self.usd_file_path}")
        if os.path.exists(self.temp_usd_path):
            os.remove(self.temp_usd_path)
            print(f"Deleted existing file {self.temp_usd_path}")
            
        # Create a new USD stage.
        self.stage = Usd.Stage.CreateNew(self.usd_file_path)
        
        # Add each spatial object to the stage.
        for obj in spatial_objects:
            self.add_object(obj)

        # Export the USD stage to a temporary USD file.
        self.stage.GetRootLayer().Export(self.temp_usd_path)
        print(f"Exported temporary USD scene to {self.temp_usd_path}")
        filename = self.root_dir + filename
        # Use usdzip to package the USD file into a USDZ file.
        cmd = ["usdzip", filename, self.temp_usd_path]
        try:
            subprocess.run(cmd, check=True)
            print(f"Exported scene to USDZ: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create USDZ file using usdzip: {e}")
        
    def _createCube(self, position, size=(1, 1, 1), color=(0, 0, 0)):
        """
        Create a cube mesh at a given position with the specified size and visual properties.
        (This helper function uses trimesh and is separate from the USD export.)
        """
        w, h, d = size
        cube = box(extents=(w, h, d))
        cube.apply_translation(position)
        
        # If only RGB is provided, use an alpha of 128 (50% transparent)
        if len(color) == 3:
            rgba = color + (128,)
        else:
            rgba = color
        
        # Ensure visuals are defined.
        if cube.visual is None or not hasattr(cube.visual, 'face_colors'):
            cube.visual = trimesh.visual.ColorVisuals(cube)
        
        face_count = len(cube.faces)
        cube.visual.face_colors = np.tile(np.array(rgba, dtype=np.uint8), (face_count, 1))
        cube.visual.material = trimesh.visual.material.SimpleMaterial(
            diffuse=[c / 255.0 for c in rgba[:3]],
            ambient=[c / 255.0 for c in rgba[:3]],
            dissolve=rgba[3] / 255.0  # 0: transparent, 1: opaque
        )
        return cube



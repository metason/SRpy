import os
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh.creation as creation
from trimesh.creation import box
from typing import List
from .SpatialObject import SpatialObject
from .SpatialRelation import SpatialRelation
import math
import copy
import subprocess
from pxr.UsdGeom import Xform, Cube
from pxr import Usd, UsdGeom, Gf, Sdf


import random  # For generating uniform random colors

from pxr.UsdGeom import Xform, Cube
from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade
import datetime

class SceneExporter:
    def __init__(self, root_dir: str):
        """
        :param root_dir: Directory where temporary USD and final USDZ files will be stored.
        """
        self.root_dir = root_dir
        # Define file paths for the final USD file and a temporary one for packaging.
        self.usd_file_path = None
        timestamp = datetime.datetime.now().microsecond
        self.temp_usd_path = os.path.join(self.root_dir, f"temp_scene_{timestamp}.usd")
        print("*"*100)
        print(self.temp_usd_path)
        print("*"*100)
        self.stage = None

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
        self.usd_file_path = os.path.join(self.root_dir, filename)
        if os.path.exists(self.usd_file_path):
            os.remove(self.usd_file_path)
            print(f"Deleted existing file {self.usd_file_path}")
        if os.path.exists(self.temp_usd_path):
            os.remove(self.temp_usd_path)
            print(f"Deleted existing file {self.temp_usd_path}")
            
        # Create a new USD stage.
        self.stage = Usd.Stage.CreateNew(self.temp_usd_path)
        
        # Add each spatial object to the stage.
        for obj in spatial_objects:
            prim_path = self._create_obj_cube(obj)
            self._create_bbox_cube(obj, prim_path)

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
        finally:
            if os.path.exists(self.temp_usd_path):
                os.remove(self.temp_usd_path)
                print(f"Deleted existing file {self.temp_usd_path}")
            
    
    def _createBboxCube(self, obj:SpatialObject, color=(0, 0, 0)):
        name = obj.label if obj.label else obj.id
        
        
    def _create_obj_cube(self, spatial_object: SpatialObject) -> None:
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
        xform.AddRotateYOp().Set(
                math.degrees(spatial_object.angle)
        )
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
        return prim_path
        
    def _create_bbox_cube(self, obj: SpatialObject, parent_path: str, color=(0.0, 0.0, 0.0)) -> None:
        """
        Creates a visual representation of the object's bounding box.
        In this example, we create a small sphere at each bounding box corner.
        It assumes that the SpatialObject has a property 'bounding_box' that is an
        iterable of eight corner points (each a vector with x, y, z attributes).
        
        :param obj: The SpatialObject.
        :param parent_path: The USD prim path of the parent transform.
        :param color: The RGB color tuple to use for the bounding box markers.
        """
        bbox_prim_path = f"{parent_path}/BBox"
        bbox_xform = UsdGeom.Xform.Define(self.stage, bbox_prim_path)
        
        
        sphere_path = f"{bbox_prim_path}/NearbySphere"
        sphere = UsdGeom.Sphere.Define(self.stage, sphere_path)
        
        x = obj.position.x
        y = obj.position.y 
        z = obj.position.z
        # Set a small radius for the sphere.
        radius = obj.nearbyRadius()
        
        sphere.GetPrim().CreateAttribute("radius", Sdf.ValueTypeNames.Float).Set(radius)
        #sphere.AddTranslateOp().Set(Gf.Vec3d(x, y+radius, z))
        # Set the sphere's position to the corner.
        # If corner is not already a Gf.Vec3d, you might need to convert it.
        
        
        # Create a simple material for the bounding sphere.
        bbox_material_path = f"{sphere_path}/Material"
        bbox_material = UsdShade.Material.Define(self.stage, bbox_material_path)
        bbox_shader_path = f"{bbox_material_path}/Shader"
        bbox_shader = UsdShade.Shader.Define(self.stage, bbox_shader_path)
        bbox_shader.CreateIdAttr("UsdPreviewSurface")
        bbox_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        bbox_shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.3)
        bbox_shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        bbox_material.CreateSurfaceOutput().ConnectToSource(bbox_shader.GetOutput("surface"))
        UsdShade.MaterialBindingAPI(sphere.GetPrim()).Bind(bbox_material)
        
        


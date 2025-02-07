import os
import tempfile
import unittest
import numpy as np
import trimesh

# Import your Exporter, SpatialObject, and Vector3 classes.
# Adjust the import paths if necessary.
from src.Exporter import SceneExporter as Exporter
from src.SpatialObject import SpatialObject
from src.Vector3 import Vector3

class TestExporter(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for exported files
        self.temp_dir = "./tests/scenes/"
        # Instantiate the Exporter with the temporary directory as root
        self.exporter = Exporter(self.temp_dir)
        
        # Create a couple of dummy SpatialObject instances.
        # (Assuming SpatialObject accepts at least id, position, width, height, depth, and confidence.)
        self.obj1 = SpatialObject(
            id="test_obj1",
            position=Vector3(0.0, 0.0, 0.0),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=1.0
        )
        self.obj2 = SpatialObject(
            id="test_obj2",
            position=Vector3(2.0, 2.0, 2.0),
            width=1.0,
            height=1.0,
            depth=1.0,
            confidence=1.0
        )
        self.spatial_objects = [self.obj1, self.obj2]

    def test_export_scene_creates_file(self):
        # Specify a filename (without or with .obj extension)
        export_filename = "test_scene.usdz"
        # Call the exportScene method with our dummy spatial objects
        self.exporter.exportUSDZ(self.spatial_objects, export_filename)
        
        # Build the full path to the exported file
        exported_file_path = os.path.join(self.temp_dir, export_filename)
        # Check that the file exists
        self.assertTrue(os.path.exists(exported_file_path), f"Exported file {exported_file_path} does not exist.")
    

if __name__ == '__main__':
    unittest.main()

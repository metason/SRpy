import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import trimesh.creation as creation

from freetype import Face

try:
    from trimesh.geometry import triangulate_polygon as default_triangulate_polygon
except ImportError:
    print("couldnt import trimesh.geometry.triangulate_polygon")

def triangulate_with_triangle(*args, **kwargs):
    kwargs["engine"] = "triangle"
    return default_triangulate_polygon(*args, **kwargs)

def create_text_3d(text, position=(0, 0, 0), depth=0.2, font_size=1):
    face = Face('./src/Arial Unicode.ttf')  # Adjust font path if needed
    face.set_char_size(font_size * 64)  # Set font size

    meshes = []
    names = ["box1", "box2", "box3"]
    angles = [np.pi/2, -np.pi/2, np.pi/4]
    sizes = [0.1, 0.2, 0.3]
    transforms = [[0., 0., 2.], [1.0, 0.0, 0.0], [0.0, 3.0, 0.0]]

    for n, angle, size, t in zip(names, angles, sizes, transforms):
        transform = np.array([[np.cos(angle), 0, -np.sin(angle), t[0]],
                              [0, 1, 0, t[1]],
                              [np.sin(angle), 0, np.cos(angle), t[2]],
                              [0, 0, 0, 1]])
        # Create a box mesh and its outline
        trm1 = trimesh.creation.box([size, size, size], transform, metadata={"name": n})
        trm2 = trimesh.path.creation.box_outline(extents=[size, size, size],
                                                 transform=transform,
                                                 metadata={"name": n})
        meshes.extend([trm1, trm2])
        
        # Variant 1: Simply skip adding the Text entity.
        # txt = trimesh.path.entities.Text(len(trm2.vertices), n, color='black')
        # meshes.append(txt)

        # Variant 2: (If you have a method to convert Text to a mesh.)
        txt = trimesh.path.entities.Text(len(trm2.vertices), n, color='black')
        if hasattr(txt, 'to_mesh'):
            meshes.append(txt.to_mesh())
        else:
            print("Text entity cannot be converted to a mesh, skipping it.")

    # Optionally, you could transform all meshes by the given position:
    for m in meshes:
        m.apply_translation(position)
    
    return meshes

    

def create_cube(position, size=(1, 1, 1)):
    w, h, d = size
    cube = trimesh.creation.box(extents=(w, h, d))
    cube.apply_translation(position)
    return cube

def main():
    # Define objects in 3D space
    objects = [
        {"position": (0, 0, 0), "size": (1, 1, 1)},
        {"position": (2, 0, 0), "size": (1, 2, 1)},
        {"position": (4, 1, 0), "size": (2, 1, 1)},
    ]

    # Create cube meshes
    scene_meshes = [create_cube(obj["position"], obj["size"]) for obj in objects]

    # Create 3D text
    text_meshes = create_text_3d("Hello 3D!", position=(1, 3, 0), depth=0.2, font_size=2)

    # Add text to the scene
    scene_meshes = scene_meshes + text_meshes

    # Merge everything into a single mesh
    scene = trimesh.scene.Scene(scene_meshes)
    #scene = trimesh.util.concatenate(scene_meshes)

    # Export as OBJ
    scene.export("scene_with_text.obj")
    print("Exported 3D scene with text as 'scene_with_text.obj'. You can open it in macOS Preview.")

if __name__ == "__main__":
    main()

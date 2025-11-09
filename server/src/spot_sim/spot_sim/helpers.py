import os
import numpy as np
from pathlib import Path
from collections import deque
from ament_index_python.packages import get_package_share_directory

from Karana.Frame import FrameContainer
from Karana.Dynamics.SOADyn_types import (
    MultibodyDS,
    Linear3SubhingeDS,
    SphericalSubhingeDS,
    HingeDS,
)
from Karana.Dynamics import (
    Multibody,
    HINGE_TYPE,
)
from Karana.Scene import (
    BoxGeometry,
    Color,
    PhysicalMaterialInfo,
    PhysicalMaterial,
    LAYER_GRAPHICS,
    LAYER_ALL,
    Texture,
)
from Karana.Scene import ProxyScenePart, ProxyScene

URDF_TO_POLICY = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
POLICY_TO_URDF = [0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11]

def urdf_to_policy(arr: np.ndarray) -> np.ndarray:
    """Reorder joints from URDF ordering to Policy ordering.
    Works with shape (12,) or (..., 12)."""
    return np.take(arr, URDF_TO_POLICY, axis=-1)

def policy_to_urdf(arr: np.ndarray) -> np.ndarray:
    """Reorder joints from Policy ordering to URDF ordering.
    Works with shape (12,) or (..., 12)."""
    return np.take(arr, POLICY_TO_URDF, axis=-1)

def createMbody(fc: FrameContainer) -> Multibody:
    urdf_path = os.path.join(get_package_share_directory('spot_sim'), "resources", "spot_simple.urdf")
    urdf_file = Path(urdf_path)
    multibody_info = MultibodyDS.fromUrdf(urdf_file)
    # convert to full6DOF hinge between root frame and spot base
    multibody_info.base_bodies[0].body.hinge = HingeDS(
        hinge_type=HINGE_TYPE.FULL6DOF,
        subhinges=[
            Linear3SubhingeDS(prescribed=False),
            SphericalSubhingeDS(prescribed=False),
        ],
    )

    # iterate through all bodies and make them visual (except for lleg)
    # also add colors
    mat_info = PhysicalMaterialInfo()
    my_deque = deque()
    my_deque.append(multibody_info.base_bodies[0])
    while my_deque:
        current = my_deque.popleft()
        if "hip" in current.body.name or "lleg" in current.body.name:
            mat_info.color = Color.fromRGB(0.1, 0.1, 0.1)
            mat_info.roughness = 0.8
            for visual in current.body.visuals:
                visual.material = PhysicalMaterial(mat_info)
        else:
            mat_info.color = Color.fromRGB(1, 0.8431, 0)
            mat_info.roughness = 0.4
            for visual in current.body.visuals:
                visual.material = PhysicalMaterial(mat_info)
        if "lleg" in current.body.name:
            continue
        for visual in current.body.visuals:
            visual.layers = LAYER_GRAPHICS
        for child in current.children:
            my_deque.append(child)

    # convert to multibody
    multibody = multibody_info.toMultibody(fc)
    multibody.ensureCurrent()
    multibody.resetData()
    assert multibody.isFinalized()
    return multibody


def createEnvironment(
    size: int, proxy_scene: ProxyScene
):
    mat_info = PhysicalMaterialInfo()
    mat_info.color = Color.fromHex("0d1440")
    texture_path = os.path.join(get_package_share_directory('spot_sim'), "resources", "whitegrid.png")
    mat_info.colorMap = Texture.lookupOrCreateTexture(texture_path)
    ground_mat = PhysicalMaterial(mat_info)
    ground_geom = BoxGeometry(size, size, 0.25)
    ground = ProxyScenePart(
        "ground", scene=proxy_scene, geometry=ground_geom, material=ground_mat, layers=LAYER_ALL
    )
    ground.setTranslation([0, 0, -0.65])

# helper to wrap angles
def wrap_to_pi(x):
    return (x + np.pi) % (2 * np.pi) - np.pi
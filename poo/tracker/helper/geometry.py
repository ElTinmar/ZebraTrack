import numpy as np
from numpy.typing import NDArray

def ellipse_direction(inertia_tensor: NDArray, heading: NDArray) -> NDArray:
    '''
    Get ellipse orientation: return the first eigenvector 
    of the inertia tensor, which corresponds to the principal 
    axis of the ellipse.
    Resolve 180 deg ambiguity by aligning with heading vector
    '''
    eigvals, eigvecs = np.linalg.eig(inertia_tensor)
    loc = np.argmax(abs(eigvals))
    eyedir = eigvecs[loc,:]
    # solve 180 deg ambiguity
    if eyedir @ heading < 0:
        eyedir = -eyedir
    return eyedir

def angle_between_vectors(v1: NDArray, v2: NDArray, signed: bool = True) -> float:
    v1_unit = v1 / np.linalg.norm(v1)
    v2_unit = v2 / np.linalg.norm(v2)
    signed_angle = np.arccos(np.dot(v1_unit,v2_unit))
    if signed:
        if np.cross(v1_unit,v2_unit) < 0:
            signed_angle = -signed_angle
    return signed_angle

def angdiff(a1: float, a2: float) -> float: 
    angle_diff = a1 - a2
    angle_diff = ((angle_diff + np.pi) % (2*np.pi)) - np.pi
    return angle_diff
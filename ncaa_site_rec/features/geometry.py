"""Geometry utilities for side-chain modeling."""

import numpy as np


def build_backbone_frame(
    n: np.ndarray,
    ca: np.ndarray,
    c: np.ndarray,
) -> np.ndarray:
    """Build an orthonormal local frame from N, CA, and C."""

    n = np.asarray(n, dtype=float)
    ca = np.asarray(ca, dtype=float)
    c = np.asarray(c, dtype=float)

    # First axis: CA -> C.
    e1 = c - ca
    e1 = e1 / np.linalg.norm(e1)

    # Second axis: N direction, perpendicular to e1.
    n_direction = n - ca
    e2 = n_direction - np.dot(n_direction, e1) * e1
    e2 = e2 / np.linalg.norm(e2)

    # Third axis: perpendicular to both.
    e3 = np.cross(e1, e2)

    return np.column_stack((e1, e2, e3))

def local_to_global(
    local_coords: np.ndarray,
    origin: np.ndarray,
    frame: np.ndarray,
) -> np.ndarray:
    """Transform local coordinates into the global coordinate system."""

    local_coords = np.asarray(local_coords, dtype=float)
    origin = np.asarray(origin, dtype=float)
    frame = np.asarray(frame, dtype=float)

    return local_coords @ frame.T + origin

def build_cb_direction(n, ca, c, chirality_sign=1.0):
    """Build a normalized CB direction from backbone coordinates."""

    import numpy as np

    n = np.asarray(n, dtype=float)
    ca = np.asarray(ca, dtype=float)
    c = np.asarray(c, dtype=float)

    v_n = n - ca
    v_c = c - ca

    v_n = v_n / np.linalg.norm(v_n)
    v_c = v_c / np.linalg.norm(v_c)

    bisector = -(v_n + v_c)
    bisector = bisector / np.linalg.norm(bisector)

    normal = np.cross(v_n, v_c)
    normal = normal / np.linalg.norm(normal)

    cb_direction = (
        bisector + chirality_sign * normal
    )

    cb_direction = cb_direction / np.linalg.norm(cb_direction)

    return cb_direction

def build_cb_from_angles(
    n,
    ca,
    c,
    ca_cb_length,
    n_ca_cb_angle,
    c_ca_cb_angle,
    chirality_sign=1.0,
):
    """Construct CB from backbone coordinates and target bond angles."""

    import numpy as np

    n = np.asarray(n, dtype=float)
    ca = np.asarray(ca, dtype=float)
    c = np.asarray(c, dtype=float)

    u = n - ca
    u = u / np.linalg.norm(u)

    v = c - ca
    v = v / np.linalg.norm(v)

    cos_theta = np.dot(u, v)
    sin_theta = np.sqrt(max(0.0, 1.0 - cos_theta**2))

    if sin_theta < 1e-8:
        raise ValueError("Backbone N, CA, C atoms are collinear.")

    e2 = (v - cos_theta * u) / sin_theta
    normal = np.cross(u, e2)

    alpha = np.radians(n_ca_cb_angle)
    beta = np.radians(c_ca_cb_angle)

    x = np.cos(alpha)
    y = (np.cos(beta) - x * cos_theta) / sin_theta

    z_squared = 1.0 - x**2 - y**2

    if z_squared < -1e-8:
        raise ValueError("Incompatible CB bond angle constraints.")

    z = chirality_sign * np.sqrt(max(0.0, z_squared))

    cb_direction = x * u + y * e2 + z * normal

    return ca + ca_cb_length * cb_direction

def align_sidechain_to_cb(
    coordinates,
    old_ca,
    old_cb,
    new_ca,
    new_cb,
    old_n,
    new_n,
):
    """Align a sidechain using CA-CB and N-CA reference directions."""

    import numpy as np

    coordinates = np.asarray(coordinates, dtype=float)

    def make_frame(ca, cb, n):
        x = cb - ca
        x = x / np.linalg.norm(x)

        reference = n - ca
        y = reference - np.dot(reference, x) * x
        y = y / np.linalg.norm(y)

        z = np.cross(x, y)

        return np.column_stack((x, y, z))

    old_frame = make_frame(old_ca, old_cb, old_n)
    new_frame = make_frame(new_ca, new_cb, new_n)

    rotation = new_frame @ old_frame.T

    aligned = (
        (coordinates - old_ca) @ rotation.T
        + new_ca
    )

    return aligned
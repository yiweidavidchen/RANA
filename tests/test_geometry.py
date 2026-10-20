import numpy as np
import pytest

from ncaa_site_rec.features.geometry import build_backbone_frame, local_to_global
from ncaa_site_rec.features.pazf import (
    generate_pazf_conformer,
    place_pazf_on_backbone,
    set_pazf_rotamer,
    generate_pazf_rotamers,
)
from rdkit.Chem import rdMolTransforms


def test_build_backbone_frame():
    """Check an orthonormal, right-handed backbone frame."""

    n = np.array([2.0, 3.0, 4.0])
    ca = np.array([1.0, 1.0, 1.0])
    c = np.array([3.0, 1.0, 1.0])

    frame = build_backbone_frame(n, ca, c)

    # The result must be a 3x3 matrix.
    assert frame.shape == (3, 3)

    # All three axes must be unit length and perpendicular.
    assert np.allclose(
        frame.T @ frame,
        np.eye(3),
        atol=1e-10,
    )

    # A right-handed coordinate system has determinant +1.
    assert np.linalg.det(frame) == pytest.approx(1.0)

    # The first axis should point from CA toward C.
    expected_e1 = (c - ca) / np.linalg.norm(c - ca)

    assert np.allclose(frame[:, 0], expected_e1)

    # The second axis should point toward the N-side
    # of the backbone plane.
    assert np.dot(frame[:, 1], n - ca) > 0

def test_local_to_global():
    """Test coordinate transformation with a rotated backbone frame."""

    n = np.array([5.0, 6.0, 5.0])
    ca = np.array([5.0, 5.0, 5.0])
    c = np.array([5.0, 5.0, 6.0])

    frame = build_backbone_frame(n, ca, c)

    local_points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 2.0, 3.0],
    ])

    global_points = local_to_global(local_points, ca, frame)

    expected = np.array([
        [5.0, 5.0, 5.0],
        [2.0, 7.0, 6.0],
    ])

    np.testing.assert_allclose(global_points, expected)

def test_place_pazf_preserves_geometry():
    """Placing pAzF should preserve all internal atom distances."""

    mol = generate_pazf_conformer(seed=42)

    original = np.asarray(
        mol.GetConformer().GetPositions(),
        dtype=float,
    )

    n = np.array([10.0, 21.0, 30.0])
    ca = np.array([10.0, 20.0, 30.0])
    c = np.array([11.0, 20.0, 30.0])

    placed = place_pazf_on_backbone(mol, n, ca, c)

    original_distances = np.linalg.norm(
        original[:, None, :] - original[None, :, :],
        axis=2,
    )

    placed_distances = np.linalg.norm(
        placed[:, None, :] - placed[None, :, :],
        axis=2,
    )

    assert placed.shape == original.shape

    np.testing.assert_allclose(
        placed[1],
        ca,
        atol=1e-10,
    )

    np.testing.assert_allclose(
        placed_distances,
        original_distances,
        atol=1e-10,
    )

def test_set_pazf_rotamer():
    """Test rotamer angles and preservation of the original molecule."""

    mol = generate_pazf_conformer(seed=42)

    original_conf = mol.GetConformer()
    original_chi1 = rdMolTransforms.GetDihedralDeg(
        original_conf, 0, 1, 2, 3
    )

    rotamer = set_pazf_rotamer(
        mol,
        chi1=-60.0,
        chi2=90.0,
    )

    conf = rotamer.GetConformer()

    chi1 = rdMolTransforms.GetDihedralDeg(
        conf, 0, 1, 2, 3
    )
    chi2 = rdMolTransforms.GetDihedralDeg(
        conf, 1, 2, 3, 4
    )

    assert np.isclose(chi1, -60.0, atol=1e-5)
    assert np.isclose(chi2, 90.0, atol=1e-5)

    # The original molecule should remain unchanged.
    assert np.isclose(
        rdMolTransforms.GetDihedralDeg(
            mol.GetConformer(), 0, 1, 2, 3
        ),
        original_chi1,
        atol=1e-5,
    )

def test_generate_pazf_rotamers():
    """Test generation of the initial pAzF rotamer grid."""

    mol = generate_pazf_conformer(seed=42)
    rotamers = generate_pazf_rotamers(mol)

    assert len(rotamers) == 12

    for chi1, chi2, rotamer in rotamers:
        assert rotamer.GetNumAtoms() == 25

        conf = rotamer.GetConformer()

        actual_chi1 = rdMolTransforms.GetDihedralDeg(
            conf, 0, 1, 2, 3
        )
        actual_chi2 = rdMolTransforms.GetDihedralDeg(
            conf, 1, 2, 3, 4
        )

        # Compare angles modulo 360 degrees.
        diff_chi1 = (actual_chi1 - chi1 + 180) % 360 - 180
        diff_chi2 = (actual_chi2 - chi2 + 180) % 360 - 180

        assert np.isclose(diff_chi1, 0.0, atol=1e-5)
        assert np.isclose(diff_chi2, 0.0, atol=1e-5)


def test_exclude_bonded_neighbor_overlaps():
    import numpy as np
    import pandas as pd

    from ncaa_site_rec.features.pazf import (
        exclude_bonded_neighbor_overlaps,
    )

    overlaps = np.ones((2, 3))

    environment = pd.DataFrame({
        "chain": ["A", "A", "A"],
        "residue_number": [20, 20, 21],
        "insertion_code": ["", "", ""],
        "atom_name": ["N", "C", "N"],
    })

    corrected = exclude_bonded_neighbor_overlaps(
        overlaps,
        sidechain_atom_indices=[2, 3],
        environment=environment,
        chain="A",
        residue_number=20,
    )

    expected = np.array([
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
    ])

    np.testing.assert_array_equal(corrected, expected)

    # The original matrix must remain unchanged.
    np.testing.assert_array_equal(
        overlaps,
        np.ones((2, 3)),
    )

def test_compute_steric_score():
    import numpy as np
    import pytest

    from ncaa_site_rec.features.pazf import (
        compute_steric_score,
    )

    overlaps = np.array([
        [0.0, 0.5],
        [1.0, 0.2],
    ])

    score = compute_steric_score(overlaps)

    assert score == pytest.approx(1.29)

    # A matrix without overlaps should have zero penalty.
    assert compute_steric_score(
        np.zeros((2, 3))
    ) == pytest.approx(0.0)

    # Negative overlap values are invalid.
    with pytest.raises(ValueError):
        compute_steric_score(
            np.array([[0.1, -0.2]])
        )

def test_angle_constrained_cb():
    import numpy as np

    from ncaa_site_rec.features.geometry import build_cb_from_angles

    n = np.array([0.0, 1.0, 0.0])
    ca = np.array([0.0, 0.0, 0.0])
    c = np.array([1.0, 0.0, 0.0])

    cb = build_cb_from_angles(
        n=n,
        ca=ca,
        c=c,
        ca_cb_length=1.50,
        n_ca_cb_angle=110.0,
        c_ca_cb_angle=114.0,
    )

    def angle(a, b):
        cosine = np.dot(a, b) / (
            np.linalg.norm(a) * np.linalg.norm(b)
        )
        return np.degrees(np.arccos(np.clip(cosine, -1, 1)))

    assert np.linalg.norm(cb - ca) == pytest.approx(1.50)
    assert angle(n - ca, cb - ca) == pytest.approx(110.0)
    assert angle(c - ca, cb - ca) == pytest.approx(114.0)


def test_sidechain_rigid_alignment():
    import numpy as np

    from ncaa_site_rec.features.geometry import align_sidechain_to_cb

    old_ca = np.array([0.0, 0.0, 0.0])
    old_cb = np.array([1.0, 0.0, 0.0])
    old_n = np.array([0.0, 1.0, 0.0])

    new_ca = np.array([5.0, 3.0, 2.0])
    new_cb = np.array([5.0, 4.0, 2.0])
    new_n = np.array([4.0, 3.0, 2.0])

    coords = np.array([
        old_ca,
        old_cb,
        old_n,
        [1.0, 1.0, 1.0],
    ])

    aligned = align_sidechain_to_cb(
        coordinates=coords,
        old_ca=old_ca,
        old_cb=old_cb,
        new_ca=new_ca,
        new_cb=new_cb,
        old_n=old_n,
        new_n=new_n,
    )

    assert np.allclose(aligned[0], new_ca)
    assert np.allclose(aligned[1], new_cb)

    original_distances = np.linalg.norm(
        coords[:, None, :] - coords[None, :, :],
        axis=-1,
    )

    aligned_distances = np.linalg.norm(
        aligned[:, None, :] - aligned[None, :, :],
        axis=-1,
    )

    assert np.allclose(original_distances, aligned_distances)
import numpy as np
import pandas as pd
import pytest

from ncaa_site_rec.features.site_ranking import rank_pazf_sites


@pytest.fixture
def sample_features():
    return pd.DataFrame({
        "residue_name": ["ALA", "GLY", "PRO", "SER", "ASN"],
        "status": [
            "scored", "scored", "scored", "scored", "skipped"
        ],
        "rsa": [0.5, 0.8, 0.3, 0.5, np.nan],
        "min_steric_score": [1.0, 2.0, 1.0, 5.0, np.nan],
        "low_clash_fraction": [0.75, 0.5, 0.75, 0.25, np.nan],
    })


def test_preserves_rows_and_original_columns(sample_features):
    ranked = rank_pazf_sites(sample_features)

    assert len(ranked) == len(sample_features)

    pd.testing.assert_frame_equal(
        ranked[sample_features.columns],
        sample_features,
    )


def test_steric_rank_ascending_with_ties(sample_features):
    ranked = rank_pazf_sites(sample_features)

    assert ranked["steric_rank"].tolist()[:4] == [
        1.0, 3.0, 1.0, 4.0
    ]


def test_rsa_rank_descending_with_ties(sample_features):
    ranked = rank_pazf_sites(sample_features)

    assert ranked["rsa_rank"].tolist()[:4] == [
        2.0, 1.0, 4.0, 2.0
    ]


def test_rotamer_robustness_rank(sample_features):
    ranked = rank_pazf_sites(sample_features)

    assert ranked["rotamer_robustness_rank"].tolist()[:4] == [
        1.0, 3.0, 1.0, 4.0
    ]


def test_skipped_residue_has_no_ranks(sample_features):
    ranked = rank_pazf_sites(sample_features)

    skipped = ranked.iloc[4]

    assert pd.isna(skipped["steric_rank"])
    assert pd.isna(skipped["rsa_rank"])
    assert pd.isna(skipped["rotamer_robustness_rank"])


def test_special_residue_flags(sample_features):
    ranked = rank_pazf_sites(sample_features)

    assert ranked.iloc[0]["special_residue_flag"] == ""
    assert (
        ranked.iloc[1]["special_residue_flag"]
        == "glycine_backbone_caution"
    )
    assert (
        ranked.iloc[2]["special_residue_flag"]
        == "proline_backbone_caution"
    )


def test_missing_required_column_raises(sample_features):
    incomplete = sample_features.drop(columns=["rsa"])

    with pytest.raises(ValueError, match="Missing required columns"):
        rank_pazf_sites(incomplete)


def test_does_not_mutate_input(sample_features):
    original = sample_features.copy(deep=True)

    rank_pazf_sites(sample_features)

    pd.testing.assert_frame_equal(sample_features, original)


def test_all_skipped_residues():
    df = pd.DataFrame({
        "residue_name": ["ALA", "SER"],
        "status": ["skipped", "skipped"],
        "rsa": [np.nan, np.nan],
        "min_steric_score": [np.nan, np.nan],
        "low_clash_fraction": [np.nan, np.nan],
    })

    ranked = rank_pazf_sites(df)

    assert ranked["steric_rank"].isna().all()
    assert ranked["rsa_rank"].isna().all()
    assert ranked["rotamer_robustness_rank"].isna().all()

def test_custom_fraction_threshold(sample_features):
    ranked = rank_pazf_sites(
        sample_features,
        favorable_fraction=0.8,
    )

    assert ranked.iloc[0]["candidate_tier"] == "geometry_limited"
    assert ranked.iloc[1]["candidate_tier"] == "geometry_limited"


def test_steric_threshold_boundary(sample_features):
    ranked = rank_pazf_sites(
        sample_features,
        low_clash_threshold=1.0,
    )

    assert ranked.iloc[0]["candidate_tier"] == "geometry_favorable"
    assert ranked.iloc[1]["candidate_tier"] == "geometry_unfavorable"


def test_invalid_threshold_raises(sample_features):
    with pytest.raises(ValueError, match="low_clash_threshold"):
        rank_pazf_sites(
            sample_features,
            low_clash_threshold=-1.0,
        )


def test_invalid_fraction_raises(sample_features):
    with pytest.raises(ValueError, match="favorable_fraction"):
        rank_pazf_sites(
            sample_features,
            favorable_fraction=1.5,
        )
import numpy as np
import pandas as pd


def rank_pazf_sites(
    feature_df: pd.DataFrame,
    low_clash_threshold: float = 10.0,
    favorable_fraction: float = 0.5,
) -> pd.DataFrame:
    """Add interpretable pAzF site rankings without a composite score."""

    if not np.isfinite(low_clash_threshold) or low_clash_threshold < 0:
        raise ValueError("low_clash_threshold must be finite and >= 0")

    if not np.isfinite(favorable_fraction) or not (
        0 < favorable_fraction <= 1
    ):
        raise ValueError("favorable_fraction must be in (0, 1]")

    required = [
        "residue_name",
        "status",
        "rsa",
        "min_steric_score",
        "low_clash_fraction",
    ]

    missing = [col for col in required if col not in feature_df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = feature_df.copy()

    result["steric_rank"] = np.nan
    result["rsa_rank"] = np.nan
    result["rotamer_robustness_rank"] = np.nan

    scored = result["status"].eq("scored")

    rank_specs = [
        ("min_steric_score", "steric_rank", True),
        ("rsa", "rsa_rank", False),
        ("low_clash_fraction", "rotamer_robustness_rank", False),
    ]

    for source, target, ascending in rank_specs:
        result.loc[scored, target] = (
            result.loc[scored, source]
            .rank(ascending=ascending, method="min")
        )

    result["special_residue_flag"] = result[
        "residue_name"
    ].map({
        "GLY": "glycine_backbone_caution",
        "PRO": "proline_backbone_caution",
    }).fillna("")

    result["candidate_tier"] = "not_evaluated"
    result["ranking_reason"] = "Site not evaluated"

    valid = (
        result["status"].eq("scored")
        & result["min_steric_score"].notna()
        & result["low_clash_fraction"].notna()
    )

    favorable = (
        valid
        & (result["min_steric_score"] <= low_clash_threshold)
        & (result["low_clash_fraction"] >= favorable_fraction)
    )

    limited = (
        valid
        & (result["min_steric_score"] <= low_clash_threshold)
        & (result["low_clash_fraction"] < favorable_fraction)
    )

    unfavorable = (
        valid
        & (result["min_steric_score"] > low_clash_threshold)
    )

    result.loc[favorable, "candidate_tier"] = "geometry_favorable"
    result.loc[limited, "candidate_tier"] = "geometry_limited"
    result.loc[unfavorable, "candidate_tier"] = "geometry_unfavorable"

    result.loc[favorable, "ranking_reason"] = (
        "Multiple low-clash pAzF rotamers"
    )
    result.loc[limited, "ranking_reason"] = (
        "Limited low-clash rotamer availability"
    )
    result.loc[unfavorable, "ranking_reason"] = (
        "No low-clash rotamer under current threshold"
    )

    return result
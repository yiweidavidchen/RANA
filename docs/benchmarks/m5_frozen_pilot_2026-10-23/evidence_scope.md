# Evidence scope and six-candidate review

The frozen input inventory is [the previous literature intake](../literature_m5_2026-10-23/README.md); its JSON digest and all ten supplied attachment digests are in `frozen_records.json`, together with the Wilkerson main/SI digests. This snapshot supplements rather than edits those records. [Wilding 2018](https://doi.org/10.1021/acssynbio.7b00316) and [Wilkerson 2020](https://doi.org/10.1021/acs.jcim.0c00725) are the T4L primary sources. [Khoshnejad 2018](https://doi.org/10.1021/acs.bioconjchem.8b00004) supplies the separate ferritin endpoint.

## Endpoint boundaries

| Endpoint class | Meaning retained here | Prohibited substitution |
| --- | --- | --- |
| Incorporation | Direct chemical identity/fidelity or specifically defined incorporation assay, if reported | Not inferred from expression, fluorescence, activity or conjugation |
| Expression | Full-length/soluble yield under its expression system and assay definition | Not inferred from geometric tier or a thermal shift |
| Stability | Assay-specific delta_Tm versus corresponding control | Not converted to activity, expression or a failed-incorporation label |
| Activity | Substrate/assay-specific activity and normalization | Not assumed from delta_Tm or EPR structural preservation |
| Conjugation | Reagent-, denominator- and condition-specific attachment endpoint | Not renamed as incorporation fraction or interchangeable across PEG/fluorophore/bead assays |

No untested, unreported or unselected site is assigned a negative label. No binary experimental label is introduced. Schinn's p-propargyloxyphenylalanine (**pPa**) is excluded from the current pAzF core, retained only for a future separately authorized ncAA extension; main PDF p2 (2413) and SI section 5.3 identify the chemical. See the prior availability matrix for its site/primer discrepancies.

## Candidate-by-candidate inclusion review

Eligibility for this **descriptive reference pilot** requires a reported single pAzF substitution, unconjugated thermal-shift endpoint, traceable source/error definition, and a verified reference chain/number/parent with a scored row. Exact full-construct equivalence is a separate, stronger standard. Decisions were made during source review and are not represented as blinded preregistration. No candidate is selected by agreement with RANA.

| Candidate | Original measurement and site evidence | Reference parent / identity | Decision |
| --- | --- | --- | --- |
| K16 | Wilding2018; Wilding main PDF p7 (516), Methods 3.2-3.3; p2 (511) site list; p4 (513), Figure 3A | 1L63 A / 16 / blank / LYS; complete N/CA/C | Include in reference pilot; full construct unresolved |
| S44 | Wilding2018; Wilding main PDF p7 (516), Methods 3.2-3.3; p2 (511) site list; p4 (513), Figure 3A | 1L63 A / 44 / blank / SER; complete N/CA/C | Include in reference pilot; full construct unresolved |
| N53 | Wilding2018; Wilding main PDF p7 (516), Methods 3.2-3.3; p2 (511) site list; p4 (513), Figure 3A | 1L63 A / 53 / blank / ASN; complete N/CA/C | Include in reference pilot; full construct unresolved |
| L91 | Wilding2018; Wilding main PDF p7 (516), Methods 3.2-3.3; p2 (511) site list; p4 (513), Figure 3A | 1L63 A / 91 / blank / LEU; complete N/CA/C | Include in reference pilot; full construct unresolved |
| K135 | Wilding2018; Wilding main PDF p7 (516), Methods 3.2-3.3; p2 (511) site list; p4 (513), Figure 3A | 1L63 A / 135 / blank / LYS; complete N/CA/C | Include in reference pilot; full construct unresolved |
| H31 | Wilkerson2020; Wilkerson main PDF p2 (5118), Proteins and Experimental Techniques; p3 (5119), Experimental Techniques; p4 Figure 2 | 1L63 A / 31 / blank / HIS; complete N/CA/C | Include in reference pilot; full construct unresolved |

All six candidates pass the endpoint and local identity checks. All six remain conditional with respect to complete construct equivalence; **zero** are fully sequence-matched verified observations. Wilding Methods 3.2 (PDF p7, 516) and Wilkerson Experimental Techniques (p2, 5118) both report Addgene cysteine-free T4L in pY71 with a C-terminal Strep-tag. Neither supplied record provides the full clone coding sequence, tag sequence or junction. The precise cysteine substitutions in the expressed clones are not independently sequence-confirmed here.

1L63 is a reference parent structure. Its SEQADV specifies C54T/C97A; SEQRES has 164 residues, but coordinates and the scan have 162. No missing C-terminal residues, tag or junction are built. All six candidate coordinates have the expected parent and complete N/CA/C, with author numbers used directly and a verified blank insertion code. Wilding's 2LZM Figure 1 depiction is recorded separately and does not establish the complete expression construct. Wilkerson names 1L63 as the control/reference and describes adding two terminal residues for its MD model; that MD preparation is not RANA's input.

## Separate or excluded conditions

| Evidence | Treatment in this freeze | Reason |
| --- | --- | --- |
| Wilding Ins163 | Separate, excluded from primary single-substitution table | Insertion between K162/N163, not replacement of N163; terminal reference coordinates incomplete |
| Wilding N53/Ins163 | Separate, excluded from primary table | Two modifications, one an insertion |
| Wilding 5 kDa / 20 kDa PEG states | Separate condition records; values not digitized here | Conjugated state changes the endpoint context; not the no-PEG pAzF substitution |
| Schinn pPa | Outside current pAzF core; future candidate | Different chemistry; no pAzF-library substitution |
| López tethering/EPR/DEER | Retained candidate evidence, outside this thermal-shift table | Spin labels, mutation combinations and attachment treatments need endpoint-specific reconstruction |
| Reddington sfGFP | Retained candidate evidence, outside T4L stability | Different protein, photophysical endpoints and positive-selection ascertainment |
| Ferritin eight-site TLC | Separate pAzF conjugation comparison | Different protein, assay and reported denominator; no pooling with delta_Tm |

The machine-readable separate/excluded registry enumerates both PEG sizes for all seven Wilding variants. No skipped/inapplicable state is silently labeled failed.

## Shared observations and source presentations

S44, N53 and L91 each have a single canonical `observation_id` shared by their Wilding 2018 and Wilkerson 2020 figure presentations. `observation_presentations.csv` has nine rows but only six underlying IDs. The five Wilding Figure 3A means/SD and the newly measured Wilkerson H31 Figure 2 mean/SEM supply the six master rows. Wilkerson's three reused presentations are not second observations. Their SEM label remains separate from the original SD label; neither exact N nor a conversion is invented. Prior four-site deduplication keys are retained alongside the new common IDs.

Within-paper replots are not extra data. Schinn's sfGFP reanalysis of Albayrak/Swartz 2013 and López's reproduced Fleissner 2011 control spectra stay external-source observations. Reddington's selected sites and references to earlier work are not a complete tested-negative library. These context records remain in the prior availability assessment rather than being re-counted in this pilot.

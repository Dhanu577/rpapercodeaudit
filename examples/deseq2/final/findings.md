# DESeq2 pilot case study findings

Verified source commit: `76c5f8523716804dbe0a9500b4b7e216c6af225c`. Package code was not executed.

The cleaned table retains **25 rows** from the 107-row draft and drops **82 rows**. Every retained paper sentence is an exact substring of the supplied `DESeq.txt` after whitespace normalization only.

## Verdict counts

| Verdict | Count |
|---|---:|
| consistent | 19 |
| partial | 5 |
| inconsistent | 1 |
| not found | 0 |
| not verified | 0 |

**Rows fully verified with a validated on-disk excerpt:** 25 of 25.
**Rows not verified:** 0.
**Human verification:** 0 rows; the `Checked by me?` field is `N` for every row.

## Most interesting inconsistencies and qualifications

### Row 12: Uncertainty — **partial**
Paper: DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Why: The paper describes uncertainty from posterior curvature, but the implementation computes a sandwich covariance that includes the ridge penalty and the unpenalized weighted information. That supports the claim only partially.
Code quote: Validated code quote: “// sigma is the covariance matrix for the betas sigma = (x.t() * (x.each_col() % w_vec) + ridge).i() * x.t() * (x.each_col() % w_vec) * (x.t() * (x.each_col() % w_vec) + ridge).i(); contrast_num.row(i) = contrast.t() * beta_hat;”.
Issue category: implementation differs from described formula
Source: [src/DESeq2.cpp:451-453](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L451-L453)

### Row 16: Observed Fisher information calculation — **inconsistent**
Paper: Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
Why: The paper defines shrinkage using an observed Fisher-information quantity. The cited implementation lines show mean/dispersion-dependent GLM weights and ridge fitting, but do not calculate the paper’s stated observed second derivative as such; the draft claim is therefore inconsistent as written.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: implementation differs from described formula
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 18: Relationship between Fisher information and shrinkage — **partial**
Paper: ThepriorinfluencestheMAPesti matewhenthedensityofthelikelihoodandthepriorare multipliedtocalculatetheposterior.
Why: The weights are related to the information calculation: fitted means, dispersion, and optional observation weights affect coefficient information. However, this snippet does not itself show the zero-centred prior being applied, the MAP estimate being formed, or the resulting movement toward zero. It is therefore partial evidence for the complete paper sentence.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: evidence is incomplete for the full prior-based MAP shrinkage claim
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 24: Gene-specific shrinkage strength — **partial**
Paper: The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
Why: The paper describes information-dependent, gene-varying shrinkage. The code estimates prior variance from a matrix of gene-wise MLE coefficients, while the amount of shrinkage also emerges from each gene’s likelihood; there is no separate explicit per-gene shrinkage-strength parameter.
Code quote: Validated code quote: “objectNZ <- object[!mcols(object)$allZero,,drop=FALSE] betaMatrix <- as.matrix(mcols(objectNZ)[,grep("MLE_", names(mcols(object))),drop=FALSE])”.
Issue category: other
Source: [R/core.R:1611-1613](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1611-L1613)

### Row 30: Behaviour for very low-count genes — **partial**
Paper: For genes with very low read count, even an estimate of zero LFC is not significant, as the large uncertainty of the estimate does not allow us to exclude that the gene may in truth be more than weakly affected by the experimental condition.
Why: The low-count behavior is an emergent consequence of GLM weights, uncertainty, and the prior rather than a dedicated low-count rule in the cited code. The direction is plausible, but the implementation does not directly encode the paper sentence as a branch.
Code quote: Validated code quote: “w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: other
Source: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

## Limitations

The cleaned set is a deliberately narrow core-method review, not a claim-coverage benchmark. Rows about rlog/VST, plotting, generic testing APIs, and downstream/benchmark analyses were dropped. The keyword locator returns candidates and can overproduce locations; a non-overlap with the pilot table is not proof of falsity. The pilot table has 107 rows but only 85 explicit file/range references, and its paper-sentence column was blank, so row-level semantic matching is necessarily conservative. The vignette change notes identify post-2014 behavior where the checked-in documentation says the implementation evolved.

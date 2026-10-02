# DESeq2 pilot case study findings

Verified source commit: `76c5f8523716804dbe0a9500b4b7e216c6af225c`. Package code was not executed.

The cleaned table retains **24 rows** from the 107-row draft and drops **83 rows**. Every retained exact paper sentence is an exact substring of the supplied `DESeq.txt` after whitespace normalization only.

## Verdict counts

| Verdict | Count |
|---|---:|
| consistent | 18 |
| partial | 4 |
| inconsistent | 0 |
| not found | 0 |
| not verified | 2 |

**Rows with validated on-disk excerpts:** 24 of 24.
**Rows not verified:** 2.
There are **six rows human-checked** and **eighteen AI-assisted only**.

## Difference from previous totals

Previous totals were 18 consistent, 4 partial, 2 not verified, 0 inconsistent, and 0 not found. Current table totals are consistent 18 (+0), partial 4 (+0), not verified 2 (+0), inconsistent 0 (+0), not found 0 (+0).

## Qualified findings (all partial, not verified, or inconsistent rows)

### Row 2: Initial estimation — **not verified**
Paper: To get a gene-wise dis persion estimate for a gene i, we start by fitting a nega tive binomial GLM without an LFC prior for the design matrix X to the gene’s count data.
Why: Validated code quote: “# fit the negative binomial GLM without a prior, # used to construct the prior variances # and for the hat matrix diagonals for calculating Cook's distance”.
Code quote: Validated code quote: “# fit the negative binomial GLM without a prior, # used to construct the prior variances # and for the hat matrix diagonals for calculating Cook's distance”.
Issue category: cited excerpt consists only of comments and describes a different step
Source: [R/fitNbinomGLMs.R:253-255](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L253-L255)

### Row 12: Uncertainty — **partial**
Paper: DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Why: The paper describes uncertainty from posterior curvature, but the implementation computes a sandwich covariance that includes the ridge penalty and the unpenalized weighted information. That supports the claim only partially.
Code quote: Validated code quote: “// sigma is the covariance matrix for the betas sigma = (x.t() * (x.each_col() % w_vec) + ridge).i() * x.t() * (x.each_col() % w_vec) * (x.t() * (x.each_col() % w_vec) + ridge).i(); contrast_num.row(i) = contrast.t() * beta_hat;”.
Issue category: implementation differs from described formula
Source: [src/DESeq2.cpp:451-453](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L451-L453)

### Row 16: Observed Fisher information calculation — **partial**
Paper: Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
Why: The cited lines calculate negative-binomial GLM working weights that contribute to coefficient-fitting information. They do not themselves calculate or identify observed Fisher information, and they do not show prior-driven MAP shrinkage. The code is related, so the evidence is partial rather than inconsistent.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: evidence is insufficient for the full observed-Fisher-information and MAP-shrinkage claim
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 18: Relationship between Fisher information and shrinkage — **partial**
Paper: The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
Why: The weights are related to the information calculation: fitted means, dispersion, and optional observation weights affect coefficient information. However, this snippet does not itself show the zero-centred prior being applied, the MAP estimate being formed, or the resulting movement toward zero. It is therefore partial evidence for the complete paper sentence.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: evidence is incomplete for the full prior-based MAP shrinkage claim
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 30: Behaviour for very low-count genes — **not verified**
Paper: For genes with very low read count, even an estimate of zero LFC is not significant, as the large uncertainty of the estimate does not allow us to exclude that the gene may in truth be more than weakly affected by the experimental condition.
Why: The cited lines calculate GLM working weights only. They do not test significance, determine whether a zero LFC can be excluded, or demonstrate the behavior of very low-count genes. This is a mismatch between the claim and the cited evidence, not proof that the repository lacks the behavior.
Code quote: Validated code quote: “w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: not supported by cited lines
Source: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

### Row 51: Relationship between sample size and shrinkage strength — **partial**
Paper: Furthermore, as the degrees of freedom increase, and the experiment pro vides more information for LFC estimation, the shrunken estimates will converge to the unshrunken estimates.
Why: The code uses residual degrees of freedom when estimating dispersion-prior variance, but it does not expose a direct function mapping sample size to LFC shrinkage. The paper’s convergence statement is therefore only indirectly supported.
Code quote: Validated code quote: “m <- nrow(modelMatrix) p <- ncol(modelMatrix)”.
Issue category: other
Source: [R/core.R:1151-1153](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1151-L1153)

## Limitations

The cleaned set is a deliberately narrow core-method review, not a claim-coverage benchmark. Rows about rlog/VST, plotting, generic testing APIs, and downstream/benchmark analyses were dropped. The keyword locator returns candidates and can overproduce locations; a non-overlap with the pilot table is not proof of falsity. The pilot table has 107 rows but only 85 explicit file/range references, and its paper-sentence column was blank, so row-level semantic matching is necessarily conservative. The same excerpt supported two different paper sentences in rows 16 and 18, so those citations should not be treated as independent proof. Rows 20 and 30 use the same generic excerpt (`src/DESeq2.cpp:337-339`), so their citations are not independent evidence. Row 2’s cited excerpt consists only of comments and describes a different step from the paper sentence. Suggested stronger evidence is explicitly unverified by the author. The vignette change notes identify post-2014 behavior where the checked-in documentation says the implementation evolved.

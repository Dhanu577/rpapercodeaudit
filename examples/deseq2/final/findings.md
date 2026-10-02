# DESeq2 pilot case study findings

Verified source commit: `76c5f8523716804dbe0a9500b4b7e216c6af225c`. Package code was not executed.

The cleaned table retains **24 rows** from the 107-row draft and drops **83 rows**. Every retained exact paper sentence is an exact substring of the supplied `DESeq.txt` after whitespace normalization only.

## Current Verdict counts

| Verdict | Count |
|---|---:|
| consistent | 18 |
| partial | 4 |
| inconsistent | 0 |
| not found | 0 |
| not verified | 2 |

## Combined view counts

The combined view uses the AI second-review verdict for rows 6–61 and the current Verdict for rows 2, 4, 12, 16, 18, and 30.

| Combined verdict | Count |
|---|---:|
| consistent | 5 |
| partial | 11 |
| inconsistent | 0 |
| not found | 0 |
| not verified | 8 |

**Rows with validated on-disk excerpts:** 24 of 24.
**Rows not verified in the current view:** 2.
There are **six rows human-checked** and **eighteen AI-assisted only**.

## Difference from previous current-view totals

Previous totals were 18 consistent, 4 partial, 2 not verified, 0 inconsistent, and 0 not found. Current table totals are consistent 18 (+0), partial 4 (+0), not verified 2 (+0), inconsistent 0 (+0), not found 0 (+0).

## Qualified findings under either view

### Row 2: Initial estimation — current **not verified**, combined **not verified**
Paper: To get a gene-wise dis persion estimate for a gene i, we start by fitting a nega tive binomial GLM without an LFC prior for the design matrix X to the gene’s count data.
Why: Validated code quote: “# fit the negative binomial GLM without a prior, # used to construct the prior variances # and for the hat matrix diagonals for calculating Cook's distance”.
Code quote: Validated code quote: “# fit the negative binomial GLM without a prior, # used to construct the prior variances # and for the hat matrix diagonals for calculating Cook's distance”.
Issue category: cited excerpt consists only of comments and describes a different step
Source: [R/fitNbinomGLMs.R:253-255](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L253-L255)

### Row 6: Prior fitting — current **consistent**, combined **partial**
Paper: Theestimate of theLFCpriorwidthiscalculatedas follows.
Why: only the function signature and MLE beta extraction; input to the prior width, not the calculation Validated code quote: “modelMatrix=NULL) { objectNZ <- object[!mcols(object)$allZero,,drop=FALSE] betaMatrix <- as.matrix(mcols(objectNZ)[,grep("MLE_", names(mcols(object))),drop=FALSE])”.
Code quote: Validated code quote: “modelMatrix=NULL) { objectNZ <- object[!mcols(object)$allZero,,drop=FALSE] betaMatrix <- as.matrix(mcols(objectNZ)[,grep("MLE_", names(mcols(object))),drop=FALSE])”.
Issue category: none
Source: [R/core.R:1610-1613](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1610-L1613)

### Row 10: Final estimate — current **consistent**, combined **partial**
Paper: finalMAPcoefficientestimates: ⃗βi=argmax ⃗β ⎛ ⎝ j logfNB Kij;μj(⃗β),αi + (⃗β) ⎞ ⎠, where μj(⃗β)=sije rxjrβr, (⃗β)= r −β2r 2σ2 r , andαi isthefinaldispersionestimateforgenei, i.
Why: comment and zero-variance check; does not show the penalized objective or the refit Validated code quote: “# refit the negative binomial GLM with a prior on betas if (any(betaPriorVar == 0)) { stop("beta prior variances are equal to zero for some variables")”.
Code quote: Validated code quote: “# refit the negative binomial GLM with a prior on betas if (any(betaPriorVar == 0)) { stop("beta prior variances are equal to zero for some variables")”.
Issue category: none
Source: [R/fitNbinomGLMs.R:307-309](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L307-L309)

### Row 12: Uncertainty — current **partial**, combined **partial**
Paper: DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Why: The paper describes uncertainty from posterior curvature, but the implementation computes a sandwich covariance that includes the ridge penalty and the unpenalized weighted information. That supports the claim only partially.
Code quote: Validated code quote: “// sigma is the covariance matrix for the betas sigma = (x.t() * (x.each_col() % w_vec) + ridge).i() * x.t() * (x.each_col() % w_vec) * (x.t() * (x.each_col() % w_vec) + ridge).i(); contrast_num.row(i) = contrast.t() * beta_hat;”.
Issue category: implementation differs from described formula
Source: [src/DESeq2.cpp:451-453](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L451-L453)

### Row 14: Two-stage procedure — current **consistent**, combined **not verified**
Paper: We get final dispersion estimates from this model in three steps, which implement a computationally fast approximation to a full empirical Bayes treatment.
Why: comments only; describe the two LFC fits, but the sentence is about the three-step dispersion procedure Validated code quote: “# this function calls fitNbinomGLMs() twice: # 1 - without the beta prior, in order to calculate the #     beta prior variance and hat matrix”.
Code quote: Validated code quote: “# this function calls fitNbinomGLMs() twice: # 1 - without the beta prior, in order to calculate the #     beta prior variance and hat matrix”.
Issue category: none
Source: [R/fitNbinomGLMs.R:238-240](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L238-L240)

### Row 16: Observed Fisher information calculation — current **partial**, combined **partial**
Paper: Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
Why: The cited lines calculate negative-binomial GLM working weights that contribute to coefficient-fitting information. They do not themselves calculate or identify observed Fisher information, and they do not show prior-driven MAP shrinkage. The code is related, so the evidence is partial rather than inconsistent.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: evidence is insufficient for the full observed-Fisher-information and MAP-shrinkage claim
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 18: Relationship between Fisher information and shrinkage — current **partial**, combined **partial**
Paper: The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
Why: The weights are related to the information calculation: fitted means, dispersion, and optional observation weights affect coefficient information. However, this snippet does not itself show the zero-centred prior being applied, the MAP estimate being formed, or the resulting movement toward zero. It is therefore partial evidence for the complete paper sentence.
Code quote: Validated code quote: “if (useWeights) { w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: evidence is incomplete for the full prior-based MAP shrinkage claim
Source: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 20: Dispersion-dependent uncertainty — current **consistent**, combined **partial**
Paper: theobservedFisherinformation, orpeakednessofthelogarithmoftheprofilelikelihood,is influencedbyanumberof factors includingthedegrees offreedom,theestimatedmeancountsμij,andthegene’s dispersionestimateαi.
Why: weights show dependence on mean and dispersion, not degrees of freedom; same generic excerpt as rows 16, 18, 30 Validated code quote: “w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Code quote: Validated code quote: “w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: none
Source: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

### Row 25: Gene-wise estimation — MLE dispersion estimation — current **consistent**, combined **not verified**
Paper: We first use the count data for each gene separately to get preliminary gene-wise dispersion estimates αgw i by maximum-likelihood estimation.
Why: comment about iteration and variable setup; the dispersion MLE call is not shown Validated code quote: “# below, iterate between mean and dispersion estimation (niter) times fitidx <- rep(TRUE,nrow(objectNZ)) mu <- matrix(0, nrow=nrow(objectNZ), ncol=ncol(objectNZ))”.
Code quote: Validated code quote: “# below, iterate between mean and dispersion estimation (niter) times fitidx <- rep(TRUE,nrow(objectNZ)) mu <- matrix(0, nrow=nrow(objectNZ), ncol=ncol(objectNZ))”.
Issue category: none
Source: [R/core.R:745-747](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L745-L747)

### Row 27: Trend fitting — dispersion versus mean relationship — current **consistent**, combined **not verified**
Paper: A parametric curve of the form (6) is fit by regressing the gene-wise dispersion estimates αgw i onto the means of the normalized counts, ¯μi.
Why: function signature only; the regression call is not shown Validated code quote: “estimateDispersionsFit <- function(object,fitType=c("parametric","local","mean", "glmGamPoi"), minDisp=1e-8, quiet=FALSE) {”.
Code quote: Validated code quote: “estimateDispersionsFit <- function(object,fitType=c("parametric","local","mean", "glmGamPoi"), minDisp=1e-8, quiet=FALSE) {”.
Issue category: none
Source: [R/core.R:865-867](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L865-L867)

### Row 28: Whether shrinkage moves uncertain estimates towards zero — current **consistent**, combined **partial**
Paper: Because the shrinkage moves large LFCs that are not well supported by the data toward zero, the agreement between the two independent sample groups increases considerably.
Why: shows the zero-centred prior in the posterior, not shrinkage toward zero Validated code quote: “sum(logLikeVector) } logPrior <- sum(dnorm(p,0,sqrt(1/lambda),log=TRUE)) negLogPost <- -1 * (logLike + logPrior)”.
Code quote: Validated code quote: “sum(logLikeVector) } logPrior <- sum(dnorm(p,0,sqrt(1/lambda),log=TRUE)) negLogPost <- -1 * (logLike + logPrior)”.
Issue category: none
Source: [R/fitNbinomGLMs.R:367-370](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L367-L370)

### Row 30: Behaviour for very low-count genes — current **not verified**, combined **not verified**
Paper: For genes with very low read count, even an estimate of zero LFC is not significant, as the large uncertainty of the estimate does not allow us to exclude that the gene may in truth be more than weakly affected by the experimental condition.
Why: The cited lines calculate GLM working weights only. They do not test significance, determine whether a zero LFC can be excluded, or demonstrate the behavior of very low-count genes. This is a mismatch between the claim and the cited evidence, not proof that the repository lacks the behavior.
Code quote: Validated code quote: “w_vec = weights.row(i).t() % mu_hat/(1.0 + alpha_hat(i) * mu_hat); w_sqrt_vec = sqrt(w_vec); } else {”.
Issue category: not supported by cited lines
Source: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

### Row 33: Final estimation — gene-specific MAP dispersion — current **consistent**, combined **partial**
Paper: Instead of the MAP value , we use the gene-wise estimate αgw i i i where mad stands for the median absolute deviation, divided as usual by the scaling factor −1(3/4).
Why: shows outlier detection, not the step of using the gene-wise estimate instead of the MAP Validated code quote: “# from all the genes, not only those from below dispOutlier <- log(mcols(objectNZ)$dispGeneEst) > log(mcols(objectNZ)$dispFit) + outlierSD * sqrt(varLogDispEsts)”.
Code quote: Validated code quote: “# from all the genes, not only those from below dispOutlier <- log(mcols(objectNZ)$dispGeneEst) > log(mcols(objectNZ)$dispFit) + outlierSD * sqrt(varLogDispEsts)”.
Issue category: none
Source: [R/core.R:1111-1114](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1111-L1114)

### Row 35: Adaptive shrinkage — strength based on estimated prior and degrees of freedom — current **consistent**, combined **not verified**
Paper: We use an empiri cal Bayes approach (Methods), which lets the strength of shrinkage depend (i) on an estimate of how close true dis persion values tend to be to the fit and (ii) on the degrees of freedom: as the sample size increases, the shrinkage decreases in strength, and eventually becomes negligi ble.
Why: only p <- ncol(...) and a comment about low degrees of freedom Validated code quote: “p <- ncol(modelMatrix) # if the residual degrees of freedom is between 1 and 3, the distribution # of log dispersions is especially asymmetric and poorly estimated”.
Code quote: Validated code quote: “p <- ncol(modelMatrix) # if the residual degrees of freedom is between 1 and 3, the distribution # of log dispersions is especially asymmetric and poorly estimated”.
Issue category: none
Source: [R/core.R:1152-1155](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1152-L1155)

### Row 41: Identification of dispersion outliers — current **consistent**, combined **not verified**
Paper: For some genes, the gene-wise esti mate αgw i canbesofarabovethepriorexpectationαtr(¯μi) that it would be unreasonable to assume that the prior is suitable for the gene.
Why: comments only; stronger code is at lines 1112-1114 (fixable) Validated code quote: “# detect outliers which have gene-wise estimates # outlierSD * standard deviation of log gene-wise estimates # above the fitted mean (prior mean)”.
Code quote: Validated code quote: “# detect outliers which have gene-wise estimates # outlierSD * standard deviation of log gene-wise estimates # above the fitted mean (prior mean)”.
Issue category: none
Source: [R/core.R:1106-1108](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1106-L1108)

### Row 49: Degrees of freedom calculation — current **consistent**, combined **partial**
Paper: The sampling distribution of a dispersion estimator is approx imately a scaled χ2 distribution with m − p degrees of freedom, withm thenumber ofsamplesandpthenumber of coefficients.
Why: only m and p are set; the m-p degrees of freedom appear at line 1198 Validated code quote: “m <- nrow(modelMatrix) p <- ncol(modelMatrix)”.
Code quote: Validated code quote: “m <- nrow(modelMatrix) p <- ncol(modelMatrix)”.
Issue category: none
Source: [R/core.R:1151-1153](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1151-L1153)

### Row 51: Relationship between sample size and shrinkage strength — current **partial**, combined **not verified**
Paper: Furthermore, as the degrees of freedom increase, and the experiment pro vides more information for LFC estimation, the shrunken estimates will converge to the unshrunken estimates.
Why: lines belong to dispersion-prior code; the sentence is about LFC shrinkage converging The code uses residual degrees of freedom when estimating dispersion-prior variance, but it does not expose a direct function mapping sample size to LFC shrinkage. The paper’s convergence statement is therefore only indirectly supported.
Code quote: Validated code quote: “m <- nrow(modelMatrix) p <- ncol(modelMatrix)”.
Issue category: other
Source: [R/core.R:1151-1153](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1151-L1153)

### Row 57: Prior distribution used for LFC estimation — current **consistent**, combined **partial**
Paper: This distribution is used as a prior on LFCs in a second round of GLM fits, and the MAP estimates are kept as final estimates of LFC.
Why: shows prior variance estimation, not the second GLM fit or MAP estimates being kept Validated code quote: “betaPriorVar <- estimateBetaPriorVar(dds, modelMatrix=modelMatrix) stopifnot(length(betaPriorVar) > 0) # parallel fork”.
Code quote: Validated code quote: “betaPriorVar <- estimateBetaPriorVar(dds, modelMatrix=modelMatrix) stopifnot(length(betaPriorVar) > 0) # parallel fork”.
Issue category: none
Source: [R/lfcShrink.R:298-300](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/lfcShrink.R#L298-L300)

### Row 61: Posterior uncertainty or standard error — current **consistent**, combined **partial**
Paper: DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Why: fit$sd reported as lfcSE; the curvature calculation is not in this file Validated code quote: “res$log2FoldChange <- log2(exp(1)) * fit$map[,coefNum] res$lfcSE <- log2(exp(1)) * fit$sd[,coefNum] mcols(res)$description[2] <- sub("MLE","MAP",mcols(res)$description[2])”.
Code quote: Validated code quote: “res$log2FoldChange <- log2(exp(1)) * fit$map[,coefNum] res$lfcSE <- log2(exp(1)) * fit$sd[,coefNum] mcols(res)$description[2] <- sub("MLE","MAP",mcols(res)$description[2])”.
Issue category: none
Source: [R/lfcShrink.R:432-434](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/lfcShrink.R#L432-L434)

## Limitations

The cleaned set is a deliberately narrow core-method review, not a claim-coverage benchmark. Rows about rlog/VST, plotting, generic testing APIs, and downstream/benchmark analyses were dropped. The keyword locator returns candidates and can overproduce locations; a non-overlap with the pilot table is not proof of falsity. The pilot table has 107 rows but only 85 explicit file/range references, and its paper-sentence column was blank, so row-level semantic matching is necessarily conservative. The same excerpt supported two different paper sentences in rows 16 and 18, so those citations should not be treated as independent proof. Rows 16, 18, 20 and 30 use the same generic excerpt (`src/DESeq2.cpp:336-339`), so their citations are not independent evidence. Rows 12 and 61 cite the same paper sentence. Many AI-assisted “consistent” verdicts rested on setup code, function signatures, or comments, as the second review shows. Row 2’s cited excerpt consists only of comments and describes a different step from the paper sentence. Suggested stronger evidence is explicitly unverified by the author. The vignette change notes identify post-2014 behavior where the checked-in documentation says the implementation evolved.

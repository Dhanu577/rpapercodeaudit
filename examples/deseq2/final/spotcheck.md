# DESeq2 spot checks

All 24 retained rows are listed below. Human-checked rows reflect the author’s supplied review; all other rows are AI-assisted only, not yet human-verified.

## Human-checked rows

### Row 2: Initial estimation
Verdict: **not supported by cited excerpt**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): To get a gene-wise dis persion estimate for a gene i, we start by fitting a nega tive binomial GLM without an LFC prior for the design matrix X to the gene’s count data.
Code: [R/fitNbinomGLMs.R:253-255](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L253-L255)

### Row 4: Prior
Verdict: **consistent**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): To incorporate empirical Bayes shrinkage of LFCs, we postulate a zero-centered normal prior for the coefficients βir of model (2) that represent LFCs (i.
Code: [R/fitNbinomGLMs.R:367-370](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L367-L370)

### Row 12: Uncertainty
Verdict: **partial**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Code: [src/DESeq2.cpp:451-453](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L451-L453)

### Row 16: Observed Fisher information calculation
Verdict: **partial**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
Code: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 18: Relationship between Fisher information and shrinkage
Verdict: **partial**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
Code: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)

### Row 30: Behaviour for very low-count genes
Verdict: **not supported by cited excerpt**
Second-review verdict: *(blank — human-checked row)*
Checked by me?: **Y**
Paper sentence (readable): For genes with very low read count, even an estimate of zero LFC is not significant, as the large uncertainty of the estimate does not allow us to exclude that the gene may in truth be more than weakly affected by the experimental condition.
Code: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

## AI-assisted only rows

### Row 6: Prior fitting
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): Theestimate of theLFCpriorwidthiscalculatedas follows.
Code: [R/core.R:1610-1613](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1610-L1613)

### Row 10: Final estimate
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): finalMAPcoefficientestimates: ⃗βi=argmax ⃗β ⎛ ⎝ j logfNB Kij;μj(⃗β),αi + (⃗β) ⎞ ⎠, where μj(⃗β)=sije rxjrβr, (⃗β)= r −β2r 2σ2 r , andαi isthefinaldispersionestimateforgenei, i.
Code: [R/fitNbinomGLMs.R:307-309](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L307-L309)

### Row 14: Two-stage procedure
Verdict: **consistent**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): We get final dispersion estimates from this model in three steps, which implement a computationally fast approximation to a full empirical Bayes treatment.
Code: [R/fitNbinomGLMs.R:238-240](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L238-L240)

### Row 20: Dispersion-dependent uncertainty
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): theobservedFisherinformation, orpeakednessofthelogarithmoftheprofilelikelihood,is influencedbyanumberof factors includingthedegrees offreedom,theestimatedmeancountsμij,andthegene’s dispersionestimateαi.
Code: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)

### Row 21: Median-based estimation of size factors
Verdict: **consistent**
Second-review verdict: **consistent**
AI-assisted only, not yet human-verified.
Paper sentence (readable): By default, the normalization constants sij are consid ered constant within a sample, sij = sj,andareestimated with the median-of-ratios method previously described and used in DESeq [4] and DEXSeq [30]: ⎛ ⎞ where ⃗c represents a numeric contrast, e.
Code: [R/core.R:536-538](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L536-L538)

### Row 25: Gene-wise estimation — MLE dispersion estimation
Verdict: **consistent**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): We first use the count data for each gene separately to get preliminary gene-wise dispersion estimates αgw i by maximum-likelihood estimation.
Code: [R/core.R:745-747](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L745-L747)

### Row 27: Trend fitting — dispersion versus mean relationship
Verdict: **consistent**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): A parametric curve of the form (6) is fit by regressing the gene-wise dispersion estimates αgw i onto the means of the normalized counts, ¯μi.
Code: [R/core.R:865-867](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L865-L867)

### Row 28: Whether shrinkage moves uncertain estimates towards zero
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): Because the shrinkage moves large LFCs that are not well supported by the data toward zero, the agreement between the two independent sample groups increases considerably.
Code: [R/fitNbinomGLMs.R:367-370](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L367-L370)

### Row 29: Prior estimation — empirical prior variance estimation
Verdict: **consistent**
Second-review verdict: **consistent**
AI-assisted only, not yet human-verified.
Paper sentence (readable): The prior variance σ2 d is thresholded at a minimal value of 0.
Code: [R/core.R:1197-1200](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1197-L1200)

### Row 33: Final estimation — gene-specific MAP dispersion
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): Instead of the MAP value , we use the gene-wise estimate αgw i i i where mad stands for the median absolute deviation, divided as usual by the scaling factor −1(3/4).
Code: [R/core.R:1111-1114](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1111-L1114)

### Row 35: Adaptive shrinkage — strength based on estimated prior and degrees of freedom
Verdict: **consistent**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): We use an empiri cal Bayes approach (Methods), which lets the strength of shrinkage depend (i) on an estimate of how close true dis persion values tend to be to the fit and (ii) on the degrees of freedom: as the sample size increases, the shrinkage decreases in strength, and eventually becomes negligi ble.
Code: [R/core.R:1152-1155](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1152-L1155)

### Row 39: Calculation or use of residual standard deviation
Verdict: **consistent**
Second-review verdict: **consistent**
AI-assisted only, not yet human-verified.
Paper sentence (readable): To avoid inflation of σ2 d due to dispersion outliers (i.
Code: [R/methods.R:178-180](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/methods.R#L178-L180)

### Row 41: Identification of dispersion outliers
Verdict: **consistent**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): For some genes, the gene-wise esti mate αgw i canbesofarabovethepriorexpectationαtr(¯μi) that it would be unreasonable to assume that the prior is suitable for the gene.
Code: [R/core.R:1106-1108](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1106-L1108)

### Row 43: The two-standard-deviation threshold
Verdict: **consistent**
Second-review verdict: **consistent**
AI-assisted only, not yet human-verified.
Paper sentence (readable): Therefore, we use the heuris tic of considering a gene as a dispersion outlier, if the residual from the trend fit is more than two standard deviations of logarithmic residuals, slr (see Equation (8)), above the fit, i.
Code: [R/core.R:944-946](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L944-L946)

### Row 49: Degrees of freedom calculation
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): The sampling distribution of a dispersion estimator is approx imately a scaled χ2 distribution with m − p degrees of freedom, withm thenumber ofsamplesandpthenumber of coefficients.
Code: [R/core.R:1151-1153](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1151-L1153)

### Row 51: Relationship between sample size and shrinkage strength
Verdict: **partial**
Second-review verdict: **not verified**
AI-assisted only, not yet human-verified.
Paper sentence (readable): Furthermore, as the degrees of freedom increase, and the experiment pro vides more information for LFC estimation, the shrunken estimates will converge to the unshrunken estimates.
Code: [R/core.R:1151-1153](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/core.R#L1151-L1153)

### Row 57: Prior distribution used for LFC estimation
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): This distribution is used as a prior on LFCs in a second round of GLM fits, and the MAP estimates are kept as final estimates of LFC.
Code: [R/lfcShrink.R:298-300](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/lfcShrink.R#L298-L300)

### Row 61: Posterior uncertainty or standard error
Verdict: **consistent**
Second-review verdict: **partial**
AI-assisted only, not yet human-verified.
Paper sentence (readable): DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Code: [R/lfcShrink.R:432-434](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/lfcShrink.R#L432-L434)


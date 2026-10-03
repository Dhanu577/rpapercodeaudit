# Clean paper text comparison — PARTIAL Gemini experiment

## Scope and status

All checks in this report are offline. No Gemini or other model/API call was made. Sentence validation used the unchanged project `validate_claims()` function; the deterministic run used the unchanged `extract_claims(..., mode="no-api")` path. Saved proposals and pilot sentences were not edited.

**The Gemini experiment remains PARTIAL:** run1 completed only chunks 2–7 (63 saved proposals); chunks 1, 8, and 9 are missing. Run2 is incomplete and produced no successful chunk. Model: `gemini-3.8-flash`; response/resolved version: `gemini-3.8-flash`; temperature `0`; OpenAI-compatible base URL `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`; Bearer authorization sourced from the secret environment variable. No final rejection rate or confidence interval is calculated.

Clean text SHA-256: `5051bbddcd6cac2971f353bddaec9ed39b7ad1881d1cf216f899a77826763d3c`. The pre-comparison freeze tag is `clean-text-frozen`.

## 3a. The 39 sentences that failed on the old text

Of the 39 original sentence-stage failures, **18 now pass** and **21 still fail** against the frozen clean text.

Each remaining failure is listed below with the exact validator error and its highest-similarity clean-text passage. Similarity is `difflib.SequenceMatcher.ratio()` after whitespace collapse only; it is report-layer context, not a validation rule.

### Proposal 4 — `C0004`

**Original proposal text:**
> Furthermore, a standard error for each estimate is reported, which is derived from the posterior’s curvature at its maximum (see Methods for details).

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9122):**
> estimates are kept as final estimates of LFC. Furthermore, a standard error for each estimate is reported, which is derived from the posterior’s curvature at its maximum (see Materials and methods for details). These shrunken

### Proposal 11 — `C0003`

**Original proposal text:**
> DESeq2 flags, for each gene, those samples that have a Cook’s distance greater than the 0.99 quantile of the F(p, m −p) distribution, where p is the number of model parameters including the intercept, and m is the number of samples.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9745):**
> were removed and the model refit. DESeq2 flags, for each gene, those samples that have a Cook’s distance greater than the 0.99 quantile of the F(p,m−p) distribution, where p is the number of model parameters including the intercept, and m is the number of samples. The use of the F distribution is motivated

### Proposal 15 — `C0007`

**Original proposal text:**
> The rlog transformation is calculated by fitting for each gene a GLM with a baseline expression (i.e., intercept only) and, computing for each sample, shrunken LFCs with respect to the baseline, using the same empirical Bayes procedure as before (Methods).

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9688):**
> the raw counts, not transformed data. The rlog transformation is calculated by fitting for each gene a GLM with a baseline expression (i.e., intercept only) and, computing for each sample, shrunken LFCs with respect to the baseline, using the same empirical Bayes procedure as before (Materials and methods). Here, however, the sample

### Proposal 16 — `C0008`

**Original proposal text:**
> Both the rlog transformation and theVST are provided in theDESeq2 package.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9220):**
> ij /s j ). Both the rlog transformation and the VST are provided in the DESeq2 package. We demonstrate the use of the

### Proposal 22 — `C0006`

**Original proposal text:**
> The sensitivity was calculated as the fraction of genes with adjusted P value < 0.1 among the genes with true differences between group means.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9826):**
> assessed by their sensitivity and precision. The sensitivity was calculated as the fraction of genes with adjusted P value <0.1 among the genes with true differences between group means. The precision was calculated as the fraction

### Proposal 23 — `C0007`

**Original proposal text:**
> The precision was calculated as the fraction of genes with true differences between group means among those with adjusted P value < 0.1.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9818):**
> with true differences between group means. The precision was calculated as the fraction of genes with true differences between group means among those with adjusted P value <0.1. The sensitivity is plotted over 1−precision, or

### Proposal 24 — `C0008`

**Original proposal text:**
> We note that EBSeq version 1.4.0 by default removes low-count genes– whose 75% quantile of normalized counts is less than ten– before calling differential expression.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9693):**
> nominal value of 0.1. We note that EBSeq version 1.4.0 by default removes low-count genes – whose 75% quantile of normalized counts is less than ten – before calling differential expression. The sensitivity of algorithms on the

### Proposal 29 — `C0002`

**Original proposal text:**
> By default, the normalization constants sij are considered constant within a sample, sij = sj,andareestimated with the median-of-ratios method previously described and used in DESeq [4] and DEXSeq [30]:

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9000):**
> standard errors on the log2 scale. By default, the normalization constants s ij are considered constant within a sample, s ij =s j , and are estimated with the median-of-ratios method previously described and used in DESeq [4] and DEXSeq [30]:

### Proposal 32 — `C0005`

**Original proposal text:**
> We assume the dispersion parameter αi follows a lognormal prior distribution that is centered around a trend that depends on the gene's mean normalized read count: log αi ∼ N logαtr(¯μi), σ2 d .

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9443):**
> , defined below. Estimation of dispersions We assume the dispersion parameter α i follows a log-normal prior distribution that is centered around a trend that depends on the gene’s mean normalized read count: log α i ∼ N log α tr ( μ ̄ i )

### Proposal 33 — `C0006`

**Original proposal text:**
> For the trend function, we use the same parametrization as we used for DEXSeq [30], namely, αtr( ¯μ) = a1 ¯ μ +α0.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9182):**
> true dispersions scatter around the trend. For the trend function, we use the same parametrization as we used for DEXSeq [30], namely, α tr ( μ ̄ ) = a 1 μ ̄ + α

### Proposal 34 — `C0007`

**Original proposal text:**
> To get a gene-wise dispersion estimate for a gene i, we start by fitting a negative binomial GLM without an LFC prior for the design matrix X to the gene's count data.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9940):**
> three steps follow. Gene-wise dispersion estimates To get a gene-wise dispersion estimate for a gene i, we start by fitting a negative binomial GLM without an LFC prior for the design matrix X to the gene’s count data. This GLM uses a rough method-of-moments

### Proposal 39 — `C0003`

**Original proposal text:**
> Therefore, the prior variance σ2 d is obtained by subtracting the expected sampling variance from an estimate of the variance of the logarithmic residuals, s2 lr :
> σ2 d = max s2 lr −ψ1((m−p)/2), 0.25 .

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9191):**
> values of m, p and α. Therefore, the prior variance σ d 2 is obtained by subtracting the expected sampling variance from an estimate of the variance of the logarithmic residuals, s lr 2 : σ d 2 = max s lr 2 − ψ 1 ( (

### Proposal 40 — `C0004`

**Original proposal text:**
> To avoid inflation of σ2 d due to dispersion outliers (i.e., genes not well captured by this prior; see below), we use a robust estimator for the standard deviation slr of the logarithmic residuals,
> slr = mad
> log αgw
> −logαtr( ¯μi) ,
> where mad stands for the median absolute deviation, divided as usual by the scaling factor −1(3/4).

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.7858):**
> sampling variance. To avoid inflation of σ d 2 due to dispersion outliers (i.e., genes not well captured by this prior; see below), we use a robust estimator for the standard deviation s lr of the logarithmic residuals, s lr = mad i log α i gw − log α tr ( μ ̄ i ) , (8) where mad stands for the median absolute deviation, divided as usual by

### Proposal 41 — `C0005`

**Original proposal text:**
> When there are three or less residual degrees of freedom (number of samples minus number of parameters to estimate), the estimation of the prior variance σ2 d using the observed variance of logarithmic residuals s2 lr tends to underestimate σ2 d. In this case, we instead estimate the prior variance through simulation.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9404):**
> of freedom When there are three or less residual degrees of freedom (number of samples minus number of parameters to estimate), the estimation of the prior variance σ d 2 using the observed variance of logarithmic residuals s lr 2 tends to underestimate σ d 2 . In this case, we instead estimate the prior variance through simulation. We match the distribution of logarithmic

### Proposal 42 — `C0006`

**Original proposal text:**
> We repeat the simulation over a grid of values for σ2 d, and select the value that minimizes the Kullback–Leibler divergence from the observed density of logarithmic residuals to the simulated density.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9645):**
> the χ 2 distribution. We repeat the simulation over a grid of values for σ d 2 , and select the value that minimizes the Kullback–Leibler divergence from the observed density of logarithmic residuals to the simulated density. Final dispersion estimate We form a

### Proposal 43 — `C0007`

**Original proposal text:**
> Therefore, we use the heuristic of considering a gene as a dispersion outlier, if the residual from the trend fit is more than two standard deviations of logarithmic residuals, slr (see Equation (8)), above the fit, i.e., if
> log αgw i >logαtr(¯μi) + 2slr.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9493):**
> this might lead to false positives. Therefore, we use the heuristic of considering a gene as a dispersion outlier, if the residual from the trend fit is more than two standard deviations of logarithmic residuals, s lr (see Equation (8)), above the fit, i.e., if log α i gw > log α tr ( μ ̄

### Proposal 44 — `C0008`

**Original proposal text:**
> Instead of the MAP value , we use the gene-wise estimate αgw i as a final dispersion value in the subsequent steps.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.8664):**
> mean. Instead of the MAP value α i MAP , we use the gene-wise estimate α i gw as a final dispersion value in the subsequent steps. In addition, the iterative fitting procedure for

### Proposal 49 — `C0001`

**Original proposal text:**
> The Wald test compares the beta estimate βir divided by its estimated standard error SE(βir) to a standard normal distribution.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9300):**
> zero. Wald test The Wald test compares the beta estimate β ir divided by its estimated standard error SE(β ir ) to a standard normal distribution. The estimated standard errors are the

### Proposal 53 — `C0005`

**Original proposal text:**
> Two-tailed P values are generated by integrating a normal distribution centered on θ with standard deviation SE(βir) from |βir| toward ∞. The value of the integral is then multiplied by 2 and thresholded at 1.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9429):**
> = − θ . Two-tailed P values are generated by integrating a normal distribution centered on θ with standard deviation SE(β ir ) from |β ir | toward ∞. The value of the integral is then multiplied by 2 and thresholded at 1. This procedure controls type-I

### Proposal 54 — `C0006`

**Original proposal text:**
> Conversely, when searching for genes whose absolute LFC is significantly below a threshold, i.e., when testing the null hypothesis H0 : |βir| ≥ θ, the P value is constructed as the maximum of two one-sided tests of the simple null hypotheses: H0a : βir = θ and H0b : βir = −θ.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9179):**
> standard DESeq2 P value when θ=0. Conversely, when searching for genes whose absolute LFC is significantly below a threshold, i.e., when testing the null hypothesis ℋ 0 : | β ir | ≥ θ , the P value is constructed as the maximum of two one-sided tests of the simple null hypotheses: ℋ 0 a : β ir = θ and ℋ 0 b

### Proposal 55 — `C0007`

**Original proposal text:**
> The one-sided P values are generated by integrating a normal distribution centered on θ with standard deviation SE(βir) from βir toward −∞, and integrating a normal distribution centered on −θ with standard deviation SE(βir) from βir toward ∞.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest clean passage (similarity 0.9339):**
> : β ir = − θ . The one-sided P values are generated by integrating a normal distribution centered on θ with standard deviation SE(β ir ) from β ir toward −∞, and integrating a normal distribution centered on −θ with standard deviation SE(β ir ) from β ir toward

## 3b. The 24 sentences that passed on the old text

Of the 24 old-text sentence passes, **12 still pass** and **12 now fail** against the clean text.

For each newly failing case, the original proposal and the nearest old/clean passages are shown side by side in sequence. The validator error is unmodified.

### Proposal 9 — `C0001`

**Original proposal text:**
> DESeq2 offers tests for composite null hypotheses of the form |βir|≤θ,whereβir is the shrunken LFC from the estimation procedure described above.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> LFC is above the chosen threshold. DESeq2 offers tests for composite null hypotheses of the form |βir|≤θ,whereβir is the shrunken LFC from the estimation procedure described above. (See Methods for details.) Figure 4A

**Nearest clean-text passage (similarity 0.8636):**
> chosen threshold. DESeq2 offers tests for composite null hypotheses of the form |β ir |≤θ, where β ir is the shrunken LFC from the estimation procedure described above. (See Materials and methods for

### Proposal 12 — `C0004`

**Original proposal text:**
> However, if there are two or fewer replicates for a condition, these samplesdonotcontribute to outlier detection, as thereare insufficient replicates to determine outlier status.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> fit using all the samples [25]. However, if there are two or fewer replicates for a condition, these samplesdonotcontribute to outlier detection, as thereare insufficient replicates to determine outlier status. Howshould one deal with flagged outliers?

**Nearest clean-text passage (similarity 0.9231):**
> samples [25]. However, if there are two or fewer replicates for a condition, these samples do not contribute to outlier detection, as there are insufficient replicates to determine outlier status. How should one deal with flagged

### Proposal 13 — `C0005`

**Original proposal text:**
> By default, outliers in conditions withsix or fewer replicatescausethewholegenetobeflaggedandremoved from subsequent analysis, including P value adjustment for multiple testing.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> two possible responses to flagged outliers. By default, outliers in conditions withsix or fewer replicatescausethewholegenetobeflaggedandremoved from subsequent analysis, including P value adjustment for multiple testing. For conditions that contain seven or

**Nearest clean-text passage (similarity 0.7682):**
> in conditions with six or fewer replicates cause the whole gene to be flagged and removed from subsequent analysis, including P value adjustment for multiple testing. For conditions that contain seven

### Proposal 20 — `C0004`

**Original proposal text:**
> These datasets were of varying total sample size (m ∈ {6, 8, 10, 20}), and the samples were split into two equal sized groups; 80% of the simulated genes had no true differential expression, while for 20% of the genes, true fold changes of 2, 3 and 4 were used to generate counts across the two groups, with the direction of fold change chosen randomly.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> data, fitting only an intercept term. These datasets were of varying total sample size (m ∈ {6, 8, 10, 20}), and the samples were split into two equal sized groups; 80% of the simulated genes had no true differential expression, while for 20% of the genes, true fold changes of 2, 3 and 4 were used to generate counts across the two groups, with the direction of fold change chosen randomly. The simulated differentially expressed genes were

**Nearest clean-text passage (similarity 0.9417):**
> from the Pickrell et al. data, fitting only an intercept term. These datasets were of varying total sample size (m∈{6,8,10,20}), and the samples were split into two equal-sized groups; 80% of the simulated genes had no true differential expression, while for 20% of the genes, true fold changes of 2, 3 and 4 were used to generate counts across the two groups, with the direction of fold change chosen randomly. The simulated differentially expressed genes were chosen

### Proposal 36 — `C0009`

**Original proposal text:**
> We then maximize the Cox–Reid adjusted likelihood of the dispersion, conditioned on the fitted values ˆμ0 ij from the initial fit, to obtain the gene-wise estimate αgw i

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 0.9971):**
> set of fitted values, ˆμ0 ij .We then maximize the Cox–Reid adjusted likelihood of the dispersion, conditioned on the fitted values ˆμ0 ij from the initial fit, to obtain the gene-wise estimate αgw i αgw i with =argmax α ℓCR

**Nearest clean-text passage (similarity 0.9641):**
> values, μ ̂ ij 0 . We then maximize the Cox–Reid adjusted likelihood of the dispersion, conditioned on the fitted values μ ̂ ij 0 from the initial fit, to obtain the gene-wise estimate α i gw , i.e., α

### Proposal 38 — `C0002`

**Original proposal text:**
> The hyperparameters a1 and α0 of (6) are obtained by iteratively fitting a gamma-family GLM. At each iteration, genes with a ratio of dispersion to fitted value outside the range [10−4,15]are left out until thesumofsquared LFCs of the newcoefficients over the old coefficients is less than 10−6 (same approach as in DEXSeq [30]).

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> to exclude such outliers is used. The hyperparameters a1 and α0 of (6) are obtained by iteratively fitting a gamma-family GLM. At each iteration, genes with a ratio of dispersion to fitted value outside the range [10−4,15]are left out until thesumofsquared LFCs of the newcoefficients over the old coefficients is less than 10−6 (same approach as in DEXSeq [30]). The parametrization (6) is based on

**Nearest clean-text passage (similarity 0.8594):**
> hyperparameters a 1 and α 0 of (6) are obtained by iteratively fitting a gamma-family GLM. At each iteration, genes with a ratio of dispersion to fitted value outside the range [10−4,15] are left out until the sum of squared LFCs of the new coefficients over the old coefficients is less than 10−6 (same approach as in DEXSeq [30]). The parametrization (6) is based on

### Proposal 45 — `C0009`

**Original proposal text:**
> Tomakethefitrobustagainstoutlierswithveryhigh absoluteLFCvalues,weusequantilematching:thewidth σr ischosensuchthatthe(1−p)empiricalquantileofthe absolutevalueof theobservedLFCs, ⃗βMLE r ,matchesthe (1−p/2)theoreticalquantileoftheprior,N(0,σ2r ),where pissetbydefaultto0.05.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 0.9524):**
> for eachcolumnrofthedesignmatrix(exceptfortheinter cept),azero-centerednormaldistributiontotheempirical distributionofMLEfoldchangeestimates ⃗βMLE r . Tomakethefitrobustagainstoutlierswithveryhigh absoluteLFCvalues,weusequantilematching:thewidth σr ischosensuchthatthe(1−p)empiricalquantileofthe absolutevalueof theobservedLFCs, ⃗βMLE r ,matchesthe (1−p/2)theoreticalquantileoftheprior,N(0,σ2r ),where pissetbydefaultto0.05.Ifwewritethetheoreticalupper quantileofanormaldistributionasQN(1−p)andthe empiricalupperquantileoftheMLELFCsasQ|βr|(1−p), thenthepriorwidthiscalculatedas: σr= Q|βr|(1−p)

**Nearest clean-text passage (similarity 0.3875):**
> . To make the fit robust against outliers with very high absolute LFC values, we use quantile matching: the width σ r is chosen

### Proposal 46 — `C0010`

**Original proposal text:**
> Toensurethatthepriorwidthσrwillbeindependentof thechoiceofbaselevel, theestimatesfromthequantile matchingprocedureareaveragedforeachfactoroverall possiblecontrastsoffactorlevels.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 0.9519):**
> empiricalupperquantileoftheMLELFCsasQ|βr|(1−p), thenthepriorwidthiscalculatedas: σr= Q|βr|(1−p) QN(1−p/2) . Toensurethatthepriorwidthσrwillbeindependentof thechoiceofbaselevel, theestimatesfromthequantile matchingprocedureareaveragedforeachfactoroverall possiblecontrastsoffactorlevels.Whendeterminingthe empiricalupperquantile,extremeLFCvalues(βMLE ir > log(2)10,or10onthebase2scale)areexcluded. Finalestimateof logarithmicfoldchangesThe

**Nearest clean-text passage (similarity 0.3394):**
> base level, the estimates from the quantile matching procedure are averaged for each factor over all possible

### Proposal 47 — `C0011`

**Original proposal text:**
> Whendeterminingthe empiricalupperquantile,extremeLFCvalues(βMLE ir > log(2)10,or10onthebase2scale)areexcluded.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 0.8730):**
> QN(1−p/2) . Toensurethatthepriorwidthσrwillbeindependentof thechoiceofbaselevel, theestimatesfromthequantile matchingprocedureareaveragedforeachfactoroverall possiblecontrastsoffactorlevels.Whendeterminingthe empiricalupperquantile,extremeLFCvalues(βMLE ir > log(2)10,or10onthebase2scale)areexcluded. Finalestimateof logarithmicfoldchangesThe loga rithmicposteriorforthevector, ⃗βi,ofmodelcoefficients βirforgeneiisthesumofthelogarithmiclikelihoodofthe

**Nearest clean-text passage (similarity 0.5033):**
> possible contrasts of factor levels. When determining the empirical upper quantile, extreme LFC values ( β ir

### Proposal 48 — `C0012`

**Original proposal text:**
> Theterm (β), i.e.,thelogarithmofthedensityofthe normal prior (uptoanadditiveconstant), canbe read asaridgepenalty term, andtherefore,weperformthe optimizationusingtheiterativelyreweightedridgeregres sionalgorithm[56],alsoknownasweightedupdates[57].

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> i.e.,αi= αMAP i ,exceptfordispersionoutliers,whereαi=αgw i . Theterm (β), i.e.,thelogarithmofthedensityofthe normal prior (uptoanadditiveconstant), canbe read asaridgepenalty term, andtherefore,weperformthe optimizationusingtheiterativelyreweightedridgeregres sionalgorithm[56],alsoknownasweightedupdates[57]. Specifically,theupdatesforagivengeneareoftheform ⃗β←XtWX+⃗ λI −1 XtW⃗z, withλr=1/σ2r

**Nearest clean-text passage (similarity 0.5284):**
> as a ridge penalty term, and therefore, we perform the optimization using the iteratively reweighted ridge regression algorithm [56], also known as weighted updates [57].

### Proposal 57 — `C0009`

**Original proposal text:**
> First, when any interaction terms are included in the design, the LFC prior width for main effect terms is not estimated from the data, but set to a wide value (σ2r = (log(2))2 1000, or 1000 on the base 2 scale).

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> for experimental designs with interaction terms. First, when any interaction terms are included in the design, the LFC prior width for main effect terms is not estimated from the data, but set to a wide value (σ2r = (log(2))2 1000, or 1000 on the base 2 scale). This ensures that shrinkage of main

**Nearest clean-text passage (similarity 0.8861):**
> for experimental designs with interaction terms. First, when any interaction terms are included in the design, the LFC prior width for main effect terms is not estimated from the data, but set to a wide value ( σ r 2 = ( log ( 2 ) ) 2 1000 , or 1000 on

### Proposal 61 — `C0013`

**Original proposal text:**
> The MLE of ⃗βi is used for calculating Cook’s distance.

**Raw validator error:** `verbatim_sentence is not an exact substring after whitespace normalization`

**Nearest old-text passage (similarity 1.0000):**
> the LFC matrix. Cook’s distancefor outlierdetection The MLE of ⃗βi is used for calculating Cook’s distance. Considering a gene i and sample

**Nearest clean-text passage (similarity 0.8846):**
> distance for outlier detection The MLE of β → i is used for calculating Cook’s distance. Considering a gene i and sample

## 3c. Original Tier-A pilot positives

The 24 original positive cases were selected unchanged from frozen `benchmark/cases.jsonl` using `tier == "A"` and `expected_valid == true`. **6 pass** and **18 fail** sentence validation against the clean text.

- **row-2-A0** (source `row-2`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > To get a gene-wise dis persion estimate for a gene i, we start by fitting a nega tive binomial GLM without an LFC prior for the design matrix X to the gene’s count data.
- **row-4-A0** (source `row-4`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > To incorporate empirical Bayes shrinkage of LFCs, we postulate a zero-centered normal prior for the coefficients βir of model (2) that represent LFCs (i.
- **row-6-A0** (source `row-6`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > Theestimate of theLFCpriorwidthiscalculatedas follows.
- **row-10-A0** (source `row-10`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > finalMAPcoefficientestimates: ⃗βi=argmax ⃗β ⎛ ⎝ j logfNB Kij;μj(⃗β),αi + (⃗β) ⎞ ⎠, where μj(⃗β)=sije rxjrβr, (⃗β)= r −β2r 2σ2 r , andαi isthefinaldispersionestimateforgenei, i.
- **row-16-A0** (source `row-16`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
- **row-18-A0** (source `row-18`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
- **row-20-A0** (source `row-20`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > theobservedFisherinformation, orpeakednessofthelogarithmoftheprofilelikelihood,is influencedbyanumberof factors includingthedegrees offreedom,theestimatedmeancountsμij,andthegene’s dispersionestimateαi.
- **row-21-A0** (source `row-21`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > By default, the normalization constants sij are consid ered constant within a sample, sij = sj,andareestimated with the median-of-ratios method previously described and used in DESeq [4] and DEXSeq [30]: ⎛ ⎞ where ⃗c represents a numeric contrast, e.
- **row-25-A0** (source `row-25`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > We first use the count data for each gene separately to get preliminary gene-wise dispersion estimates αgw i by maximum-likelihood estimation.
- **row-27-A0** (source `row-27`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > A parametric curve of the form (6) is fit by regressing the gene-wise dispersion estimates αgw i onto the means of the normalized counts, ¯μi.
- **row-29-A0** (source `row-29`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > The prior variance σ2 d is thresholded at a minimal value of 0.
- **row-33-A0** (source `row-33`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > Instead of the MAP value , we use the gene-wise estimate αgw i i i where mad stands for the median absolute deviation, divided as usual by the scaling factor −1(3/4).
- **row-35-A0** (source `row-35`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > We use an empiri cal Bayes approach (Methods), which lets the strength of shrinkage depend (i) on an estimate of how close true dis persion values tend to be to the fit and (ii) on the degrees of freedom: as the sample size increases, the shrinkage decreases in strength, and eventually becomes negligi ble.
- **row-39-A0** (source `row-39`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > To avoid inflation of σ2 d due to dispersion outliers (i.
- **row-41-A0** (source `row-41`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > For some genes, the gene-wise esti mate αgw i canbesofarabovethepriorexpectationαtr(¯μi) that it would be unreasonable to assume that the prior is suitable for the gene.
- **row-43-A0** (source `row-43`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > Therefore, we use the heuris tic of considering a gene as a dispersion outlier, if the residual from the trend fit is more than two standard deviations of logarithmic residuals, slr (see Equation (8)), above the fit, i.
- **row-49-A0** (source `row-49`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > The sampling distribution of a dispersion estimator is approx imately a scaled χ2 distribution with m − p degrees of freedom, withm thenumber ofsamplesandpthenumber of coefficients.
- **row-51-A0** (source `row-51`): verbatim_sentence is not an exact substring after whitespace normalization
  - Original pilot sentence:
    > Furthermore, as the degrees of freedom increase, and the experiment pro vides more information for LFC estimation, the shrunken estimates will converge to the unshrunken estimates.

## 3d. Unchanged deterministic extractor on clean text

Report-only flags use the existing definitions: `short_sentence` means fewer than 5 whitespace-delimited tokens; `reference_like` uses the existing report-only citation/reference heuristic. Neither flag changes acceptance.

| Text/input | Total proposals | Accepted by no-API path | Rejected by no-API path | `short_sentence` | `reference_like` | Both flags |
|---|---:|---:|---:|---:|---:|---:|
| Clean publisher text (this run) | 549 | 549 | 0 | 178 | 161 | 93 |
| Old-text baseline (saved, unchanged) | 319 | not recomputed here | not recomputed here | 193 | 114 | not available in the specified baseline |

## 3e. All 63 saved Gemini proposals

| Paper text | Total saved proposals | Pass `validate_claims()` | Fail `validate_claims()` |
|---|---:|---:|---:|
| Old `examples/deseq2/DESeq.txt` | 63 | 24 | 39 |
| Clean `paper_clean.txt` | 63 | 30 | 33 |

These are raw counts for the available 63 proposals only. They are not complete-run estimates; chunks 1, 8, and 9 and the second run remain unavailable.

# DESeq2 spot checks

These are instructions for independent human checking. None of these rows is manually verified by the user yet.

## Spot check 1: row 30 — Behaviour for very low-count genes
Verdict label: **not verified** (draft; human review pending)
Paper sentence: For genes with very low read count, even an estimate of zero LFC is not significant, as the large uncertainty of the estimate does not allow us to exclude that the gene may in truth be more than weakly affected by the experimental condition.
Code: [src/DESeq2.cpp:337-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L337-L339)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.

## Spot check 2: row 12 — Uncertainty
Verdict label: **partial** (draft; human review pending)
Paper sentence: DESeq2 reports the standard error for each shrunken LFC estimate, obtained from the curvature of the coefficient’s posterior (dashed lines in Figure 2D) at its maximum.
Code: [src/DESeq2.cpp:451-453](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L451-L453)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.

## Spot check 3: row 16 — Observed Fisher information calculation
Verdict label: **partial** (draft; human review pending)
Paper sentence: Theeffectofthezero-centerednor malpriorcanbeunderstoodasshrinkingtheMAPLFC estimatesbasedontheamountofinformationtheexperi mentprovidesforthiscoefficient,andwebrieflyelaborate onthishere.
Code: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.

## Spot check 4: row 18 — Relationship between Fisher information and shrinkage
Verdict label: **partial** (draft; human review pending)
Paper sentence: The strength of shrinkage does not depend simply on the mean count, but rather on the amount of informa tion available for the fold change estimation (as indicated by the observed Fisher information; see Methods).
Code: [src/DESeq2.cpp:336-339](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/src/DESeq2.cpp#L336-L339)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.

## Spot check 5: row 2 — Initial estimation
Verdict label: **consistent** (draft; human review pending)
Paper sentence: To get a gene-wise dis persion estimate for a gene i, we start by fitting a nega tive binomial GLM without an LFC prior for the design matrix X to the gene’s count data.
Code: [R/fitNbinomGLMs.R:253-255](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L253-L255)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.

## Spot check 6: row 4 — Prior
Verdict label: **consistent** (draft; human review pending)
Paper sentence: To incorporate empirical Bayes shrinkage of LFCs, we postulate a zero-centered normal prior for the coefficients βir of model (2) that represent LFCs (i.
Code: [R/fitNbinomGLMs.R:367-370](https://github.com/thelovelab/DESeq2/blob/76c5f8523716804dbe0a9500b4b7e216c6af225c/R/fitNbinomGLMs.R#L367-L370)
Instruction: Open the permalink, read the cited lines, and decide whether the quoted code supports the paper sentence; record your decision and notes in the Final Table.


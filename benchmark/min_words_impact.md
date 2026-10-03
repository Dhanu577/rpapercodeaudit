# Impact of MIN_WORDS = 5 on saved deterministic proposals

This is a static impact calculation over the saved `benchmark/natural_proposals_deterministic.json` output (319 proposals). It applies the spec rule exactly: collapse whitespace with the existing `\s+` normalizer, strip, then count whitespace-delimited tokens. It does not call a validator, run tests, alter proposal labels, or regenerate model output.

**Would be rejected under MIN_WORDS = 5: 193 of 319.** The rule must not be lowered to preserve these proposals. Per the task gate, this impact requires stopping the v3 validation and regression runs after the frozen commit and the post-freeze checks.

| Proposal ID | Normalized token count | Saved verbatim sentence |
|---|---:|---|
| `H0002` | 2 | experiment [1]. |
| `H0007` | 4 | genes with low counts. |
| `H0009` | 2 | method [4]. |
| `H0014` | 3 | (GLM)[12] as follows. |
| `H0017` | 2 | studies [15]. |
| `H0018` | 1 | gene. |
| `H0019` | 1 | genes. |
| `H0028` | 2 | dispersion-mean dependence. |
| `H0032` | 3 | the final estimate. |
| `H0034` | 1 | fit. |
| `H0036` | 4 | final estimate of dispersion. |
| `H0037` | 1 | count. |
| `H0038` | 1 | [16]. |
| `H0039` | 2 | expressed genes. |
| `H0041` | 2 | [16] dataset. |
| `H0047` | 3 | over all genes. |
| `H0051` | 2 | Hochberg [21]. |
| `H0055` | 1 | 1. |
| `H0059` | 4 | a user-specified target FDR. |
| `H0061` | 2 | most genes. |
| `H0062` | 3 | ered biologically significant. |
| `H0063` | 4 | threshold, \|βir\| ≤ θ. |
| `H0064` | 1 | threshold. |
| `H0065` | 2 | data [19]. |
| `H0067` | 3 | for a gene. |
| `H0069` | 3 | adjusted P values. |
| `H0070` | 2 | , adjusted. |
| `H0072` | 4 | gene from downstream analysis. |
| `H0074` | 2 | [16] dataset. |
| `H0078` | 2 | mean counts. |
| `H0081` | 4 | ReCount online resource [27]. |
| `H0082` | 2 | [16] dataset. |
| `H0086` | 4 | assigned to a gene. |
| `H0087` | 4 | nate from each gene. |
| `H0088` | 2 | cases [28]. |
| `H0093` | 2 | procedure [21]. |
| `H0096` | 1 | 1. |
| `H0099` | 1 | [34]. |
| `H0106` | 4 | file 1: Figures S12–S16. |
| `H0108` | 3 | of normalized counts). |
| `H0109` | 2 | expression [39]. |
| `H0110` | 4 | differentially expressed genes exist. |
| `H0116` | 3 | 01)under thenull hypothesis. |
| `H0117` | 3 | 01 (black line). |
| `H0118` | 4 | 4 for all algorithms. |
| `H0119` | 4 | adjusted P value threshold. |
| `H0123` | 1 | 1). |
| `H0129` | 3 | library assays [46]. |
| `H0131` | 1 | gene. |
| `H0132` | 4 | as final dispersion estimates. |
| `H0134` | 2 | adjustment [47]. |
| `H0135` | 1 | 6). |
| `H0136` | 3 | 1/μj +α . |
| `H0142` | 1 | dispersion. |
| `H0145` | 2 | 25 . |
| `H0146` | 3 | of prior (5). |
| `H0147` | 4 | suitable for the gene. |
| `H0149` | 2 | QN(1−p/2) . |
| `H0150` | 1 | log(2)10,or10onthebase2scale)areexcluded. |
| `H0151` | 1 | sionalgorithm[56],alsoknownasweightedupdates[57]. |
| `H0155` | 3 | without dispersion shrinkage. |
| `H0156` | 4 | tion often zero counts. |
| `H0159` | 4 | exceeds a threshold θ>0. |
| `H0161` | 2 | θ =0. |
| `H0164` | 2 | H =W1/2X(XtWX)−1XtW1/2. |
| `H0165` | 2 | ,0 . |
| `H0166` | 3 | Bioconductor project [11]. |
| `H0169` | 4 | and gene annotation versions. |
| `H0170` | 2 | Count [64]. |
| `H0181` | 1 | 1. |
| `H0182` | 1 | 2. |
| `H0183` | 1 | 3. |
| `H0184` | 1 | 4. |
| `H0185` | 1 | 5. |
| `H0186` | 1 | 6. |
| `H0187` | 1 | 12:31–46. |
| `H0188` | 3 | Bioinformatics 2007, 23:2881–2887. |
| `H0189` | 4 | Nucleic AcidsRes 2012, 40:4288–4297. |
| `H0190` | 3 | GenomeBiol 2010, 11:106. |
| `H0191` | 1 | 27:2672–2678. |
| `H0192` | 3 | Biostatistics 2013, 14:232–243. |
| `H0193` | 1 | 7. |
| `H0194` | 1 | 8. |
| `H0195` | 1 | 9. |
| `H0197` | 3 | Bioinformatics 2010, 11:422. |
| `H0198` | 3 | Biostatistics 2013, 14:113–128. |
| `H0199` | 3 | 31,500-element cDNA array. |
| `H0200` | 3 | GenomeRes 2001, 11:1861–1870. |
| `H0201` | 1 | 10. |
| `H0202` | 1 | 11. |
| `H0203` | 4 | Genome Biol 2004, 5:R80. |
| `H0204` | 1 | 12. |
| `H0205` | 2 | Hall/CRC; 1989. |
| `H0206` | 1 | 13. |
| `H0207` | 2 | 2012, 13:204–216. |
| `H0208` | 1 | 14. |
| `H0209` | 3 | BMCBioinformatics 2011, 12:480. |
| `H0210` | 1 | 15. |
| `H0211` | 3 | Biol 2004, 3:1–25. |
| `H0212` | 1 | 16. |
| `H0213` | 3 | PLoSONE 2011, 6:17820. |
| `H0214` | 1 | 17. |
| `H0215` | 3 | Nature 2010, 464:768–772. |
| `H0216` | 1 | 18. |
| `H0217` | 2 | Springer; 2009. |
| `H0218` | 1 | 19. |
| `H0219` | 3 | Bioinformatics 2013, 14:262. |
| `H0220` | 1 | 20. |
| `H0221` | 3 | Bioinformatics 2012, 28:2782–2788. |
| `H0222` | 1 | 21. |
| `H0223` | 3 | Methodol 1995, 57:289–300. |
| `H0224` | 1 | 22. |
| `H0225` | 3 | USA 2010, 107:9546–9551. |
| `H0226` | 1 | 23. |
| `H0227` | 3 | Bioinformatics 2009, 25:765–771. |
| `H0228` | 1 | 24. |
| `H0230` | 1 | 25. |
| `H0231` | 3 | Technometrics 1977, 19:15–18. |
| `H0232` | 1 | 26. |
| `H0233` | 3 | GenomeRes 2010, 20:847–860. |
| `H0234` | 1 | 27. |
| `H0236` | 2 | 2011, 12:449. |
| `H0237` | 1 | 28. |
| `H0238` | 3 | NatBiotechnol 2012, 31:46–53. |
| `H0239` | 1 | 29. |
| `H0240` | 3 | Bioinformatics 2012, 28:1721–1728. |
| `H0241` | 1 | 30. |
| `H0242` | 3 | GenomeRes 2012, 22:2008–2017. |
| `H0243` | 1 | 31. |
| `H0244` | 2 | JComputBiol2009, 16:1117–1140. |
| `H0245` | 1 | 32. |
| `H0246` | 1 | 2013. |
| `H0247` | 1 | 33. |
| `H0249` | 3 | Bioinformatics 2009, 26:139–140. |
| `H0250` | 1 | 34. |
| `H0252` | 1 | 35. |
| `H0253` | 3 | Bioinformatics 2013, 29:1035–1043. |
| `H0254` | 1 | 36. |
| `H0256` | 2 | 2014, 15:29. |
| `H0257` | 1 | 37. |
| `H0258` | 3 | JClassif 1985, 2:193–218. |
| `H0259` | 1 | 38. |
| `H0260` | 3 | AnnApplStat 2011, 5:2493–2518. |
| `H0261` | 1 | 39. |
| `H0262` | 3 | Bioinformatics 2006, 22:789–794. |
| `H0263` | 1 | 40. |
| `H0264` | 3 | Nature 2014, 510:278–282. |
| `H0265` | 1 | 41. |
| `H0266` | 1 | 2013. |
| `H0267` | 1 | 42. |
| `H0268` | 3 | Nature 2012, 481:389–393. |
| `H0269` | 1 | 43. |
| `H0270` | 4 | G3 (Bethesda) 2013, 4:11–18. |
| `H0271` | 1 | 44. |
| `H0272` | 3 | PLoSComputBiol 2014, 10:1003531. |
| `H0273` | 1 | 45. |
| `H0274` | 1 | 42:3623–3637. |
| `H0275` | 1 | 46. |
| `H0276` | 3 | Nature 2014, 509:487–491. |
| `H0277` | 1 | 47. |
| `H0279` | 1 | 48. |
| `H0281` | 2 | 2007, 9:321–332. |
| `H0282` | 1 | 49. |
| `H0284` | 1 | 50. |
| `H0285` | 4 | PacJ Math 1966, 16:1–3. |
| `H0286` | 1 | 51. |
| `H0289` | 1 | 52. |
| `H0291` | 1 | 53. |
| `H0292` | 2 | 2001, 8:37–52. |
| `H0293` | 1 | 54. |
| `H0294` | 1 | 18:96–104. |
| `H0295` | 1 | 55. |
| `H0297` | 2 | 2002, 18:105–110. |
| `H0298` | 1 | 56. |
| `H0300` | 1 | 57. |
| `H0301` | 3 | JStatSoftw 2010, 33:1–22. |
| `H0302` | 1 | 58. |
| `H0303` | 3 | BMCBioinformatics 2011, 12:372. |
| `H0304` | 1 | 59. |
| `H0306` | 1 | 60. |
| `H0307` | 3 | PLoSComputBiol 2013, 9:1003118. |
| `H0308` | 1 | 61. |
| `H0309` | 1 | 2013. |
| `H0310` | 1 | 62. |
| `H0311` | 3 | Bioinformatics 2015, 31:166. |
| `H0312` | 1 | 63. |
| `H0313` | 2 | 2012, 28:2532–2533. |
| `H0314` | 1 | 64. |
| `H0315` | 3 | Bioinformatics 2014, 30:923–930. |
| `H0316` | 1 | 65. |
| `H0317` | 4 | deletions and gene fusions. |
| `H0318` | 3 | GenomeBiol 2013, 14:36. |
| `H0319` | 1 | 66. |

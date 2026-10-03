# V3.1 sentence-case relabeling

This relabeling was made after the `min_words_impact.md` review and before any v3 case was run under the revised specification. The five-word acceptance threshold proved unreliable for PDF-derived text: source extraction can merge or split words, while reference-list entries, bare numbers, and sentence fragments can be exact text. The validator therefore has no word-count rejection rule; token-count and reference-like properties are report-only.

| Mutation type | V3.1 class | Treatment |
|---|---|---|
| `S_empty_or_whitespace` | `must_reject` | Empty after whitespace normalization remains invalid. |
| `S_one_word_substring` | `boundary` | Record the observed decision; do not score it as a required acceptance or rejection. |
| `S_four_word_sentence` | `boundary` | Record the observed decision; do not score it as a required acceptance or rejection. |
| `S_exactly_five_words` | `must_accept` | A non-empty exact substring is accepted; five tokens are not a special threshold. |

No other labels are changed by this revision. The v1/v2 cases and results remain untouched. The prior `benchmark-cases-v3-frozen` tag is preserved; the regenerated inputs are frozen separately at `benchmark-cases-v3.1-frozen`.

# V3.1 bugs found — pending frozen run

The v3.1 case set has not been executed. No v3.1 must-class failure is claimed at this point. After the annotated `benchmark-cases-v3.1-frozen` tag is pushed and the runner completes, this file will list every `must_accept` rejection and every `must_reject` acceptance with its case input and raw validator log. Boundary cases will remain excluded and reported separately.

The earlier `row-6-A0` pilot rejection was caused by the superseded five-word rule. Under the revised exact-substring/empty-only rule, the 24-record pilot preflight accepted 24/24; see `preflight_v3_1.md`.

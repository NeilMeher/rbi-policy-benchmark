# RBI Policy Statement Benchmark

Can a learned sentence ranker recover rate decisions and trace them to their source? A percentage from another policy instrument can read as plausible unless the system locates the right evidence.

The dataset contains 31 dated Indian MPC decisions. Each row records the policy repo rate in integer basis points, its signed change, the action label, an author-written rationale and digest, a source URL, and a source locator. `protocol.md` records the split and labeling rules. To check the data, open the linked RBI release or publication, locate the policy decision, compare its repo rate against the preceding decision, and check the outlook or rationale separately. Underlying reports are linked and the repo redistributes only factual fields and original paraphrases.

## Results

| System | Action | Exact rate and change | Evidence sentence |
|---|---:|---:|---:|
| Keyword rules | 12/12 | 12/12 | 12/12 |
| Naive Bayes | 12/12 | 12/12 | 12/12 |

The test starts on 5 April 2024 and has eight holds and four cuts. No test meeting raises the rate. Both rankers find the correct sentence on this small, manually condensed dataset. The test cannot establish parity on full statements or on rate increases. The 6 June 2025 example shows why the policy repo decision must be separated from the concurrent cash reserve ratio change.

## Run locally

With Python 3.11 or later, run `python -m unittest -v`, then `python benchmark.py --pilot --output pilot-results.json`, `python benchmark.py --output results.json`, and `python demo.py`. Open `index.html` and select 2025-06-06. There are no third-party dependencies or keys.

The central choice is to rank evidence first, then extract the rate from the selected sentence. Both systems receive the previously published repo rate. Explain why that input is available in deployment, how a mixed-instrument sentence can cause an abstention, and how you would create a holdout with policy raises.

Neil Meher specified the project and its evaluation requirements. Codex built the benchmark, checked RBI sources and drafted the labels. An independent manual label review by Neil is pending.

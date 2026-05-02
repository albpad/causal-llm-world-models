# Benchmark Method Review Pass 1

Scope: review of the actual benchmark used in the analysis, focusing on how KG1 is instantiated in code and where the analysis depends on template logic rather than an extracted graph.

## Findings

### 1. The benchmark is template-authored, not graph-loaded

The code path used to generate the benchmark does not build the battery from a `kg1_data.json` graph. Instead, it hard-codes 12 baseline templates and all perturbations in `build_all_templates()` and only uses `kg1_data.json` for optional coverage validation in `main()`.

Evidence:
- [`src/causal_llm_eval/vignette_generator.py:3`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L3) to [`src/causal_llm_eval/vignette_generator.py:10`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L10) say the generator "reads KG1 from kg1_data.json".
- [`src/causal_llm_eval/vignette_generator.py:114`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L114) defines `build_all_templates()` with the full authored benchmark.
- [`src/causal_llm_eval/vignette_generator.py:1230`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L1230) to [`src/causal_llm_eval/vignette_generator.py:1268`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L1268) serialise those templates directly into the battery.
- [`src/causal_llm_eval/vignette_generator.py:1381`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L1381) to [`src/causal_llm_eval/vignette_generator.py:1412`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L1412) show `kg1_data.json` is only used to validate edge coverage.

Implication:
- The analysis is reproducible from the released benchmark.
- It is not accurate to describe the released benchmark as graph-derived at runtime.

### 2. Template gold labels override the global rule engine

The rule engine in `causal_templates.py` is not the primary source of truth for treatment stances. `determine_stance()` first checks the template-authored `expected_recommendations` and `expected_excluded`, and only then falls back to treatment-level blocker logic.

Evidence:
- [`src/causal_llm_eval/causal_templates.py:361`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L361) to [`src/causal_llm_eval/causal_templates.py:416`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L416)

Implication:
- The benchmark evaluates a locked set of authored treatment consequences.
- The global rule layer is secondary and mainly supports reasoning generation and fallback stance assignment.

### 3. Some treatment rule objects are intentionally sparse, so behavior is mostly template-driven

For some treatments, the standalone rule object is minimal and does not encode the full practical eligibility logic that the benchmark enforces.

Examples:
- [`src/causal_llm_eval/causal_templates.py:117`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L117) to [`src/causal_llm_eval/causal_templates.py:130`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L130): `ophl_type_iib` only has `baseline_laryngeal_function = dysfunctional` as an explicit hard blocker.
- [`src/causal_llm_eval/causal_templates.py:132`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L132) to [`src/causal_llm_eval/causal_templates.py:145`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L145): `ophl_type_iii` is similarly sparse.
- [`src/causal_llm_eval/causal_templates.py:287`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L287) to [`src/causal_llm_eval/causal_templates.py:310`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L310): `cetuximab_concurrent` and `carboplatin_5fu` are represented mainly as metadata flags (`indications_when_cisplatin_blocked`) rather than explicit blocker trees.

Implication:
- The benchmark’s real behavior for these treatments comes mostly from family restriction and perturbation-level expected labels, not from a rich graph-like rule object.

### 4. Low-consensus and grey-zone statements are in the scored benchmark

The released battery intentionally includes statements with table-level consensus below 80%, but treats them as explicit scored probes rather than separate exploratory items.

Evidence:
- [`src/causal_llm_eval/vignette_generator.py:662`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L662) to [`src/causal_llm_eval/vignette_generator.py:664`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L664): `S47R` is encoded as a grey-zone perturbation.
- [`src/causal_llm_eval/vignette_generator.py:769`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L769) to [`src/causal_llm_eval/vignette_generator.py:780`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L780): `S70` is encoded as a grey-zone perturbation.
- [`src/causal_llm_eval/vignette_generator.py:848`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L848) to [`src/causal_llm_eval/vignette_generator.py:863`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/vignette_generator.py#L863): `SA6` is encoded as a grey-zone perturbation.

Implication:
- This is defensible if the benchmark is explicitly framed as including contested decision regions.
- It should not be described as if every scored edge is a uniformly high-consensus gold-standard rule.

### 5. The analysis question space is manually bounded by family treatment lists

The treatments that can be evaluated for a given family are manually fixed in `FAMILY_TREATMENTS`.

Evidence:
- [`src/causal_llm_eval/causal_templates.py:476`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L476) to [`src/causal_llm_eval/causal_templates.py:495`](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/src/causal_llm_eval/causal_templates.py#L495)

Examples:
- `post_ict_response` only evaluates `rt_alone`, `concurrent_crt`, and `total_laryngectomy`.
- `pretreatment_function` only evaluates non-surgical LP versus TL.
- `cisplatin_eligibility` includes `rt_accelerated` as the fallback radiotherapy route.

Implication:
- The benchmark does not ask the full treatment space in each case.
- It evaluates a curated decision frontier, which is methodologically reasonable but narrower than a full KG execution claim.

## Overall evaluation

The benchmark used for analysis is coherent and strongly curated, but it is best described as a locked, statement-traceable perturbation battery rather than as a graph-executed rule system.

That distinction matters because:
- provenance comes from statement IDs,
- treatment consequences come primarily from template-authored gold labels,
- and the global rule layer mainly supports explanation and fallback behavior.

## Recommended next review slice

Review family-by-family fidelity:
- compare each family’s perturbations to the underlying statement language,
- identify where expected labels are broader or narrower than the cited statement,
- and separate high-consensus directional edges from grey-zone uncertainty probes.

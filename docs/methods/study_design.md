# KG₁ Counterfactual Sensitivity Analysis — Study Design & Execution Guide

## 1. Study Overview

**Objective**: Recover the implicit causal graph (KG₂) encoded in 7 LLMs' clinical reasoning about laryngeal and hypopharyngeal cancer treatment, and compare it to the expert consensus graph (KG₁) derived from Ferrari et al.'s 137 Delphi statements (Lancet Oncol 2025; 26: e264-81).

**Core innovation**: This is *behavioural causal discovery on the LLM itself* — treating each model as a black-box system whose input-output function implicitly encodes a causal graph, and recovering that graph through structured clinical interventions (counterfactual vignettes).

## 2. Study Design

### 2.1 Scale

| Parameter | Value |
|-----------|-------|
| Vignette battery | 88 items (12 baselines + 64 perturbations + 12 null controls) |
| Models | 7 (see §3) |
| Runs per item per model | 30 |
| Temperature | 0.6 |
| Phases per query | 2 (open-ended + targeted) |
| Total API calls | 36,960 |
| KG₁ edges tested | 57 / 58 |
| Clinical families | 10 |

### 2.2 Vignette Families

| Family | Baselines | Perturbations | Key edges tested |
|--------|-----------|---------------|------------------|
| Glottic cT2 | 2 | 12 | TLM exposure, AC involvement, RT fractionation |
| Glottic cT3 | 2 | 12 | TC erosion conditionality, paraglottic space, arytenoid |
| Supraglottic cT3 | 1 | 7 | Pre-epiglottic space, vallecular extension |
| Hypopharyngeal | 1 | 6 | Pyriform apex, postcricoid, CRT eligibility |
| cT4a unselected | 1 | 5 | Extralaryngeal extension, TL necessity |
| cT4a selected | 1 | 6 | Magic plane preservation, OPHL viability |
| Cisplatin eligibility | 1 | 7 | Renal/cardiac/neuro CIs, cetuximab alternatives |
| Post-ICT response | 1 | 7 | CR vs PR thresholds, salvage TL triggers |
| Elderly/frail | 1 | 6 | ECOG, age, CGA, frailty vs chronological age |
| Pretreatment function | 1 | 8 | Aspiration, tracheostomy, baseline laryngeal function |

### 2.3 Perturbation Types

- **flip** (n=52): Single clinical variable changed → expected to change at least one treatment stance
- **null** (n=12): Rephrased vignette, clinically identical → expected NO change (noise floor)
- **grey_zone** (n=12): Perturbation targeting one of 3 Delphi statements with <80% consensus

## 3. Model Selection

All models served via Together.ai (api.together.xyz). $800 budget.

| Short name | API model string | Tier | $/M in | $/M out | Est. cost |
|------------|------------------|------|--------|---------|-----------|
| llama-3.1-8b | meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo | scaling | $0.18 | $0.18 | $1.62 |
| qwen3-235b-instruct | Qwen/Qwen3-235B-A22B-Instruct-2507-tput | general_large | $0.20 | $0.60 | $3.27 |
| llama-4-maverick | meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 | general_large | $0.27 | $0.85 | $4.57 |
| llama-3.3-70b | meta-llama/Llama-3.3-70B-Instruct-Turbo | scaling | $0.88 | $0.88 | $7.90 |
| deepseek-v3.1 | deepseek-ai/DeepSeek-V3.1 | general_large | $0.60 | $1.70 | $9.45 |
| qwen3-235b-thinking | Qwen/Qwen3-235B-A22B-Thinking-2507 | reasoning | $0.65 | $3.00 | $31.15 |
| deepseek-r1 | deepseek-ai/DeepSeek-R1 | reasoning | $3.00 | $7.00 | $106.39 |
| **TOTAL** | | | | | **~$164** |

### 3.1 Selection Rationale

**Five planned comparisons** (pre-registered):

1. **Thinking vs non-thinking** (same architecture): Qwen3-235B Thinking vs Qwen3-235B Instruct. Identical weights, identical tokeniser. Only difference: thinking tokens enabled. Tests whether explicit chain-of-thought improves clinical reasoning.

2. **Reasoning specialist vs general**: DeepSeek R1 (RL-trained reasoning) vs DeepSeek V3.1 (same family, general). Tests whether reinforcement learning for reasoning transfers to clinical decision-making.

3. **Size scaling**: Llama 3.1 8B → Llama 3.3 70B → Llama 4 Maverick (~400B MoE). Same vendor lineage. Tests whether scale improves causal graph fidelity.

4. **Architecture diversity**: Dense (Llama 70B) vs MoE-small (Maverick 17B×128E) vs MoE-large (Qwen3 235B, DeepSeek V3.1/R1). Tests whether architecture matters for clinical reasoning.

5. **Cross-family**: Llama vs Qwen vs DeepSeek at comparable scale. Tests vendor-specific training effects on clinical knowledge.

## 4. Statistical Analysis Plan

### 4.1 Primary Analysis: Edge Detection

For each perturbation–baseline pair (P, B), for each model, across N=30 runs:

1. **Extract treatment stances** from Phase 1 (open-ended) + Phase 2 (targeted) responses
2. **Build treatment distributions**: P(stance | vignette) for each treatment option
3. **Fisher's exact test** per treatment: 2×2 table [recommended/not-recommended] × [baseline/perturbation]
4. **Jensen-Shannon divergence** between baseline and perturbation distributions (continuous edge weight)
5. **Benjamini-Hochberg FDR correction** across all tests (q = 0.05)

### 4.2 Statistical Power

With N=30 per condition and a medium effect size (Cramér's V = 0.3), Fisher's exact test has approximately 80% power at α = 0.05. The 12 null perturbations establish the noise floor: any effect size exceeding the 95th percentile of null-perturbation JSD values is considered clinically meaningful.

### 4.3 Divergence Taxonomy

Each edge in KG₁ maps to one of five outcomes in KG₂:

| Type | Definition | Detection method |
|------|-----------|-----------------|
| **Correct edge** | Significant, right direction, appropriate magnitude | Fisher p < 0.05 (FDR), direction matches KG₁ |
| **Missing edge** | KG₁ predicts change, model doesn't change | Failed to reject H₀ |
| **Spurious edge** | No KG₁ edge, model changes anyway | Rejected H₀ where KG₁ predicts independence |
| **Wrong direction** | Significant change, wrong direction | Directional test contradicts KG₁ |
| **Magnitude misalignment** | Right direction, inappropriate magnitude | JSD outside expected range for edge type |
| **Wrong conditionality** | Edge active in wrong clinical contexts | Interaction analysis across context pairs |

### 4.4 Aggregate Metrics

- **Recommendation accuracy**: TP/(TP+FN) — fraction of expected recommendations detected
- **Exclusion accuracy**: TN/(TN+FP) — fraction of expected contraindications correctly identified
- **Recommendation precision**: TP/(TP+FP) — avoid false recommendations
- **Conditionality recognition rate**: fraction of conditional edges where model uses correct conditioning
- **Uncertainty calibration**: for grey-zone items, model expresses appropriate uncertainty
- **Null specificity**: fraction of null perturbations where model correctly doesn't change

## 5. Pipeline Architecture

### 5.1 Files

| File | Lines | Function |
|------|-------|----------|
| `vignette_battery.json` | 5014 | 88 clinical vignettes with expected outcomes |
| `llm_query_runner.py` | 341 | Two-phase prompting, Together.ai API, checkpointing |
| `response_parser.py` | 592 | Stance extraction, Fisher/JSD/FDR, divergence taxonomy |
| `test_pipeline.py` | 149 | 23 integration tests (all pass) |
| `colab_runner.py` | 215 | Complete Colab notebook (9 cells) |

### 5.2 Two-Phase Prompting

**Phase 1 (ecological validity)**: Open-ended clinical question — "What is your treatment recommendation?" Captures the model's natural reasoning process without priming.

**Phase 2 (edge coverage)**: Family-specific targeted questions — "Is TLM appropriate? Is OPHL type II appropriate?" Forces the model to address every treatment option, ensuring complete stance extraction even for treatments the model didn't mention spontaneously.

Phase 2 stances take precedence over Phase 1 when both exist (higher specificity).

### 5.3 Response Parsing

- 15+ treatment types detected via regex (TLM, TORS, OPHL variants I/II/IIB/III, TL, CRT, ICT, RT variants, cisplatin, cetuximab, carboplatin)
- Negation-aware: "not indicated", "not appropriate" → excluded (not recommended)
- Sentence-level matching prioritised over window-level (prevents cross-line contamination)
- Conditionality detection: "depends on", "in this context", "for TLM but not OPHL"
- Uncertainty detection: "no consensus", "debatable", "grey zone", "individualized decision"

## 6. Execution Guide

### 6.1 Setup (Google Colab)

1. Upload to Google Drive `/KG1_study/`:
   - `vignette_battery.json`
   - `llm_query_runner.py`
   - `response_parser.py`

2. Add `TOGETHER_API_KEY` to Colab Secrets (Settings → Secrets)

3. Upload `colab_runner.py` as notebook (File → Upload)

### 6.2 Pilot Test (~$0.03, ~2 minutes)

```python
MODELS = ["llama-3.1-8b"]
N_RUNS = 1
PILOT_ITEMS = ["B1-BASE", "B1-P1", "B1-P2", "B1-NULL1"]
```

Validates: API connectivity, response format, stance extraction, scoring.

### 6.3 Full Run (~$164, ~4-6 hours)

```python
MODELS = [
    "llama-3.1-8b", "qwen3-235b-instruct", "llama-4-maverick",
    "llama-3.3-70b", "deepseek-v3.1", "qwen3-235b-thinking", "deepseek-r1"
]
N_RUNS = 30
PILOT_ITEMS = None
```

**Safe to interrupt**: JSONL checkpoint after every response. Re-running skips completed queries.

**Recommended strategy**: Run cheap models first (llama-3.1-8b alone: $1.62), validate parsing works on real outputs, then run all 7.

### 6.4 Outputs

```
/KG1_study/
├── results/
│   └── run_YYYYMMDD_HHMM.jsonl    # Raw API responses (36,960 records)
└── analysis/
    ├── metrics.json                 # Per-model aggregate scores
    ├── edge_tests.json              # Fisher/JSD/FDR per perturbation pair
    ├── divergences.json             # 5-type divergence classification
    ├── kg2.json                     # Reconstructed causal graph per model
    ├── parsed.json                  # Extracted treatment stances
    ├── report.md                    # Human-readable summary
    ├── summary.json                 # Paper-ready export
    ├── agg_perf.png                 # Aggregate performance bar chart
    ├── edge_heatmap.png             # Edge detection matrix
    └── jsd_dist.png                 # JSD distribution per model
```

## 7. Expected Findings (Hypotheses)

1. **Reasoning models (R1, Qwen-Thinking) will have higher edge detection rates** — explicit chain-of-thought should help with multi-step clinical reasoning

2. **Small models (8B) will fail on conditionality** — correctly detecting that TC inner cortex erosion blocks TLM but NOT OPHL requires nuanced understanding of surgical anatomy

3. **Thinking tokens will improve exclusion accuracy more than recommendation accuracy** — detecting contraindications requires more reasoning than detecting indications

4. **All models will over-generalise on some edges** — e.g., treating any cartilage involvement as CI for all surgery, when it's only CI for TLM

5. **Grey-zone items will show model overconfidence** — where experts disagreed (3 Delphi items <80% consensus), models will commit to definitive recommendations rather than expressing uncertainty

6. **Null perturbation JSD will be >0 for all models** — surface-level prompt sensitivity exists even with controlled vignettes (replicating the MIT FAccT 2025 finding)

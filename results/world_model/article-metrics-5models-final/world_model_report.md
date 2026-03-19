# World Model Evaluation Report

Behavioural causal discovery assessment of LLM implicit causal graphs.

**Framework**: Quality (alignment with expert consensus) × Solidity (internal consistency under repeated probing).

## 1. Summary

| Model | WMI | Label | Quality | Solidity | SID | Soft Recall | SNR | Split-Half Agr | Edge Entropy | Flip Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-r1 | **0.634** | Moderate world model | 0.674 | 0.596 | 34/243 | 62.1% | 2.14 | 80.2% | 0.561 | 49.7% |
| kimi-k2.5 | **0.611** | Moderate world model | 0.668 | 0.558 | 41/246 | 74.1% | 2.46 | 62.5% | 0.588 | 53.0% |
| llama-3.1-8b | **0.522** | Weak world model | 0.462 | 0.589 | 45/233 | 17.2% | 0.80 | 89.0% | 0.409 | 34.0% |
| mistral-small-24b | **0.507** | Weak world model | 0.443 | 0.579 | 31/236 | 43.1% | 1.66 | 82.1% | 0.623 | 58.7% |
| qwen3-next-80b-instruct | **0.524** | Weak world model | 0.430 | 0.640 | 32/237 | 39.7% | 1.87 | 88.8% | 0.502 | 42.7% |

## 2. Structural Intervention Distance (Quality)

SID counts how many intervention → treatment predictions the model gets wrong compared to expert consensus. Each perturbation is an intervention on a clinical variable; we check whether the model's response shifts match expert expectations.


### deepseek-r1

- **SID**: 34/243 (14.0% wrong)

Error breakdown:

- **no_shift_when_expected**: 23 cases
  - A1-P2 × total_laryngectomy: base=0% → pert=7%
  - A1-P3 × total_laryngectomy: base=0% → pert=14%
  - A2-P1 × tlm: base=93% → pert=80%
- **unexpected_reduction**: 11 cases
  - A2-P2 × rt_alone: base=87% → pert=20%
  - A2-P3 × tlm: base=93% → pert=7%
  - B1-P4 × surgical_lp: base=100% → pert=45%

### kimi-k2.5

- **SID**: 41/246 (16.7% wrong)

Error breakdown:

- **no_shift_when_expected**: 27 cases
  - A1-P2 × total_laryngectomy: base=11% → pert=0%
  - A1-P3 × total_laryngectomy: base=11% → pert=33%
  - A2-P1 × tlm: base=33% → pert=7%
- **unexpected_reduction**: 13 cases
  - A1-P2 × tlm: base=100% → pert=40%
  - A1-P3 × tlm: base=100% → pert=27%
  - B1-P4 × surgical_lp: base=93% → pert=38%
- **wrong_direction**: 1 cases
  - H1-P1 × total_laryngectomy: base=0% → pert=53%

### llama-3.1-8b

- **SID**: 45/233 (19.3% wrong)

Error breakdown:

- **no_shift_when_expected**: 42 cases
  - A1-P1 × tlm: base=100% → pert=100%
  - A1-P2 × total_laryngectomy: base=50% → pert=7%
  - A1-P3 × total_laryngectomy: base=50% → pert=44%
- **unexpected_reduction**: 3 cases
  - A1-P2 × nonsurgical_lp: base=100% → pert=47%
  - C1-P3 × nonsurgical_lp: base=100% → pert=47%
  - C1-P3 × concurrent_crt: base=100% → pert=40%

### mistral-small-24b

- **SID**: 31/236 (13.1% wrong)

Error breakdown:

- **no_shift_when_expected**: 27 cases
  - A1-P1 × tlm: base=100% → pert=60%
  - A1-P2 × total_laryngectomy: base=7% → pert=13%
  - A1-P3 × total_laryngectomy: base=7% → pert=9%
- **unexpected_reduction**: 4 cases
  - A2-P3 × tlm: base=100% → pert=13%
  - G1-REL01 × cisplatin_high_dose: base=100% → pert=0%
  - G1-GREY-S70 × cisplatin_high_dose: base=100% → pert=27%

### qwen3-next-80b-instruct

- **SID**: 32/237 (13.5% wrong)

Error breakdown:

- **no_shift_when_expected**: 27 cases
  - A1-P1 × tlm: base=100% → pert=87%
  - A1-P2 × total_laryngectomy: base=15% → pert=0%
  - A1-P3 × total_laryngectomy: base=15% → pert=15%
- **unexpected_reduction**: 5 cases
  - A2-P2 × rt_alone: base=73% → pert=7%
  - C1-P5 × total_laryngectomy: base=53% → pert=0%
  - G1-REL01 × cisplatin_high_dose: base=100% → pert=0%

## 3. Split-Half Reliability (Solidity)

Randomly split runs into two halves (100 times), build independent KGs, measure edge agreement. High agreement = stable internal structure.

- **deepseek-r1**: agreement = 80.2%, SHD = 11.5 ± 3.7
- **kimi-k2.5**: agreement = 62.5%, SHD = 21.8 ± 4.0
- **llama-3.1-8b**: agreement = 89.0%, SHD = 6.4 ± 2.5
- **mistral-small-24b**: agreement = 82.1%, SHD = 10.4 ± 2.9
- **qwen3-next-80b-instruct**: agreement = 88.8%, SHD = 6.5 ± 2.8

## 4. Edge Consistency Entropy (Solidity)

Shannon entropy of per-edge stance distributions. Low = consistent, high = noisy.


### deepseek-r1 (mean H = 0.561, flip rate = 49.7%)

**Most unstable edges** (highest entropy):

- F1-P1 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 1, 'uncertain': 1, 'excluded': 1}
- G1-NULL × cetuximab_concurrent: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 5, 'excluded': 5, 'recommended': 5}
- I1-P1 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 3, 'recommended': 3, 'excluded': 3}
- A2-BASE × ophl_any: H=1.000, dominant=excluded (50%), dist={'excluded': 6, 'recommended': 6}
- F1-BASE × rt_alone: H=1.000, dominant=excluded (50%), dist={'excluded': 3, 'recommended': 3}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × nonsurgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × total_laryngectomy: H=-0.000, dominant=excluded (100%)

### kimi-k2.5 (mean H = 0.588, flip rate = 53.0%)

**Most unstable edges** (highest entropy):

- G1-BASE × ict_rt: H=1.000, dominant=excluded (33%), dist={'excluded': 1, 'relative_ci': 1, 'recommended': 1}
- B1-NULL1 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 2, 'excluded': 2, 'recommended': 2}
- C1-P2 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 1, 'excluded': 1, 'recommended': 1}
- C1-P4 × ophl_type_ii: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 2, 'recommended': 2, 'excluded': 2}
- A1-P3 × ict_rt: H=1.000, dominant=recommended (50%), dist={'recommended': 2, 'excluded': 2}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × nonsurgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × ict_rt: H=-0.000, dominant=excluded (100%)

### llama-3.1-8b (mean H = 0.409, flip rate = 34.0%)

**Most unstable edges** (highest entropy):

- A1-BASE × total_laryngectomy: H=1.000, dominant=recommended (50%), dist={'recommended': 2, 'excluded': 2}
- A2-BASE × total_laryngectomy: H=1.000, dominant=recommended (50%), dist={'recommended': 4, 'excluded': 4}
- G1-BASE × cetuximab_concurrent: H=1.000, dominant=excluded (50%), dist={'excluded': 2, 'recommended': 2}
- H1-BASE × ophl_any: H=1.000, dominant=excluded (50%), dist={'excluded': 3, 'recommended': 3}
- A1-P3 × ict_rt: H=1.000, dominant=excluded (50%), dist={'excluded': 2, 'recommended': 2}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_accelerated: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × nonsurgical_lp: H=-0.000, dominant=recommended (100%)

### mistral-small-24b (mean H = 0.623, flip rate = 58.7%)

**Most unstable edges** (highest entropy):

- A1-P2 × rt_alone: H=1.000, dominant=uncertain (33%), dist={'uncertain': 1, 'excluded': 1, 'recommended': 1}
- A1-NULL × concurrent_crt: H=1.000, dominant=excluded (33%), dist={'excluded': 5, 'recommended': 5, 'relative_ci': 5}
- B1-P1 × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'relative_ci': 1, 'excluded': 1}
- B1-P4 × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'relative_ci': 1, 'excluded': 1}
- D1-P2 × rt_alone: H=1.000, dominant=excluded (33%), dist={'excluded': 1, 'relative_ci': 1, 'recommended': 1}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A2-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A2-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A2-BASE × total_laryngectomy: H=-0.000, dominant=excluded (100%)

### qwen3-next-80b-instruct (mean H = 0.502, flip rate = 42.7%)

**Most unstable edges** (highest entropy):

- J1-BASE × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'excluded': 1, 'relative_ci': 1}
- F1-P5 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 1, 'recommended': 1, 'excluded': 1}
- A2-NULL × ophl_any: H=1.000, dominant=excluded (50%), dist={'excluded': 6, 'recommended': 6}
- C1-P3 × rt_alone: H=1.000, dominant=recommended (50%), dist={'recommended': 4, 'excluded': 4}
- D1-P3 × cisplatin_high_dose: H=1.000, dominant=recommended (50%), dist={'recommended': 2, 'excluded': 2}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × concurrent_crt: H=-0.000, dominant=excluded (100%)
- A1-BASE × ict_rt: H=-0.000, dominant=excluded (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)

## 5. Signal-to-Noise Ratio (Solidity)

Ratio of mean JSD on causal perturbations vs null perturbations. SNR > 3 = good discrimination. SNR ~1 = no discrimination.

- **deepseek-r1**: SNR = 2.14 (causal μ=0.1545, null μ=0.0722), detection power = 17.3%
- **kimi-k2.5**: SNR = 2.46 (causal μ=0.1874, null μ=0.0763), detection power = 20.7%
- **llama-3.1-8b**: SNR = 0.80 (causal μ=0.0593, null μ=0.0741), detection power = 2.6%
- **mistral-small-24b**: SNR = 1.66 (causal μ=0.1157, null μ=0.0696), detection power = 13.1%
- **qwen3-next-80b-instruct**: SNR = 1.87 (causal μ=0.1031, null μ=0.0551), detection power = 15.6%

## 6. Interpretation


### deepseek-r1: Moderate world model (WMI = 0.634)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.

### kimi-k2.5: Moderate world model (WMI = 0.611)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.

### llama-3.1-8b: Weak world model (WMI = 0.522)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.

### mistral-small-24b: Weak world model (WMI = 0.507)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.

### qwen3-next-80b-instruct: Weak world model (WMI = 0.524)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.
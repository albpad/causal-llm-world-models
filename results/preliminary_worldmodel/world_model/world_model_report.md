# World Model Evaluation Report

Behavioural causal discovery assessment of LLM implicit causal graphs.

**Framework**: Quality (alignment with expert consensus) × Solidity (internal consistency under repeated probing).

## 1. Summary

| Model | WMI | Label | Quality | Solidity | SID | Soft Recall | SNR | Split-Half Agr | Edge Entropy | Flip Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-r1 | **0.657** | Moderate world model | 0.755 | 0.572 | 19/161 | 60.0% | 1.63 | 81.2% | 0.562 | 49.9% |
| mistral-small-24b | **0.644** | Moderate world model | 0.677 | 0.612 | 19/154 | 42.9% | 1.71 | 82.8% | 0.573 | 49.4% |
| qwen3-next-80b-instruct | **0.631** | Moderate world model | 0.671 | 0.592 | 20/155 | 45.7% | 1.34 | 81.9% | 0.487 | 38.1% |

## 2. Structural Intervention Distance (Quality)

SID counts how many intervention → treatment predictions the model gets wrong compared to expert consensus. Each perturbation is an intervention on a clinical variable; we check whether the model's response shifts match expert expectations.


### deepseek-r1

- **SID**: 19/161 (11.8% wrong)

Error breakdown:

- **no_shift_when_expected**: 15 cases
  - A1-P2 × total_laryngectomy: base=0% → pert=7%
  - A1-P3 × total_laryngectomy: base=0% → pert=14%
  - A2-P1 × tlm: base=93% → pert=80%
- **unexpected_reduction**: 4 cases
  - A2-P2 × rt_alone: base=87% → pert=20%
  - A2-P3 × tlm: base=93% → pert=7%
  - B1-P4 × surgical_lp: base=100% → pert=45%

### mistral-small-24b

- **SID**: 19/154 (12.3% wrong)

Error breakdown:

- **no_shift_when_expected**: 18 cases
  - A1-P1 × tlm: base=100% → pert=60%
  - A1-P2 × total_laryngectomy: base=7% → pert=13%
  - A1-P3 × total_laryngectomy: base=7% → pert=9%
- **unexpected_reduction**: 1 cases
  - A2-P3 × tlm: base=100% → pert=13%

### qwen3-next-80b-instruct

- **SID**: 20/155 (12.9% wrong)

Error breakdown:

- **no_shift_when_expected**: 18 cases
  - A1-P1 × tlm: base=100% → pert=87%
  - A1-P2 × total_laryngectomy: base=15% → pert=0%
  - A1-P3 × total_laryngectomy: base=15% → pert=15%
- **unexpected_reduction**: 2 cases
  - A2-P2 × rt_alone: base=73% → pert=7%
  - C1-P5 × total_laryngectomy: base=53% → pert=0%

## 3. Split-Half Reliability (Solidity)

Randomly split runs into two halves (100 times), build independent KGs, measure edge agreement. High agreement = stable internal structure.

- **deepseek-r1**: agreement = 81.2%, SHD = 6.6 ± 3.1
- **mistral-small-24b**: agreement = 82.8%, SHD = 6.0 ± 2.7
- **qwen3-next-80b-instruct**: agreement = 81.9%, SHD = 6.3 ± 1.9

## 4. Edge Consistency Entropy (Solidity)

Shannon entropy of per-edge stance distributions. Low = consistent, high = noisy.


### deepseek-r1 (mean H = 0.562, flip rate = 49.9%)

**Most unstable edges** (highest entropy):

- F1-P1 × rt_alone: H=1.000, dominant=uncertain (33%), dist={'uncertain': 1, 'relative_ci': 1, 'excluded': 1}
- A1-P1 × ophl_type_ii: H=1.000, dominant=excluded (50%), dist={'excluded': 3, 'recommended': 3}
- A2-BASE × ophl_any: H=1.000, dominant=excluded (50%), dist={'excluded': 6, 'recommended': 6}
- C1-P3 × rt_alone: H=1.000, dominant=excluded (50%), dist={'excluded': 3, 'relative_ci': 3}
- C1-P5 × ophl_type_ii: H=1.000, dominant=recommended (50%), dist={'recommended': 2, 'excluded': 2}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × nonsurgical_lp: H=-0.000, dominant=recommended (100%)
- A1-BASE × total_laryngectomy: H=-0.000, dominant=excluded (100%)

### mistral-small-24b (mean H = 0.573, flip rate = 49.4%)

**Most unstable edges** (highest entropy):

- A1-NULL × concurrent_crt: H=1.000, dominant=excluded (33%), dist={'excluded': 5, 'recommended': 5, 'relative_ci': 5}
- A1-P2 × rt_alone: H=1.000, dominant=uncertain (33%), dist={'uncertain': 1, 'excluded': 1, 'recommended': 1}
- B1-P1 × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'relative_ci': 1, 'excluded': 1}
- B1-P4 × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'relative_ci': 1, 'excluded': 1}
- D1-P2 × rt_alone: H=1.000, dominant=excluded (33%), dist={'excluded': 1, 'relative_ci': 1, 'recommended': 1}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × surgical_lp: H=-0.000, dominant=recommended (100%)
- A1-NULL × tlm: H=-0.000, dominant=recommended (100%)
- A1-NULL × ict_rt: H=-0.000, dominant=excluded (100%)
- A1-NULL × surgical_lp: H=-0.000, dominant=recommended (100%)

### qwen3-next-80b-instruct (mean H = 0.487, flip rate = 38.1%)

**Most unstable edges** (highest entropy):

- F1-P5 × rt_alone: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 1, 'recommended': 1, 'excluded': 1}
- J1-BASE × rt_alone: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'excluded': 1, 'relative_ci': 1}
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

- **deepseek-r1**: SNR = 1.63 (causal μ=0.1156, null μ=0.0711), detection power = 11.2%
- **mistral-small-24b**: SNR = 1.71 (causal μ=0.0850, null μ=0.0497), detection power = 16.2%
- **qwen3-next-80b-instruct**: SNR = 1.34 (causal μ=0.0740, null μ=0.0552), detection power = 7.7%

## 6. Interpretation


### deepseek-r1: Moderate world model (WMI = 0.657)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.

### mistral-small-24b: Moderate world model (WMI = 0.644)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.

### qwen3-next-80b-instruct: Moderate world model (WMI = 0.631)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.
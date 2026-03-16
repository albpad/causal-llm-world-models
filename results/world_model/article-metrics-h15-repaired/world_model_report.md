# World Model Evaluation Report

Behavioural causal discovery assessment of LLM implicit causal graphs.

**Framework**: Quality (alignment with expert consensus) × Solidity (internal consistency under repeated probing).

## 1. Summary

| Model | WMI | Label | Quality | Solidity | SID | Soft Recall | SNR | Split-Half Agr | Edge Entropy | Flip Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| kimi-k2.5 | **0.610** | Moderate world model | 0.669 | 0.556 | 40/246 | 74.1% | 2.46 | 61.7% | 0.588 | 53.0% |
| llama-3.1-8b | **0.522** | Weak world model | 0.462 | 0.590 | 45/233 | 17.2% | 0.80 | 89.4% | 0.409 | 34.0% |

## 2. Structural Intervention Distance (Quality)

SID counts how many intervention → treatment predictions the model gets wrong compared to expert consensus. Each perturbation is an intervention on a clinical variable; we check whether the model's response shifts match expert expectations.


### kimi-k2.5

- **SID**: 40/246 (16.3% wrong)

Error breakdown:

- **no_shift_when_expected**: 27 cases
  - A1-P2 × total_laryngectomy: base=11% → pert=0%
  - A1-P3 × total_laryngectomy: base=11% → pert=33%
  - A2-P1 × tlm: base=33% → pert=7%
- **unexpected_reduction**: 12 cases
  - A1-P2 × tlm: base=100% → pert=40%
  - A1-P3 × tlm: base=100% → pert=27%
  - B1-P9 × surgical_lp: base=93% → pert=12%
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

## 3. Split-Half Reliability (Solidity)

Randomly split runs into two halves (100 times), build independent KGs, measure edge agreement. High agreement = stable internal structure.

- **kimi-k2.5**: agreement = 61.7%, SHD = 22.2 ± 4.8
- **llama-3.1-8b**: agreement = 89.4%, SHD = 6.1 ± 2.6

## 4. Edge Consistency Entropy (Solidity)

Shannon entropy of per-edge stance distributions. Low = consistent, high = noisy.


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

## 5. Signal-to-Noise Ratio (Solidity)

Ratio of mean JSD on causal perturbations vs null perturbations. SNR > 3 = good discrimination. SNR ~1 = no discrimination.

- **kimi-k2.5**: SNR = 2.46 (causal μ=0.1874, null μ=0.0763), detection power = 20.7%
- **llama-3.1-8b**: SNR = 0.80 (causal μ=0.0593, null μ=0.0741), detection power = 2.6%

## 6. Interpretation


### kimi-k2.5: Moderate world model (WMI = 0.610)

The model has a moderately complete world model with good coverage of the major causal pathways. Gaps remain in specific areas.

### llama-3.1-8b: Weak world model (WMI = 0.522)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.
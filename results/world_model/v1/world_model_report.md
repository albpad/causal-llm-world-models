# World Model Evaluation Report

Behavioural causal discovery assessment of LLM implicit causal graphs.

**Framework**: Quality (alignment with expert consensus) × Solidity (internal consistency under repeated probing).

## 1. Summary

| Model | WMI | Label | Quality | Solidity | SID | Soft Recall | SNR | Split-Half Agr | Edge Entropy | Flip Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| kimi-k2.5 | **0.561** | Weak world model | 0.614 | 0.513 | 34/153 | 40.0% | 2.16 | 66.9% | 0.611 | 56.2% |
| llama-3.1-8b | **0.504** | Weak world model | 0.529 | 0.479 | 44/154 | 7.3% | 0.46 | 85.7% | 0.449 | 39.9% |

## 2. Structural Intervention Distance (Quality)

SID counts how many intervention → treatment predictions the model gets wrong compared to expert consensus. Each perturbation is an intervention on a clinical variable; we check whether the model's response shifts match expert expectations.


### kimi-k2.5

- **SID**: 34/153 (22.2% wrong)

Error breakdown:

- **no_shift_when_expected**: 31 cases
  - A1-P2 × total_laryngectomy: base=17% → pert=33%
  - A1-P3 × total_laryngectomy: base=17% → pert=40%
  - A2-P1 × tlm: base=33% → pert=11%
- **unexpected_reduction**: 3 cases
  - A1-P2 × tlm: base=100% → pert=45%
  - A1-P3 × tlm: base=100% → pert=43%
  - G1-REL01 × cisplatin_high_dose: base=73% → pert=0%

### llama-3.1-8b

- **SID**: 44/154 (28.6% wrong)

Error breakdown:

- **no_shift_when_expected**: 43 cases
  - A1-P1 × tlm: base=100% → pert=100%
  - A1-P2 × total_laryngectomy: base=30% → pert=20%
  - A1-P3 × total_laryngectomy: base=30% → pert=29%
- **unexpected_reduction**: 1 cases
  - J1-P6 × total_laryngectomy: base=87% → pert=45%

## 3. Split-Half Reliability (Solidity)

Randomly split runs into two halves (100 times), build independent KGs, measure edge agreement. High agreement = stable internal structure.

- **kimi-k2.5**: agreement = 66.9%, SHD = 18.1 ± 4.0
- **llama-3.1-8b**: agreement = 85.7%, SHD = 7.8 ± 2.1

## 4. Edge Consistency Entropy (Solidity)

Shannon entropy of per-edge stance distributions. Low = consistent, high = noisy.


### kimi-k2.5 (mean H = 0.611, flip rate = 56.2%)

**Most unstable edges** (highest entropy):

- A1-BASE × ophl_type_ii: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 1, 'recommended': 1, 'excluded': 1}
- F1-P3 × concurrent_crt: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'relative_ci': 1, 'excluded': 1}
- G1-REL02 × ict_rt: H=1.000, dominant=recommended (33%), dist={'recommended': 1, 'excluded': 1, 'uncertain': 1}
- G1-GREY-S70 × rt_alone: H=1.000, dominant=excluded (33%), dist={'excluded': 1, 'recommended': 1, 'relative_ci': 1}
- J1-P4 × ict_rt: H=1.000, dominant=relative_ci (33%), dist={'relative_ci': 2, 'excluded': 2, 'recommended': 2}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- C1-BASE × concurrent_crt: H=-0.000, dominant=recommended (100%)
- D1-BASE × tlm: H=-0.000, dominant=excluded (100%)
- D1-BASE × ophl_any: H=-0.000, dominant=excluded (100%)
- E1-BASE × tlm: H=-0.000, dominant=excluded (100%)

### llama-3.1-8b (mean H = 0.449, flip rate = 39.9%)

**Most unstable edges** (highest entropy):

- G1-NULL × tlm: H=1.000, dominant=uncertain (33%), dist={'uncertain': 1, 'relative_ci': 1, 'excluded': 1}
- J1-BASE × ophl_any: H=1.000, dominant=excluded (50%), dist={'excluded': 2, 'recommended': 2}
- B1-P8 × rt_alone: H=1.000, dominant=uncertain (50%), dist={'uncertain': 2, 'excluded': 2}
- C1-P5 × rt_alone: H=1.000, dominant=recommended (50%), dist={'recommended': 2, 'excluded': 2}
- F1-P5 × ict_rt: H=1.000, dominant=recommended (50%), dist={'recommended': 5, 'excluded': 5}

**Most stable edges** (lowest entropy):

- A1-BASE × tlm: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_alone: H=-0.000, dominant=recommended (100%)
- A1-BASE × rt_accelerated: H=-0.000, dominant=recommended (100%)
- A1-P1 × tlm: H=-0.000, dominant=recommended (100%)
- A1-P1 × ict_rt: H=-0.000, dominant=excluded (100%)

## 5. Signal-to-Noise Ratio (Solidity)

Ratio of mean JSD on causal perturbations vs null perturbations. SNR > 3 = good discrimination. SNR ~1 = no discrimination.

- **kimi-k2.5**: SNR = 2.16 (causal μ=0.2274, null μ=0.1051), detection power = 15.0%
- **llama-3.1-8b**: SNR = 0.46 (causal μ=0.0429, null μ=0.0939), detection power = 0.0%

## 6. Interpretation


### kimi-k2.5: Weak world model (WMI = 0.561)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.

### llama-3.1-8b: Weak world model (WMI = 0.504)

The model has a partial world model with moderate coverage but significant gaps. Some causal pathways are represented but the model cannot reliably generalise across novel variable combinations.
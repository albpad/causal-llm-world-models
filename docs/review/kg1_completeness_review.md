# KG1 Completeness Review

Source article: [/Users/albertopaderno/Downloads/doc 3.pdf](/Users/albertopaderno/Downloads/doc%203.pdf)

## Bottom line

KG1 is strong and mostly source-grounded, but it is not fully source-complete yet.

The current graph covers the core atomic treatment-selection logic well, but three items need confirmation before KG1 should be treated as locked:

1. Add `S72R` as an explicit edge source for alternative concurrent regimens after cisplatin ineligibility.
2. Add `S73R` as the source for accelerated or hyperfractionated radiotherapy alone when the patient is unfit for any systemic treatment and declines total laryngectomy.
3. Re-anchor `H1-P4` to `S129` because progression / no response after induction chemotherapy is not directly encoded today.

## Quick summary

- Current battery:
  - `12` baselines
  - `76` perturbations
  - `57` unique statement-linked probes
- Current KG1 coverage:
  - Strong for direct stage / extent / function / cisplatin-eligibility / post-ICT rules
  - Incomplete for one fallback-treatment branch and one ICT progression anchor
- Recommended decision:
  - Approve KG1 after adding `S72R`, `S73R`, and `S129`
  - Keep second-order interaction statements out of KG1 v1 unless you explicitly want a denser graph

## Domain review

| Domain | Included in current KG1 | Status | Notes |
|---|---|---|---|
| Granular T2-T3 / transoral surgery | `S4R`, `SA2`, `S5R`, `S6R`, `S7R`, `S8`, `S9R`, `S10R` | Good | Core transoral logic is well represented |
| OPHL / conservative surgery | `S13`, `S14`, `S15R`, `S16R`, `S17R`, `S18R` | Good | Main eligibility / contraindication edges are present |
| Non-surgical LP / RT / chemo | `S19R`, `S20R`, `S21`, `S22`, `S23R`, `S24R`, `S27`, `S28`, `S30`, `S31R` | Good but incomplete | Missing explicit fallback-regimen statements `S72R` and `S73R` |
| T4a selection | `S35R`, `S38R`, `S39R`, `S40R`, `S41R`, `S42R`, `S43`, `S45`, `S46`, `S47R`, `S49R`, `S52R`, `S55R` | Good | Main high-stakes treatment shifts are covered |
| Systemic fitness / cisplatin eligibility | `S67`, `S68R`, `S69R`, `S70`, `S74R`, `S75R`, `S77R` | Good but incomplete | `S68R` is currently doing some work that should be grounded by `S72R` |
| Older / frailty | `S80`, `S84`, `S88`, `S89` | Acceptable for v1 | Core treatment-selection effect of frailty is covered |
| Prognostic / predictive / post-ICT | `S111R`, `S112`, `S115`, `S116`, `S119R`, `S120R`, `S121R`, `SA6` | Good but incomplete | Progression / no-response scenario should be anchored to `S129` |

## Required additions or re-anchors

### 1. `S72R`

Article meaning:
- If the patient is unfit for any cisplatin schedule and refuses total laryngectomy, `cetuximab` or `carboplatin + 5FU` can be used concurrently with radiation.

Why it matters:
- The battery already recommends `cetuximab_concurrent` and `carboplatin_5fu` in cisplatin-ineligible settings.
- Today those recommendations are mostly grounded via `S68R`, which defines contraindications to cisplatin, not the fallback regimen itself.

Recommendation:
- Add `S72R` as an explicit source edge for those alternative-regimen recommendations.

### 2. `S73R`

Article meaning:
- If the patient is unfit for any systemic treatment and declines total laryngectomy, accelerated or hyperfractionated radiotherapy alone can be offered.

Why it matters:
- The current battery uses `S67` to exclude chemo-based preservation when systemic fitness is poor.
- That is incomplete because the article still provides a fallback non-surgical route in this situation.

Recommendation:
- Add a dedicated perturbation or branch grounded in `S73R`.
- Do not let `S67` imply that all non-surgical preservation is excluded.

### 3. `S129` for `H1-P4`

Article meaning:
- In advanced disease or no response to induction chemotherapy, the team should be clear that larynx-preservation strategies have worse functional and survival outcomes than total laryngectomy.

Why it matters:
- `H1-P4` currently tests progression after ICT with a strong shift toward total laryngectomy.
- That scenario is clinically coherent, but it is not currently source-anchored in the battery.

Recommendation:
- Anchor `H1-P4` to `S129`.
- Keep `S121R` for stable-disease refusal-of-TL logic.

## Statements reviewed and intentionally left out of KG1 v1

These are not obvious mistakes. They are mostly second-order interaction rules, process statements, or non-atomic choices.

| Statement | Proposed status | Reason |
|---|---|---|
| `S25-S26R` | Leave out of v1 | Tailored CRT vs ICT choice is multi-factor and not a clean single-edge rule |
| `S29R` | Leave out of v1 | Comparative long-term mortality, not a direct treatment-selection edge |
| `S44R` | Leave out of v1 | Broad contextual factors, not a single atomic edge |
| `S48` | Leave out of v1 | Functional consequence of adjuvant treatment after OPHL, not a baseline treatment-selection edge |
| `S71R`, `S76`, `S78` | Leave out of v1 | Workup / assessment / schedule nuance, not primary causal treatment edges |
| `S85`, `S86R2`, `S87R`, `S91R` | Optional v2 expansion | Older-patient interaction rules; mostly refinements of already represented age / frailty / hearing logic |
| `S117`, `S118` | Leave out of v1 | Predictive-method / early-assessment statements without stable direct treatment edge encoding |

## Practical conclusion

If you want a clean KG1 v1 for the next model-testing phase:

- Keep the current core structure
- Add `S72R`
- Add `S73R`
- Re-anchor `H1-P4` to `S129`
- Leave the older-patient interaction layer for KG1 v2 unless you want a denser graph now

## Quick approval checklist

- Approve `S72R` addition: `yes / no`
- Approve `S73R` addition: `yes / no`
- Approve `S129` anchor for `H1-P4`: `yes / no`
- Keep `S85`, `S86R2`, `S87R`, `S91R` out of KG1 v1: `yes / no`

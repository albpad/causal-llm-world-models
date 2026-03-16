# Behavioral Causal Discovery as a Test of World Models in LLMs

## 1. The problem

The current LLM evaluation stack is dominated by next-token-derived tasks: multiple choice, factual recall, free-response agreement with experts, and post-hoc reasoning quality. These evaluations are useful, but they do **not** answer the question that matters for the world-model agenda:

> Does the model behave as if it has an internal causal representation of the domain?

A model can score well on benchmarks by exploiting statistical regularities, memorized correlations, or stylistically plausible justifications, while still lacking the interventional structure required for robust generalization.

If the term **world model** is to have operational meaning, it should imply at least three properties:

- **Intervention sensitivity**: when a causally relevant variable changes, the model’s decisions should change in the expected direction.
- **Invariance to irrelevant change**: perturbations that should be causally null should not induce substantial behavioral shifts.
- **Structural coherence**: these response patterns should compose into a graph that resembles a trusted causal structure rather than a bag of local associations.

This is what standard benchmark evaluation generally fails to test.

## 2. The idea

We propose **behavioral causal discovery**: recover the causal graph the model behaves as if it has, and compare it to a gold-standard causal graph derived independently of the model.

Formally:

- Let **KG1** be a trusted reference causal graph over domain variables and decision targets.
- Construct matched baseline / perturbation examples that approximate atomic interventions `do(X = x')`.
- Query the model repeatedly on both baseline and perturbed cases.
- Convert outputs into structured action or treatment stances.
- Measure whether the perturbation causes the expected distributional shift in model behavior.
- Aggregate detected shifts into a recovered behavioral graph, **KG2**.

The central object of evaluation is therefore not answer accuracy but the relationship:

`KG1 (reference structure) -> perturbations -> model behavior -> KG2 (recovered structure)`

This turns “does the model have a world model?” into a graph recovery problem.

## 3. Why this is a genuine world-model test

This framework targets the property people usually mean when they talk about world models: that the system has an internalized structure of how the world changes under intervention.

It does so in a way that is:

- **behavioral**: no access to weights, activations, or hidden states is required
- **causal**: the unit of analysis is intervention-induced change, not static correctness
- **structural**: success requires recovery of a coherent graph, not isolated good answers
- **falsifiable**: a model can fail by missing edges, flipping directions, or reacting more to noise than to causal perturbations

In other words, this is not another benchmark. It is an attempt to operationalize a specific claim about internal structure.

## 4. Experimental realization

We instantiate the framework in a tightly specified expert domain with a well-defined causal reference graph.

### Reference graph

- **137** expert consensus statements distilled into **55 directed causal edges**
- source nodes are clinically meaningful variables
- target nodes are treatment decisions

### Behavioral probe set

- **88 counterfactual vignettes**
- **12** baseline cases
- **64** causal perturbations
- **12** null perturbations

Each perturbation changes exactly one relevant variable while all others are held fixed. The null controls alter variables that should not causally change the decision.

### Query and parsing pipeline

- repeated stochastic sampling across runs
- two-phase prompting: open-ended recommendation plus structured stance elicitation
- rule-based parsing into treatment/action stances
- perturbation-vs-baseline comparison using:
  - **Fisher’s exact test** with multiple-testing correction
  - **Jensen-Shannon divergence (JSD)** as a continuous shift measure

### Graph recovery and evaluation

The recovered graph KG2 is evaluated against KG1 along three orthogonal dimensions:

1. **Coverage**
   How much of the expert graph is recovered at all?

2. **Fidelity**
   When edges are recovered, are they directionally and interventionally correct?
   We quantify this with:
   - direction accuracy
   - **Structural Intervention Distance (SID)** adapted to intervention-treatment predictions

3. **Discriminability**
   Does the model respond more strongly to causal perturbations than to null perturbations?
   We quantify this with:
   - causal vs null **mean JSD**
   - **signal-to-noise ratio (SNR)**
   - detection power above the null 95th percentile

These three axes separate very different failure modes that benchmark accuracy collapses together.

## 5. Preview of the results

We tested two models:

- **Kimi K2.5**, a stronger reasoning-oriented model
- **Llama 3.1-8B Instruct**, a smaller standard instruct model

### Kimi K2.5

- soft recall: **41/55 = 74.5%**
- hard recall: **10/55 = 18.2%**
- direction accuracy: **70.0%**
- SID: **37/165 = 22.4%**
- mean causal JSD: **0.229**
- mean null JSD: **0.078**
- SNR: **2.95**
- detection power: **28.5%**

Interpretation: the model recovers a substantial portion of the expert graph and shows real causal sensitivity, but it remains incomplete and far from robust. It has a **partial world model**, not a complete one.

### Llama 3.1-8B

- soft recall: **4/55 = 7.3%**
- hard recall: **1/55 = 1.8%**
- direction accuracy: **100.0%**, but only on the **4** soft-detected edges
- SID: **44/154 = 28.6%**
- mean causal JSD: **0.043**
- mean null JSD: **0.094**
- SNR: **0.46**
- detection power: **0.0%**

Interpretation: this is the signature of a model without a coherent causal world model. The strongest result is not just low recall; it is that the model responds **more strongly to irrelevant perturbations than to causal ones**.

## 6. What the results mean

The main conclusion is not merely that one model is better than another.

The deeper conclusion is that:

> benchmark-style competence can coexist with weak, partial, or absent world-model structure.

The stronger model is not “solved”; it is only partial. The smaller standard model does not fail gracefully; it fails in a way that exposes the absence of reliable interventional structure.

This matters because a world model should not be inferred from surface competence. It should be demonstrated by correct behavior under controlled change.

## 7. Why this matters for AI research

This is not fundamentally a medical paper. The clinical domain is only a well-bounded testbed with a strong external reference graph.

The broader contribution is methodological:

- a way to evaluate world-model claims **without** mechanistic interpretability access
- a way to distinguish recall from causal structure
- a way to turn “does the model understand the domain?” into a graph comparison problem
- a way to quantify failure modes that are directly relevant to planning, science, robotics, and safety

Any domain with a sufficiently trusted causal scaffold can be used in the same way.

## 8. Bottom line

If the field wants to argue that LLMs have world models, then answer accuracy is not enough.

What matters is whether the model:

- tracks the right variables
- ignores the wrong variables
- responds correctly to intervention
- and composes those responses into a coherent causal structure

Behavioral causal discovery is a concrete way to test that claim.

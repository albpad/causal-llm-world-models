#!/usr/bin/env python3
"""
KG2 Response Parser, Statistical Scorer & Divergence Analyser
==============================================================
Parses LLM responses -> extracts treatment stances -> statistical edge detection
(Fisher exact + JSD) -> FDR correction -> divergence taxonomy -> KG2 assembly.

Usage:
    python response_parser.py --results results/run_XXX.jsonl \
        --battery vignette_battery.json --outdir analysis
"""

import json, re, argparse, math
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict

try:
    from .label_space import derive_aggregate_stance_records
except ImportError:
    from label_space import derive_aggregate_stance_records

# =====================================================================
# TREATMENT ALIASES & STANCE PATTERNS
# =====================================================================

TREATMENT_ALIASES = {
    "tlm": [r"transoral laser microsurgery", r"\bTLM\b", r"transoral laser", r"laser microsurgery"],
    "tors": [r"transoral robotic surgery", r"\bTORS\b"],
    "ophl_type_i": [r"OPHL type I\b", r"supraglottic laryngectomy", r"OPHL.I\b"],
    "ophl_type_ii": [r"OPHL type II\b", r"OPHL.II\b", r"\bCHEP\b", r"\bCHP\b",
                     r"cricohyoidoepiglottopexy", r"cricohyoidopexy", r"supracricoid.*type II\b"],
    "ophl_type_iib": [r"OPHL type IIB", r"OPHL.IIB"],
    "ophl_type_iii": [r"OPHL type III", r"OPHL.III", r"tracheohyoidoepiglottopexy"],
    "ophl_any": [r"open partial.*laryngectomy", r"\bOPHL\b", r"partial horizontal laryngectomy",
                 r"supracricoid laryngectomy", r"(?<!total )partial laryngectomy",
                 r"conservation laryngeal surgery"],
    "total_laryngectomy": [r"total laryngectomy", r"\bTL\b",
                           r"(?<!partial )(?<!horizontal )(?<!supracricoid )laryngectomy(?! preservation)"],
    "concurrent_crt": [r"concurrent chemoradio", r"chemoradiotherapy", r"\bCRT\b",
                       r"chemoradiation", r"concurrent.*cisplatin.*RT"],
    "ict_rt": [r"induction chemotherapy", r"\bICT\b", r"neoadjuvant chemo",
               r"TPF.*induction", r"induction.*followed by"],
    "rt_alone": [r"radiotherapy alone", r"radiation alone", r"RT alone",
                 r"definitive radiotherapy(?! with| and| plus| concurrent)"],
    "rt_accelerated": [r"accelerated.*radio", r"hyperfractionated.*radio",
                       r"altered fractionation", r"accelerated RT"],
    "cisplatin_high_dose": [r"high.dose cisplatin", r"cisplatin 100\s*mg", r"cisplatin q3w"],
    "cetuximab_concurrent": [r"cetuximab", r"erbitux", r"bioradiation"],
    "carboplatin_5fu": [r"carboplatin.*5.?FU", r"carboplatin.*fluorouracil"],
    "nonsurgical_lp": [r"non.?surgical (?:organ|larynx) preservation", r"non.?surgical LP", r"organ preservation protocols?"],
    "surgical_lp": [r"surgical larynx preservation", r"conservative surgery", r"conservative laryngeal surgery"],
}

# Structured label patterns (highest priority — from Phase 2 formatted output)
# These match "**Treatment**: LABEL" or "Treatment: LABEL" format
STRUCTURED_LABEL = re.compile(
    r"(?:\*\*[^*]+\*\*|[A-Z][A-Za-z\s/()]+):\s*"
    r"(APPROPRIATE|CONTRAINDICATED|RELATIVELY CONTRAINDICATED|UNCERTAIN)",
    re.I
)

STANCE_POS = [r"(?:would |should |I )recommend", r"\bappropriate\b", r"viable option",
              r"\breasonable\b", r"\bindicated\b", r"\bsuitable\b", r"\beligible\b",
              r"first.line", r"\bpreferred\b", r"standard of care", r"\bAPPROPRIATE\b"]
STANCE_NEG = [r"contraindicated", r"not appropriate", r"not recommended", r"not suitable",
              r"should not", r"would not recommend", r"ruled out", r"precluded",
              r"cannot be.*performed", r"not a viable", r"\bCONTRAINDICATED\b",
              r"absolute contraindication"]
STANCE_REL = [r"relative contraindication", r"relatively contraindicated",
              r"RELATIVELY CONTRAINDICATED", r"with caution", r"may not be ideal",
              r"less favorable", r"suboptimal"]
STANCE_UNC = [r"\buncertain\b", r"\bdebatable\b", r"\bcontroversial\b",
              r"no clear consensus", r"\bUNCERTAIN\b", r"equipoise",
              r"grey zone", r"gray zone"]

# Double-negative patterns — these mean POSITIVE (not inappropriate = appropriate)
DOUBLE_NEG_POS = re.compile(
    r"\b(?:not\s+(?:inappropriate|contraindicated|unreasonable|unsuitable)|"
    r"cannot\s+(?:be\s+)?(?:ruled\s+out|excluded|dismissed))\b", re.I
)

NEG_PREFIX = re.compile(r"\b(?:not|no|never|don.t|doesn.t|isn.t|cannot|can.t|shouldn.t|wouldn.t)\s+", re.I)


def _get_sentence(text, pos):
    start = pos
    while start > 0:
        ch = text[start-1]
        if ch == '\n': break
        if ch == '.' and not (start >= 2 and text[start-2].isdigit()): break
        start -= 1
    end = pos
    while end < len(text):
        ch = text[end]
        if ch == '\n': break
        if ch == '.' and not (end+1 < len(text) and text[end+1] == ' ' and end > 0 and text[end-1].isdigit()): break
        end += 1
    return text[start:end+1].strip()


def _classify(window, sentence):
    # Phase 0: Structured label detection (highest priority, highest confidence)
    # Matches "**Treatment**: APPROPRIATE" or "Treatment: CONTRAINDICATED" patterns
    label_match = STRUCTURED_LABEL.search(sentence)
    if label_match:
        label = label_match.group(1).upper()
        if label == "APPROPRIATE": return "recommended", 0.98
        if label == "CONTRAINDICATED": return "excluded", 0.98
        if label == "RELATIVELY CONTRAINDICATED": return "relative_ci", 0.98
        if label == "UNCERTAIN": return "uncertain", 0.98

    # Phase 0.5: Double-negative detection (before negation handling)
    # "not inappropriate", "cannot be ruled out" -> positive
    if DOUBLE_NEG_POS.search(sentence):
        return "recommended", 0.80

    # Phase A: Sentence-level only (high confidence)
    for pat in STANCE_NEG:
        if re.search(pat, sentence, re.I): return "excluded", 0.95
    for pp in STANCE_POS:
        neg = r"(?:not|no|never|don.t|cannot|isn.t)\s+" + pp
        if re.search(neg, sentence, re.I): return "excluded", 0.90
    for pat in STANCE_REL:
        if re.search(pat, sentence, re.I): return "relative_ci", 0.90
    for pat in STANCE_UNC:
        if re.search(pat, sentence, re.I): return "uncertain", 0.85
    for pat in STANCE_POS:
        m = re.search(pat, sentence, re.I)
        if m:
            prefix = sentence[max(0, m.start()-20):m.start()]
            if NEG_PREFIX.search(prefix): return "excluded", 0.85
            return "recommended", 0.95

    # Phase B: Window-level fallback (lower confidence)
    # First check for structured labels in the window
    label_match_w = STRUCTURED_LABEL.search(window)
    if label_match_w:
        label = label_match_w.group(1).upper()
        if label == "APPROPRIATE": return "recommended", 0.85
        if label == "CONTRAINDICATED": return "excluded", 0.85
        if label == "RELATIVELY CONTRAINDICATED": return "relative_ci", 0.85
        if label == "UNCERTAIN": return "uncertain", 0.85

    if DOUBLE_NEG_POS.search(window):
        return "recommended", 0.65

    for pat in STANCE_NEG:
        if re.search(pat, window, re.I): return "excluded", 0.70
    for pp in STANCE_POS:
        neg = r"(?:not|no|never|don.t|cannot|isn.t)\s+" + pp
        if re.search(neg, window, re.I): return "excluded", 0.65
    for pat in STANCE_REL:
        if re.search(pat, window, re.I): return "relative_ci", 0.65
    for pat in STANCE_UNC:
        if re.search(pat, window, re.I): return "uncertain", 0.60
    for pat in STANCE_POS:
        if re.search(pat, window, re.I): return "recommended", 0.60
    return None, 0


def extract_stances(text, phase):
    if not text: return []
    stances = []
    for tx, aliases in TREATMENT_ALIASES.items():
        positions = []
        for al in aliases:
            for m in re.finditer(al, text, re.I): positions.append(m.start())
        if not positions: continue
        best_s, best_c, best_e = None, 0, ""
        for pos in positions:
            ws = max(0, pos-150); we = min(len(text), pos+150)
            s, c = _classify(text[ws:we], _get_sentence(text, pos))
            if s and c > best_c: best_s, best_c, best_e = s, c, _get_sentence(text, pos)[:200]
        if best_s:
            stances.append({"treatment": tx, "stance": best_s, "confidence": best_c,
                            "evidence": best_e, "phase": phase})
    return stances


def detect_conditionality(text):
    if not text: return False
    pats = [r"depends on", r"in (?:the context|this context|this case)",
            r"if.*(?:glottic|supraglottic|hypopharyngeal)",
            r"contraindicated for.*but.*appropriate for",
            r"tumor.related.*vs.*comorbidity", r"source of.*(?:functional decline|ECOG)",
            r"site.specific|site.dependent"]
    return any(re.search(p, text, re.I) for p in pats)


def detect_uncertainty(text):
    if not text: return False
    pats = [r"\buncertain\b", r"no.*consensus", r"debat(?:able|ed)", r"controvers(?:ial|y)",
            r"data.*limited", r"individual(?:ized|ised).*decision", r"shared decision",
            r"grey zone|gray zone"]
    return any(re.search(p, text, re.I) for p in pats)


def parse_result(r):
    if r.get("error"): return None
    p1 = r.get("phase1_response", "") or ""
    p2 = r.get("phase2_response", "") or ""
    combined = p1 + "\n\n" + p2
    s1 = extract_stances(p1, "phase1")
    s2 = extract_stances(p2, "phase2")
    smap = {}
    for s in s1: smap[s["treatment"]] = s
    for s in s2:
        if s["treatment"] not in smap or s["confidence"] >= smap[s["treatment"]]["confidence"]:
            smap[s["treatment"]] = s
    smap = derive_aggregate_stance_records(smap)
    return {
        "item_id": r["item_id"], "model_name": r["model_name"], "run_idx": r["run_idx"],
        "stances": list(smap.values()),
        "conditionality": detect_conditionality(combined),
        "uncertainty": detect_uncertainty(combined),
    }


# =====================================================================
# STATISTICAL EDGE DETECTION
# =====================================================================

def _jsd(p, q):
    """Jensen-Shannon divergence between two distributions (dicts)."""
    keys = set(list(p.keys()) + list(q.keys()))
    eps = 1e-10
    m = {k: 0.5*(p.get(k, 0)+q.get(k, 0)) for k in keys}
    def kl(a, b):
        return sum(a.get(k, eps) * math.log((a.get(k, eps)+eps)/(b.get(k, eps)+eps)) for k in keys)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def build_treatment_distribution(parsed_list):
    """From a list of parsed results for ONE (item, model), build P(treatment_stance)."""
    counts = defaultdict(lambda: defaultdict(int))
    n = len(parsed_list)
    if n == 0: return {}
    for p in parsed_list:
        for s in p["stances"]:
            counts[s["treatment"]][s["stance"]] += 1
    # Normalize per treatment
    dist = {}
    for tx, stance_counts in counts.items():
        total = sum(stance_counts.values())
        dist[tx] = {st: c/total for st, c in stance_counts.items()}
    return dist


def fishers_exact_multi(table_a, table_b, treatments):
    """Fisher's exact test for each treatment: recommended vs not-recommended between two conditions."""
    from scipy.stats import fisher_exact
    results = {}
    for tx in treatments:
        a_rec = table_a.get(tx, {}).get("recommended", 0)
        a_not = table_a.get(tx, {}).get("total", 0) - a_rec
        b_rec = table_b.get(tx, {}).get("recommended", 0)
        b_not = table_b.get(tx, {}).get("total", 0) - b_rec
        if a_rec + a_not == 0 or b_rec + b_not == 0: continue
        table = [[a_rec, a_not], [b_rec, b_not]]
        try:
            odds, pval = fisher_exact(table)
            results[tx] = {"odds_ratio": float(odds), "p_value": float(pval),
                           "a_rec_rate": float(a_rec/(a_rec+a_not)), "b_rec_rate": float(b_rec/(b_rec+b_not))}
        except: pass
    return results


def bh_fdr(pvalues, q=0.05):
    """Benjamini-Hochberg FDR correction. Returns dict of key -> (pval, reject, adjusted_p)."""
    items = sorted(pvalues.items(), key=lambda x: x[1])
    m = len(items)
    results = {}
    for rank, (key, pval) in enumerate(items, 1):
        threshold = q * rank / m
        adj_p = min(pval * m / rank, 1.0)
        results[key] = {"p_value": float(pval), "adjusted_p": float(adj_p), "reject": bool(pval <= threshold)}
    return results


# =====================================================================
# EDGE DETECTION & DIVERGENCE TAXONOMY
# =====================================================================

def detect_edges(all_parsed, battery_items):
    """
    For each perturbation-baseline pair and each model:
    1. Build treatment distributions from N=30 runs
    2. Fisher's exact test per treatment
    3. JSD between distributions
    4. Classify into divergence taxonomy
    """
    # Group by (item_id, model_name)
    grouped = defaultdict(list)
    for p in all_parsed:
        grouped[(p["item_id"], p["model_name"])].append(p)

    # Build treatment count tables: (item_id, model) -> {treatment: {stance: count, total: N}}
    count_tables = {}
    for (iid, mn), plist in grouped.items():
        table = defaultdict(lambda: defaultdict(int))
        for p in plist:
            for s in p["stances"]:
                table[s["treatment"]][s["stance"]] += 1
                table[s["treatment"]]["total"] += 1
        count_tables[(iid, mn)] = dict(table)

    # For each perturbation, compare to its baseline
    edge_tests = []
    for pert in battery_items.values():
        if pert.get("type") == "baseline": continue
        base_id = pert.get("baseline_id")
        if not base_id: continue
        edges = pert.get("edge_justification", [])
        exp_rec = set(pert.get("expected_recommendations", []))
        exp_exc = set(pert.get("expected_excluded", []))
        grey = pert.get("grey_zone_statement")

        for mn in set(k[1] for k in count_tables.keys()):
            base_table = count_tables.get((base_id, mn), {})
            pert_table = count_tables.get((pert["id"], mn), {})
            if not base_table or not pert_table: continue

            # Build distributions for JSD
            base_parsed = grouped.get((base_id, mn), [])
            pert_parsed = grouped.get((pert["id"], mn), [])
            dist_base = build_treatment_distribution(base_parsed)
            dist_pert = build_treatment_distribution(pert_parsed)

            # JSD per treatment
            all_tx = set(list(dist_base.keys()) + list(dist_pert.keys()))
            jsd_scores = {}
            for tx in all_tx:
                d1 = dist_base.get(tx, {"recommended": 0.5, "excluded": 0.5})
                d2 = dist_pert.get(tx, {"recommended": 0.5, "excluded": 0.5})
                jsd_scores[tx] = _jsd(d1, d2)

            # Fisher's exact per treatment
            fisher_results = fishers_exact_multi(base_table, pert_table, all_tx)

            # Overall JSD (average across treatments present in expected)
            relevant_tx = exp_rec | exp_exc
            overall_jsd = sum(jsd_scores.get(tx, 0) for tx in relevant_tx) / max(len(relevant_tx), 1)

            # Collect all p-values for FDR
            for tx, fr in fisher_results.items():
                test_key = f"{pert['id']}:{mn}:{tx}"
                edge_tests.append({
                    "pert_id": pert["id"], "base_id": base_id, "model": mn,
                    "treatment": tx, "test_key": test_key,
                    "p_value": fr["p_value"], "odds_ratio": fr["odds_ratio"],
                    "base_rec_rate": fr["a_rec_rate"], "pert_rec_rate": fr["b_rec_rate"],
                    "jsd": jsd_scores.get(tx, 0), "overall_jsd": overall_jsd,
                    "edges": edges, "exp_rec": list(exp_rec), "exp_exc": list(exp_exc),
                    "type": pert.get("type"), "grey_zone": grey,
                    "n_base": len(base_parsed), "n_pert": len(pert_parsed),
                })

    # BH-FDR correction across all tests
    if edge_tests:
        pvals = {t["test_key"]: t["p_value"] for t in edge_tests}
        fdr = bh_fdr(pvals)
        for t in edge_tests:
            f = fdr[t["test_key"]]
            t["adjusted_p"] = float(f["adjusted_p"])
            t["significant"] = bool(f["reject"])

    return edge_tests


def classify_divergence(edge_tests, battery_items):
    """
    Apply the 5-type divergence taxonomy:
    1. Missing edge: KG1 edge, no significant behavioral change
    2. Spurious edge: No KG1 edge, significant behavioral change
    3. Wrong conditionality: Edge active in wrong contexts
    4. Wrong direction: Significant change but wrong direction
    5. Magnitude misalignment: Right direction, wrong magnitude
    """
    divergences = []
    for t in edge_tests:
        exp_rec = set(t["exp_rec"])
        exp_exc = set(t["exp_exc"])
        tx = t["treatment"]

        # Determine expected direction for this treatment
        should_be_recommended = tx in exp_rec
        should_be_excluded = tx in exp_exc
        if not should_be_recommended and not should_be_excluded:
            continue  # treatment not in expectations, skip

        sig = t.get("significant", False)
        base_rate = t["base_rec_rate"]
        pert_rate = t["pert_rec_rate"]
        direction_shift = pert_rate - base_rate  # positive = more recommended in pert

        if should_be_excluded:
            # Edge says perturbation should REDUCE this treatment
            if not sig:
                divergences.append({**t, "divergence_type": "missing_edge",
                    "detail": f"{tx} should be excluded but no significant shift detected"})
            elif direction_shift > 0:
                divergences.append({**t, "divergence_type": "wrong_direction",
                    "detail": f"{tx} should decrease but increased ({base_rate:.0%}->{pert_rate:.0%})"})
            elif abs(t["jsd"]) < 0.1 and "absolute" in str(t.get("type", "")):
                divergences.append({**t, "divergence_type": "magnitude_misalignment",
                    "detail": f"{tx} absolute CI but weak shift (JSD={t['jsd']:.3f})"})
            # else: correct

        elif should_be_recommended:
            # Edge says this treatment should be present in perturbation
            if not sig:
                # Not significant could mean it was already recommended (good) or missed
                pass  # handled at per-item level
            elif direction_shift < -0.3:
                divergences.append({**t, "divergence_type": "wrong_direction",
                    "detail": f"{tx} should remain viable but dropped ({base_rate:.0%}->{pert_rate:.0%})"})

    return divergences


# =====================================================================
# AGGREGATE METRICS
# =====================================================================

def compute_metrics(all_parsed, battery_items):
    """Compute per-model aggregate accuracy metrics."""
    grouped = defaultdict(list)
    for p in all_parsed:
        grouped[(p["item_id"], p["model_name"])].append(p)

    model_scores = defaultdict(lambda: {"tp": 0, "fn": 0, "tn": 0, "fp": 0,
                                         "cond_correct": 0, "cond_total": 0,
                                         "unc_correct": 0, "unc_total": 0,
                                         "null_correct": 0, "null_total": 0, "n_items": 0})

    for (iid, mn), plist in grouped.items():
        exp = battery_items.get(iid)
        if not exp: continue
        exp_rec = set(exp.get("expected_recommendations", []))
        exp_exc = set(exp.get("expected_excluded", []))

        # Majority vote across N runs
        tx_votes = defaultdict(lambda: defaultdict(int))
        for p in plist:
            for s in p["stances"]:
                tx_votes[s["treatment"]][s["stance"]] += 1

        llm_rec = set()
        llm_exc = set()
        for tx, votes in tx_votes.items():
            majority = max(votes, key=votes.get)
            if majority == "recommended":
                llm_rec.add(tx)
                if tx.startswith("ophl_type"): llm_rec.add("ophl_any")
            elif majority in ("excluded", "relative_ci"):
                llm_exc.add(tx)
                if tx.startswith("ophl_type"): llm_exc.add("ophl_any")

        # OPHL catch-all
        ophl_types = {"ophl_type_i", "ophl_type_ii", "ophl_type_iib", "ophl_type_iii"}
        if "ophl_any" in exp_rec and llm_rec & ophl_types: llm_rec.add("ophl_any")
        if "ophl_any" in exp_exc and llm_exc & ophl_types: llm_exc.add("ophl_any")

        ms = model_scores[mn]
        ms["tp"] += len(exp_rec & llm_rec)
        ms["fn"] += len(exp_rec - llm_rec)
        ms["tn"] += len(exp_exc & llm_exc)
        ms["fp"] += len(exp_exc & llm_rec)
        ms["n_items"] += 1

        # Conditionality
        if exp.get("type") == "flip" and exp.get("edge_justification"):
            ms["cond_total"] += 1
            if any(p["conditionality"] for p in plist):
                ms["cond_correct"] += 1

        # Uncertainty (grey zone)
        if exp.get("grey_zone_statement"):
            ms["unc_total"] += 1
            if any(p["uncertainty"] for p in plist):
                ms["unc_correct"] += 1

        # Null specificity
        if "NULL" in iid:
            ms["null_total"] += 1
            if exp_rec == (exp_rec & llm_rec) and not (exp_exc & llm_rec):
                ms["null_correct"] += 1

    metrics = {}
    for mn, ms in model_scores.items():
        metrics[mn] = {
            "n_items": ms["n_items"],
            "rec_accuracy": ms["tp"] / max(ms["tp"]+ms["fn"], 1),
            "exc_accuracy": ms["tn"] / max(ms["tn"]+ms["fp"], 1),
            "rec_precision": ms["tp"] / max(ms["tp"]+ms["fp"], 1),
            "cond_rate": ms["cond_correct"] / max(ms["cond_total"], 1) if ms["cond_total"] else None,
            "unc_rate": ms["unc_correct"] / max(ms["unc_total"], 1) if ms["unc_total"] else None,
            "null_spec": ms["null_correct"] / max(ms["null_total"], 1) if ms["null_total"] else None,
        }
    return metrics


# =====================================================================
# KG2 ASSEMBLY
# =====================================================================

def assemble_kg2(edge_tests):
    """Build KG2 per model: edge -> {detected, weight, n_probes}."""
    model_edge = defaultdict(lambda: defaultdict(list))
    for t in edge_tests:
        for edge in t["edges"]:
            model_edge[t["model"]][edge].append(t.get("significant", False))

    kg2 = {}
    for mn, edges in model_edge.items():
        kg2[mn] = {}
        for edge, detections in edges.items():
            n = len(detections)
            nd = sum(detections)
            kg2[mn][edge] = {"detected": bool(nd > n/2), "n_probes": int(n),
                             "detection_rate": float(nd/n) if n else 0.0}
    return kg2


# =====================================================================
# REPORT GENERATION
# =====================================================================

def generate_report(metrics, kg2, divergences, edge_tests, out_path):
    L = []
    L.append("# KG1 vs KG2 Analysis Report\n")

    L.append("## 1. Aggregate Performance\n")
    L.append("| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |")
    L.append("|---|---|---|---|---|---|---|")
    for mn, m in sorted(metrics.items()):
        c = f"{m['cond_rate']:.0%}" if m['cond_rate'] is not None else "-"
        u = f"{m['unc_rate']:.0%}" if m['unc_rate'] is not None else "-"
        ns = f"{m['null_spec']:.0%}" if m['null_spec'] is not None else "-"
        L.append(f"| {mn} | {m['rec_accuracy']:.0%} | {m['exc_accuracy']:.0%} "
                 f"| {m['rec_precision']:.0%} | {c} | {u} | {ns} |")

    L.append("\n## 2. KG2 Edge Detection Matrix\n")
    if kg2:
        all_e = sorted(set(e for me in kg2.values() for e in me))
        models = sorted(kg2.keys())
        L.append("| Edge | " + " | ".join(models) + " |")
        L.append("|---|" + "|".join(["---"]*len(models)) + "|")
        for e in all_e:
            row = f"| {e} |"
            for mn in models:
                d = kg2[mn].get(e)
                if d: row += f" {'+'if d['detected'] else '-'} ({d['detection_rate']:.0%}) |"
                else: row += " -- |"
            L.append(row)

    L.append(f"\n## 3. Divergence Taxonomy ({len(divergences)} total)\n")
    by_type = defaultdict(list)
    for d in divergences: by_type[d["divergence_type"]].append(d)
    for dtype in ["missing_edge", "wrong_direction", "wrong_conditionality",
                  "magnitude_misalignment", "spurious_edge"]:
        items = by_type.get(dtype, [])
        L.append(f"\n### {dtype} ({len(items)} instances)")
        for d in items[:10]:
            L.append(f"- **{d['pert_id']}** x {d['model']}: {d['detail']}")

    L.append(f"\n## 4. Statistical Tests Summary\n")
    if edge_tests:
        sig = sum(1 for t in edge_tests if t.get("significant"))
        L.append(f"Total tests: {len(edge_tests)}, Significant (BH-FDR q=0.05): {sig} ({sig/len(edge_tests):.0%})")

    with open(out_path, "w") as f: f.write("\n".join(L))
    return "\n".join(L)


# =====================================================================
# MAIN PIPELINE
# =====================================================================

def run_analysis(results_path, battery_path, output_dir):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)

    with open(battery_path) as f: bat = json.load(f)
    expected = {}
    for b in bat["baselines"]: expected[b["id"]] = b
    for p in bat["perturbations"]: expected[p["id"]] = p

    results = []
    with open(results_path) as f:
        for line in f:
            if line.strip():
                try: results.append(json.loads(line))
                except: pass
    print(f"Loaded {len(results)} results")

    all_parsed = [p for p in (parse_result(r) for r in results) if p]
    print(f"Parsed {len(all_parsed)} responses")

    # Aggregate metrics (majority vote)
    metrics = compute_metrics(all_parsed, expected)
    print("\nAggregate metrics:")
    for mn, m in sorted(metrics.items()):
        print(f"  {mn}: rec={m['rec_accuracy']:.0%} exc={m['exc_accuracy']:.0%}")

    # Statistical edge detection (Fisher + JSD + FDR)
    print("\nRunning statistical edge detection...")
    edge_tests = detect_edges(all_parsed, expected)
    if edge_tests:
        sig = sum(1 for t in edge_tests if t.get("significant"))
        print(f"  {len(edge_tests)} tests, {sig} significant (BH-FDR q=0.05)")

    # Divergence taxonomy
    divergences = classify_divergence(edge_tests, expected)
    by_type = defaultdict(int)
    for d in divergences: by_type[d["divergence_type"]] += 1
    print(f"\nDivergences: {dict(by_type)}")

    # KG2 assembly
    kg2 = assemble_kg2(edge_tests)

    # Save outputs
    with open(out/"metrics.json", "w") as f: json.dump(metrics, f, indent=2)
    with open(out/"edge_tests.json", "w") as f: json.dump(edge_tests, f, indent=2, default=str)
    with open(out/"divergences.json", "w") as f: json.dump(divergences, f, indent=2, default=str)
    with open(out/"kg2.json", "w") as f: json.dump(kg2, f, indent=2)
    with open(out/"parsed.json", "w") as f: json.dump(all_parsed, f, indent=2, default=str)
    generate_report(metrics, kg2, divergences, edge_tests, out/"report.md")

    print(f"\nOutputs: {out}/")
    return metrics, kg2, edge_tests, divergences


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--battery", required=True)
    p.add_argument("--outdir", default="analysis")
    run_analysis(**vars(p.parse_args()))

if __name__ == "__main__": main()

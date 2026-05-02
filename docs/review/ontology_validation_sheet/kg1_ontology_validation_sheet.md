# KG1 Ontology Validation Sheet

Purpose: rapid expert review of how each benchmark statement was normalized into variables, value transitions, and treatment consequences.

How to use:
- Work primarily from the CSV if you want to edit directly.
- Mark `expert_review_status` as `approved`, `revise`, or `unclear`.
- Use `expert_validated_variable_mapping` to confirm whether the chosen normalized variable(s) are clinically appropriate.
- Use `expert_validated_treatment_effect` to confirm whether the observed treatment consequence is faithful to the source statement.

Key files:
- CSV: `/Users/albertopaderno/Desktop/github LLM/causal-llm-world-models/docs/review/ontology_validation_sheet/kg1_ontology_validation_sheet.csv`
- Source benchmark: `data/vignettes/vignette_battery.json`
- Source statement extraction: `results/kg1_extraction/ferrari_pdf/statement_rows.json`

## Preview
| Statement | Class | Variables | Recommended | Excluded | Grey zone |
|---|---|---|---|---|---|
| `S10R` | `contextual_selection` | `pre_epiglottic_space, primary_site, thyroid_cartilage_erosion` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_i, ophl_type_ii, ophl_type_iib, surgical_lp` | `tlm` | `False` |
| `S111R` | `selection_factor` | `frailty_status, g8_score` | `concurrent_crt, nonsurgical_lp, rt_alone, total_laryngectomy` | `none` | `False` |
| `S112` | `selection_factor` | `pre_epiglottic_space, primary_site` | `concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy` | `tlm` | `False` |
| `S115` | `selection_factor` | `airway_obstruction, baseline_laryngeal_function, ecog_ps, pretreatment_feeding_tube, pretreatment_tracheostomy, swallowing_status` | `concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy` | `none` | `False` |
| `S116` | `response_adapted` | `ict_response, vc_remobilization_post_ict, vocal_cord_mobility` | `concurrent_crt, nonsurgical_lp` | `rt_alone, total_laryngectomy` | `False` |
| `S119R` | `contextual_selection` | `ict_response, vc_remobilization_post_ict, vocal_cord_mobility` | `concurrent_crt, nonsurgical_lp, total_laryngectomy` | `rt_alone, total_laryngectomy` | `False` |
| `S12` | `contextual_selection` | `pre_epiglottic_space, primary_site` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, total_laryngectomy` | `tlm` | `False` |
| `S120R` | `response_adapted` | `ict_response, vc_remobilization_post_ict, vocal_cord_mobility` | `concurrent_crt, nonsurgical_lp` | `rt_alone, total_laryngectomy` | `False` |
| `S121R` | `response_adapted` | `ict_response, vc_remobilization_post_ict, vocal_cord_mobility` | `concurrent_crt, nonsurgical_lp, total_laryngectomy` | `rt_alone` | `True` |
| `S129` | `response_adapted` | `ict_response, vc_remobilization_post_ict, vocal_cord_mobility` | `total_laryngectomy` | `rt_alone` | `False` |
| `S13` | `contextual_selection` | `cardiopulmonary_function, extralaryngeal_extension, frailty_status, g8_score, neurological_function, t_stage, thyroid_cartilage_outer_cortex` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, total_laryngectomy` | `tlm` | `False` |
| `S14` | `contextual_selection` | `thyroid_cartilage_inner_cortex` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp` | `tlm` | `False` |
| `S15R` | `absolute_contraindication` | `magic_plane_crossing` | `concurrent_crt, nonsurgical_lp, total_laryngectomy` | `ophl_type_i, ophl_type_ii, tlm` | `False` |
| `S16R` | `absolute_contraindication` | `arytenoid_mobility, baseline_laryngeal_function, posterior_laryngeal_involvement` | `concurrent_crt, nonsurgical_lp, total_laryngectomy` | `tlm` | `False` |
| `S17R` | `absolute_contraindication` | `cricoarytenoid_joint_invasion, subglottic_extension` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_iii, surgical_lp` | `ophl_type_ii, tlm` | `False` |
| `S18R` | `fallback_option` | `cricoarytenoid_joint_invasion, subglottic_extension` | `concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_iii, surgical_lp` | `ophl_type_ii, tlm` | `False` |
| `S19R` | `relative_contraindication` | `airway_obstruction, baseline_laryngeal_function, ecog_ps, pretreatment_feeding_tube, pretreatment_tracheostomy, swallowing_status` | `concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy` | `none` | `False` |
| `S20R` | `relative_contraindication` | `cricoid_cartilage_involvement, subglottic_extension` | `concurrent_crt, nonsurgical_lp, total_laryngectomy` | `none` | `False` |
| `S21` | `exception` | `age` | `concurrent_crt, ict_rt, nonsurgical_lp` | `total_laryngectomy` | `False` |
| `S22` | `recommendation` | `laryngeal_exposure` | `nonsurgical_lp, ophl_any, ophl_type_ii, rt_alone, surgical_lp` | `tlm` | `False` |

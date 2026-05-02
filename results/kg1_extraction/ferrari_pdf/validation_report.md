# KG1 Extraction Validation

- Source PDF: `/Users/albertopaderno/Downloads/doc 3.pdf`
- Statement rows extracted: `148`
- Rows meeting 80% table threshold: `135`
- Rows below 80% table threshold: `13`
- Candidate rules generated: `505`
- Benchmark statement IDs: `60`
- Benchmark IDs found in PDF extraction: `60`
- Benchmark IDs with candidate rules: `60`

## Coverage
- Benchmark IDs missing from PDF extraction: `none`
- Benchmark IDs without candidate rules: `none`
- Benchmark IDs below the 80% table threshold: `S47R, S70, SA6`

## Notes
- The PDF table is treated as a source table, not as the sole source of final approval status.
- The article reports 137 approved statements, but the visible PDF table includes rows below the 80% threshold and does not encode the appendix-level revision history required to reconstruct final conference approvals deterministically.
- Validation therefore checks source-table extraction coverage and benchmark alignment, not conference-level adjudication.

## Benchmark Alignment Preview
| Statement ID | Section | Class | Candidate Rules | Families | 80% Table Threshold |
|---|---|---|---|---|---|
| `S10R` | `Transoral surgery` | `contextual_selection` | `12` | `glottic_cT3, supraglottic_cT3` | `True` |
| `S111R` | `Prognostic and predictive factors` | `selection_factor` | `1` | `elderly_frail` | `True` |
| `S112` | `Prognostic and predictive factors` | `selection_factor` | `1` | `supraglottic_cT3` | `True` |
| `S115` | `Prognostic and predictive factors` | `selection_factor` | `3` | `hypopharyngeal, pretreatment_function` | `True` |
| `S116` | `Prognostic and predictive factors` | `response_adapted` | `3` | `post_ict_response` | `True` |
| `S119R` | `Prognostic and predictive factors` | `contextual_selection` | `4` | `post_ict_response` | `True` |
| `S12` | `Transoral surgery` | `contextual_selection` | `2` | `cT4a_selected, hypopharyngeal, supraglottic_cT3` | `True` |
| `S120R` | `Prognostic and predictive factors` | `response_adapted` | `4` | `post_ict_response` | `True` |
| `S121R` | `Prognostic and predictive factors` | `response_adapted` | `2` | `post_ict_response` | `True` |
| `S129` | `Listening to the patient’s preferences: tools and implementation` | `response_adapted` | `4` | `post_ict_response` | `True` |
| `S13` | `Open partial horizontal laryngectomy` | `contextual_selection` | `2` | `elderly_frail` | `True` |
| `S14` | `Open partial horizontal laryngectomy` | `contextual_selection` | `2` | `glottic_cT3` | `True` |
| `S15R` | `Open partial horizontal laryngectomy` | `absolute_contraindication` | `2` | `cT4a_selected` | `True` |
| `S16R` | `Open partial horizontal laryngectomy` | `absolute_contraindication` | `2` | `glottic_cT3` | `True` |
| `S17R` | `Open partial horizontal laryngectomy` | `absolute_contraindication` | `2` | `glottic_cT3` | `True` |
| `S18R` | `Open partial horizontal laryngectomy` | `fallback_option` | `2` | `glottic_cT3` | `True` |
| `S19R` | `Radiotherapy and chemotherapy` | `relative_contraindication` | `6` | `hypopharyngeal, pretreatment_function` | `True` |
| `S20R` | `Radiotherapy and chemotherapy` | `relative_contraindication` | `2` | `pretreatment_function` | `True` |
| `S21` | `Radiotherapy and chemotherapy` | `exception` | `2` | `pretreatment_function` | `True` |
| `S22` | `Radiotherapy and chemotherapy` | `recommendation` | `4` | `glottic_cT2` | `True` |
| `S23R` | `Radiotherapy and chemotherapy` | `contextual_selection` | `2` | `glottic_cT2, glottic_cT3` | `True` |
| `S24R` | `Radiotherapy and chemotherapy` | `relative_contraindication` | `3` | `cT4a_selected, supraglottic_cT3` | `True` |
| `S27` | `Radiotherapy and chemotherapy` | `exception` | `2` | `glottic_cT3` | `True` |
| `S28` | `Radiotherapy and chemotherapy` | `contextual_selection` | `2` | `glottic_cT3` | `True` |
| `S30` | `Radiotherapy and chemotherapy` | `contextual_selection` | `4` | `post_ict_response` | `True` |

# Family-Stratified Supplementary Analysis

- Families represented: `10`
- Union of family-level gold edges: `57`
- One additional benchmark edge (`S80`) functions as a shared null-control edge rather than a family-specific directional edge; together these reconcile to the full 58-edge benchmark.
- Note: `cT4a_unselected` is retained as baseline/null-control context and therefore carries no directional gold-edge denominator.

| Family | Model | Gold edges | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | SID rate | Mean causal JSD | Fraction above global null 95th |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cT4a_selected | DeepSeek-R1 | 10 | 50.0% | 71.4% | 28.6% | 80.0% | 26.7% | 0.077 | 1.9% |
| cT4a_selected | Kimi K2.5 | 10 | 50.0% | 100.0% | 0.0% | 100.0% | 26.7% | 0.080 | 3.6% |
| cT4a_selected | Qwen3-Next-80B-A3B-Instruct | 10 | 20.0% | 40.0% | 60.0% | 50.0% | 21.4% | 0.072 | 6.4% |
| cT4a_selected | Mistral-Small-24B | 10 | 0.0% | 0.0% | 100.0% | NA | 21.4% | 0.102 | 11.5% |
| cT4a_selected | Gemma 4 31B | 10 | 0.0% | NA | NA | NA | 21.4% | 0.125 | 13.3% |
| cT4a_selected | Llama 3.1-8B | 10 | 0.0% | NA | NA | NA | 21.4% | 0.023 | 0.0% |
| cT4a_unselected | DeepSeek-R1 | 0 | NA | NA | NA | NA | NA | NA | NA |
| cT4a_unselected | Kimi K2.5 | 0 | NA | NA | NA | NA | NA | NA | NA |
| cT4a_unselected | Qwen3-Next-80B-A3B-Instruct | 0 | NA | NA | NA | NA | NA | NA | NA |
| cT4a_unselected | Mistral-Small-24B | 0 | NA | NA | NA | NA | NA | NA | NA |
| cT4a_unselected | Gemma 4 31B | 0 | NA | NA | NA | NA | NA | NA | NA |
| cT4a_unselected | Llama 3.1-8B | 0 | NA | NA | NA | NA | NA | NA | NA |
| cisplatin_eligibility | DeepSeek-R1 | 8 | 100.0% | 66.7% | 33.3% | 75.0% | 11.4% | 0.158 | 15.1% |
| cisplatin_eligibility | Kimi K2.5 | 8 | 100.0% | 100.0% | 0.0% | 75.0% | 20.0% | 0.243 | 31.5% |
| cisplatin_eligibility | Qwen3-Next-80B-A3B-Instruct | 8 | 87.5% | 100.0% | 0.0% | 85.7% | 11.1% | 0.161 | 19.0% |
| cisplatin_eligibility | Mistral-Small-24B | 8 | 100.0% | 100.0% | 0.0% | 50.0% | 11.1% | 0.190 | 23.2% |
| cisplatin_eligibility | Gemma 4 31B | 8 | 12.5% | 50.0% | 50.0% | 0.0% | 17.4% | 0.122 | 10.6% |
| cisplatin_eligibility | Llama 3.1-8B | 8 | 25.0% | 100.0% | 0.0% | 0.0% | 30.2% | 0.084 | 1.4% |
| elderly_frail | DeepSeek-R1 | 6 | 83.3% | 62.5% | 37.5% | 40.0% | 25.0% | 0.192 | 21.4% |
| elderly_frail | Kimi K2.5 | 6 | 83.3% | 50.0% | 50.0% | 40.0% | 16.7% | 0.284 | 45.5% |
| elderly_frail | Qwen3-Next-80B-A3B-Instruct | 6 | 33.3% | 66.7% | 33.3% | 0.0% | 18.2% | 0.075 | 7.7% |
| elderly_frail | Mistral-Small-24B | 6 | 66.7% | 57.1% | 42.9% | 50.0% | 18.2% | 0.161 | 33.3% |
| elderly_frail | Gemma 4 31B | 6 | 83.3% | 62.5% | 37.5% | 20.0% | 37.5% | 0.153 | 17.6% |
| elderly_frail | Llama 3.1-8B | 6 | 0.0% | NA | NA | NA | 10.0% | 0.098 | 0.0% |
| glottic_cT2 | DeepSeek-R1 | 6 | 16.7% | 100.0% | 0.0% | 100.0% | 10.7% | 0.086 | 7.5% |
| glottic_cT2 | Kimi K2.5 | 6 | 50.0% | 100.0% | 0.0% | 66.7% | 14.3% | 0.123 | 14.0% |
| glottic_cT2 | Qwen3-Next-80B-A3B-Instruct | 6 | 16.7% | 100.0% | 0.0% | 100.0% | 16.7% | 0.078 | 7.7% |
| glottic_cT2 | Mistral-Small-24B | 6 | 16.7% | 100.0% | 0.0% | 100.0% | 12.5% | 0.068 | 2.7% |
| glottic_cT2 | Gemma 4 31B | 6 | 50.0% | 75.0% | 25.0% | 33.3% | 16.7% | 0.140 | 13.9% |
| glottic_cT2 | Llama 3.1-8B | 6 | 16.7% | 100.0% | 0.0% | 100.0% | 16.7% | 0.047 | 2.8% |
| glottic_cT3 | DeepSeek-R1 | 19 | 68.4% | 81.2% | 18.8% | 100.0% | 11.5% | 0.147 | 20.4% |
| glottic_cT3 | Kimi K2.5 | 19 | 78.9% | 75.0% | 25.0% | 53.3% | 19.0% | 0.184 | 21.9% |
| glottic_cT3 | Qwen3-Next-80B-A3B-Instruct | 19 | 63.2% | 85.7% | 14.3% | 91.7% | 10.4% | 0.087 | 12.1% |
| glottic_cT3 | Mistral-Small-24B | 19 | 57.9% | 91.7% | 8.3% | 100.0% | 11.8% | 0.103 | 12.9% |
| glottic_cT3 | Gemma 4 31B | 19 | 36.8% | 70.0% | 30.0% | 85.7% | 18.4% | 0.112 | 8.6% |
| glottic_cT3 | Llama 3.1-8B | 19 | 21.1% | 80.0% | 20.0% | 75.0% | 19.7% | 0.070 | 5.9% |
| hypopharyngeal | DeepSeek-R1 | 4 | 75.0% | 100.0% | 0.0% | 100.0% | 0.0% | 0.148 | 23.1% |
| hypopharyngeal | Kimi K2.5 | 4 | 50.0% | 100.0% | 0.0% | 100.0% | 0.0% | 0.092 | 6.1% |
| hypopharyngeal | Qwen3-Next-80B-A3B-Instruct | 4 | 0.0% | NA | NA | NA | 0.0% | 0.089 | 13.3% |
| hypopharyngeal | Mistral-Small-24B | 4 | 25.0% | 20.0% | 80.0% | 0.0% | 0.0% | 0.066 | 18.2% |
| hypopharyngeal | Gemma 4 31B | 4 | 25.0% | 100.0% | 0.0% | 100.0% | 0.0% | 0.111 | 9.5% |
| hypopharyngeal | Llama 3.1-8B | 4 | 0.0% | NA | NA | NA | 0.0% | 0.045 | 0.0% |
| post_ict_response | DeepSeek-R1 | 11 | 45.5% | 35.7% | 64.3% | 80.0% | 41.2% | 0.155 | 19.0% |
| post_ict_response | Kimi K2.5 | 11 | 100.0% | 57.9% | 42.1% | 90.9% | 17.6% | 0.202 | 27.1% |
| post_ict_response | Qwen3-Next-80B-A3B-Instruct | 11 | 18.2% | 14.3% | 85.7% | 50.0% | 29.4% | 0.149 | 27.4% |
| post_ict_response | Mistral-Small-24B | 11 | 9.1% | 25.0% | 75.0% | 100.0% | 29.4% | 0.097 | 8.9% |
| post_ict_response | Gemma 4 31B | 11 | 81.8% | 75.0% | 25.0% | 100.0% | 11.8% | 0.151 | 20.5% |
| post_ict_response | Llama 3.1-8B | 11 | 18.2% | 40.0% | 60.0% | 50.0% | 29.4% | 0.117 | 3.8% |
| pretreatment_function | DeepSeek-R1 | 5 | 80.0% | 66.7% | 33.3% | 75.0% | 0.0% | 0.148 | 17.7% |
| pretreatment_function | Kimi K2.5 | 5 | 60.0% | 50.0% | 50.0% | 100.0% | 0.0% | 0.164 | 17.7% |
| pretreatment_function | Qwen3-Next-80B-A3B-Instruct | 5 | 20.0% | 50.0% | 50.0% | 100.0% | 0.0% | 0.103 | 17.5% |
| pretreatment_function | Mistral-Small-24B | 5 | 20.0% | 50.0% | 50.0% | 0.0% | 0.0% | 0.109 | 9.4% |
| pretreatment_function | Gemma 4 31B | 5 | 20.0% | 100.0% | 0.0% | 100.0% | 0.0% | 0.097 | 8.7% |
| pretreatment_function | Llama 3.1-8B | 5 | 40.0% | 100.0% | 0.0% | 50.0% | 0.0% | 0.175 | 8.2% |
| supraglottic_cT3 | DeepSeek-R1 | 5 | 60.0% | 75.0% | 25.0% | 100.0% | 13.0% | 0.124 | 13.6% |
| supraglottic_cT3 | Kimi K2.5 | 5 | 60.0% | 75.0% | 25.0% | 100.0% | 17.4% | 0.124 | 7.7% |
| supraglottic_cT3 | Qwen3-Next-80B-A3B-Instruct | 5 | 0.0% | 0.0% | 100.0% | NA | 21.7% | 0.062 | 5.9% |
| supraglottic_cT3 | Mistral-Small-24B | 5 | 0.0% | 0.0% | 100.0% | NA | 17.4% | 0.112 | 11.4% |
| supraglottic_cT3 | Gemma 4 31B | 5 | 0.0% | NA | NA | NA | 17.4% | 0.080 | 0.0% |
| supraglottic_cT3 | Llama 3.1-8B | 5 | 0.0% | NA | NA | NA | 17.4% | 0.027 | 0.0% |

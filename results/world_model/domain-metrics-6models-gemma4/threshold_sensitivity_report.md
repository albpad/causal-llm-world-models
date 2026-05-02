# Threshold Sensitivity Analysis

This supplementary analysis evaluates how the main detection-dependent metrics vary across threshold choices.
The locked default outputs are preserved; the sweeps are used only as robustness checks.

## Qualitative Summary
- Across all soft-threshold settings, the highest soft recall remained with `Kimi K2.5`.
- `DeepSeek-R1` retained the strongest soft-edge direction accuracy across the soft-threshold sweep (77.4% to 78.9%).
- `Kimi K2.5` had the highest hard recall in `6` of `9` hard-threshold configurations.
- `Llama 3.1-8B` remained the weakest locked-default coverage model; discriminability is unchanged because SNR and detection power are threshold-independent.

## Soft-Threshold Sweep
| Model | Threshold | Soft recall | Soft precision | Soft FDR | Soft-edge direction accuracy |
|---|---:|---:|---:|---:|---:|
| DeepSeek-R1 | 0.15 | 65.5% | 61.3% | 38.7% | 78.9% |
| DeepSeek-R1 | 0.25 | 62.1% | 60.0% | 40.0% | 77.8% |
| DeepSeek-R1 | 0.35 | 53.4% | 56.4% | 43.6% | 77.4% |
| Kimi K2.5 | 0.15 | 74.1% | 66.2% | 33.8% | 67.4% |
| Kimi K2.5 | 0.25 | 74.1% | 66.2% | 33.8% | 67.4% |
| Kimi K2.5 | 0.35 | 72.4% | 65.6% | 34.4% | 66.7% |
| Qwen3-Next-80B-A3B-Instruct | 0.15 | 50.0% | 59.2% | 40.8% | 79.3% |
| Qwen3-Next-80B-A3B-Instruct | 0.25 | 39.7% | 53.5% | 46.5% | 73.9% |
| Qwen3-Next-80B-A3B-Instruct | 0.35 | 25.9% | 42.9% | 57.1% | 73.3% |
| Mistral-Small-24B | 0.15 | 46.6% | 64.3% | 35.7% | 74.1% |
| Mistral-Small-24B | 0.25 | 43.1% | 62.5% | 37.5% | 72.0% |
| Mistral-Small-24B | 0.35 | 29.3% | 53.1% | 46.9% | 70.6% |
| Gemma 4 31B | 0.15 | 46.6% | 69.2% | 30.8% | 74.1% |
| Gemma 4 31B | 0.25 | 41.4% | 66.7% | 33.3% | 70.8% |
| Gemma 4 31B | 0.35 | 39.7% | 65.7% | 34.3% | 73.9% |
| Llama 3.1-8B | 0.15 | 17.2% | 71.4% | 28.6% | 50.0% |
| Llama 3.1-8B | 0.25 | 17.2% | 71.4% | 28.6% | 50.0% |
| Llama 3.1-8B | 0.35 | 15.5% | 69.2% | 30.8% | 44.4% |

## Hard-Threshold Sweep
| Model | Rate threshold | JSD threshold | Hard recall | Hard precision | Hard FDR | Hard-edge direction accuracy |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek-R1 | 0.40 | 0.05 | 19.0% | 31.4% | 68.6% | 72.7% |
| DeepSeek-R1 | 0.40 | 0.10 | 19.0% | 31.4% | 68.6% | 72.7% |
| DeepSeek-R1 | 0.40 | 0.15 | 19.0% | 31.4% | 68.6% | 72.7% |
| DeepSeek-R1 | 0.50 | 0.05 | 15.5% | 27.3% | 72.7% | 66.7% |
| DeepSeek-R1 | 0.50 | 0.10 | 15.5% | 27.3% | 72.7% | 66.7% |
| DeepSeek-R1 | 0.50 | 0.15 | 15.5% | 27.3% | 72.7% | 66.7% |
| DeepSeek-R1 | 0.60 | 0.05 | 8.6% | 17.2% | 82.8% | 60.0% |
| DeepSeek-R1 | 0.60 | 0.10 | 8.6% | 17.2% | 82.8% | 60.0% |
| DeepSeek-R1 | 0.60 | 0.15 | 8.6% | 17.2% | 82.8% | 60.0% |
| Kimi K2.5 | 0.40 | 0.05 | 27.6% | 42.1% | 57.9% | 68.8% |
| Kimi K2.5 | 0.40 | 0.10 | 27.6% | 42.1% | 57.9% | 68.8% |
| Kimi K2.5 | 0.40 | 0.15 | 27.6% | 42.1% | 57.9% | 68.8% |
| Kimi K2.5 | 0.50 | 0.05 | 17.2% | 31.2% | 68.8% | 80.0% |
| Kimi K2.5 | 0.50 | 0.10 | 17.2% | 31.2% | 68.8% | 80.0% |
| Kimi K2.5 | 0.50 | 0.15 | 17.2% | 31.2% | 68.8% | 80.0% |
| Kimi K2.5 | 0.60 | 0.05 | 5.2% | 12.0% | 88.0% | 33.3% |
| Kimi K2.5 | 0.60 | 0.10 | 5.2% | 12.0% | 88.0% | 33.3% |
| Kimi K2.5 | 0.60 | 0.15 | 5.2% | 12.0% | 88.0% | 33.3% |
| Qwen3-Next-80B-A3B-Instruct | 0.40 | 0.05 | 12.1% | 25.9% | 74.1% | 57.1% |
| Qwen3-Next-80B-A3B-Instruct | 0.40 | 0.10 | 12.1% | 25.9% | 74.1% | 57.1% |
| Qwen3-Next-80B-A3B-Instruct | 0.40 | 0.15 | 10.3% | 23.1% | 76.9% | 66.7% |
| Qwen3-Next-80B-A3B-Instruct | 0.50 | 0.05 | 5.2% | 13.0% | 87.0% | 0.0% |
| Qwen3-Next-80B-A3B-Instruct | 0.50 | 0.10 | 5.2% | 13.0% | 87.0% | 0.0% |
| Qwen3-Next-80B-A3B-Instruct | 0.50 | 0.15 | 3.4% | 9.1% | 90.9% | 0.0% |
| Qwen3-Next-80B-A3B-Instruct | 0.60 | 0.05 | 1.7% | 4.8% | 95.2% | 0.0% |
| Qwen3-Next-80B-A3B-Instruct | 0.60 | 0.10 | 1.7% | 4.8% | 95.2% | 0.0% |
| Qwen3-Next-80B-A3B-Instruct | 0.60 | 0.15 | 1.7% | 4.8% | 95.2% | 0.0% |
| Mistral-Small-24B | 0.40 | 0.05 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.40 | 0.10 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.40 | 0.15 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.50 | 0.05 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.50 | 0.10 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.50 | 0.15 | 3.4% | 11.8% | 88.2% | 50.0% |
| Mistral-Small-24B | 0.60 | 0.05 | 1.7% | 6.2% | 93.8% | 0.0% |
| Mistral-Small-24B | 0.60 | 0.10 | 1.7% | 6.2% | 93.8% | 0.0% |
| Mistral-Small-24B | 0.60 | 0.15 | 1.7% | 6.2% | 93.8% | 0.0% |
| Gemma 4 31B | 0.40 | 0.05 | 19.0% | 47.8% | 52.2% | 63.6% |
| Gemma 4 31B | 0.40 | 0.10 | 19.0% | 47.8% | 52.2% | 63.6% |
| Gemma 4 31B | 0.40 | 0.15 | 19.0% | 47.8% | 52.2% | 63.6% |
| Gemma 4 31B | 0.50 | 0.05 | 15.5% | 42.9% | 57.1% | 66.7% |
| Gemma 4 31B | 0.50 | 0.10 | 15.5% | 42.9% | 57.1% | 66.7% |
| Gemma 4 31B | 0.50 | 0.15 | 15.5% | 42.9% | 57.1% | 66.7% |
| Gemma 4 31B | 0.60 | 0.05 | 6.9% | 25.0% | 75.0% | 25.0% |
| Gemma 4 31B | 0.60 | 0.10 | 6.9% | 25.0% | 75.0% | 25.0% |
| Gemma 4 31B | 0.60 | 0.15 | 6.9% | 25.0% | 75.0% | 25.0% |
| Llama 3.1-8B | 0.40 | 0.05 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.40 | 0.10 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.40 | 0.15 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.50 | 0.05 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.50 | 0.10 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.50 | 0.15 | 1.7% | 20.0% | 80.0% | 0.0% |
| Llama 3.1-8B | 0.60 | 0.05 | 0.0% | 0.0% | 100.0% | 0.0% |
| Llama 3.1-8B | 0.60 | 0.10 | 0.0% | 0.0% | 100.0% | 0.0% |
| Llama 3.1-8B | 0.60 | 0.15 | 0.0% | 0.0% | 100.0% | 0.0% |

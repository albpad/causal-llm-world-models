# Supplementary Table S1. Query Settings for the Canonical Analysis Dataset

| Model | Provider endpoint | Registry model ID | Observed model ID(s) in retained dataset | Temperature | Max tokens | Reasoning effort | Runs per item |
|---|---|---|---|---:|---:|---|---:|
| DeepSeek-R1 | Together.ai chat-completions API | deepseek-ai/DeepSeek-R1 | deepseek-ai/DeepSeek-R1 (1320) | 0.6 | 8192 | default | 15 |
| Kimi K2.5 | Together.ai chat-completions API | moonshotai/Kimi-K2.5 | moonshotai/Kimi-K2.5 (1320) | 1.0 | 4096 | default | 15 |
| Qwen3-Next-80B-A3B-Instruct | Together.ai chat-completions API | Qwen/Qwen3-Next-80B-A3B-Instruct | Qwen/Qwen3-Next-80B-A3B-Instruct (1320) | 0.6 | 4096 | default | 15 |
| Mistral-Small-24B | Together.ai chat-completions API | mistralai/Mistral-Small-24B-Instruct-2501 | mistralai/Mistral-Small-24B-Instruct-2501 (1320) | 0.6 | 4096 | default | 15 |
| Gemma 4 31B | Together.ai chat-completions API | google/gemma-4-31B-it | google/gemma-4-31B-it (1320) | 0.6 | 1024 | default | 15 |
| Llama 3.1-8B | Together.ai chat-completions API | meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo | meta-llama/Meta-Llama-3-8B-Instruct-Lite (60); meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo (1260) | 0.6 | 4096 | default | 15 |

Temperatures were fixed within model and were not tuned per vignette or per family.

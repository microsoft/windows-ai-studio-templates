# Qwen3-0.6B GenAI Bundle

These are Model Lab invocation recipes, not WinMLBuildConfig documents.
WinML CLI 0.5.0 rejects `-c/--config` for optimized GenAI bundle builds.
Foundry Toolkit's `run_wmk_build.py` recognizes `recipe_type: genai-bundle`
and translates the selected recipe into:

```text
winml build -m Qwen/Qwen3-0.6B -o <output> --export-type optimized --ep <ep> --device <device> --precision w8a16
```

The recipe pins the model, execution provider, device, and transformer precision.
The CLI's registered Qwen3 recipe builds context and iterator graphs at w8a16,
embeddings at fp32 on CPU, and lm_head at w4a32 on CPU. It assembles the graphs,
external weights, tokenizer, and genai_config.json into the output directory.
Bundle settings and component generation remain owned by WinML CLI, not copied
into an unsupported WinMLBuildConfig schema.

Source: `microsoft/winml-cli`, branch `release/v0.5.0`, commit
`815331644db7bcdee3e73882e7fd6f2143d74425`.
Workflow: https://microsoft.github.io/winml-cli/latest/samples/qwen3-genai-bundle/

Supported targets come from that commit's Qwen3 GenaiBundleRecipe registration:
CPU/CPU, QNN/NPU, VitisAI/NPU, OpenVINO/NPU, and OpenVINO/GPU.
The CPU bundle was built locally; other targets require compatible hardware,
drivers, and execution providers and have not been validated on this CPU host.

Benchmark the whole output directory, not one component graph:

WinML CLI 0.5.0 supports GenAI text generation through `perf --runtime ort-genai`,
but its `eval` command does not support the ort-genai runtime. Model Lab rejects
accuracy evaluation of these bundles rather than evaluating a component graph.

```text
winml perf -m <output> --runtime ort-genai --device cpu --ep cpu --max-new-tokens 20 --prompt "What is the capital of France?"
```
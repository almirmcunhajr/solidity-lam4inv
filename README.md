# solidity-lam4inv

`solidity-lam4inv` adapts [LaM4Inv](https://github.com/SoftWiser-group/LaM4Inv/tree/main) to target Solidity smart contracts. The
implementation reuses the LaM4Inv's framework but supplies Solidity-aware front-ends, integrates an on-demand adaptation of
[Code2Inv](https://github.com/PL-ML/code2inv)'s verification-condition (VC) generator, and augments the loop with a configurable
pipeline of cooperating large-language-model models. The result is an invariant synthesiser for function-scoped `while` loops that
combines large-language-model guidance with symbolic reasoning tailored to the Ethereum Virtual Machine (EVM).

## Key features

- **Solidity-centric invariant search** – extracts the function loop targeted by each benchmark and emits candidates as
  Solidity `assert` statements.
- **Multi-model LLM pipeline** – orchestrates a chain of LLM models that share conversation state, increase presence
  penalties for predicates that repeatedly fail, and can be ordered to, for example, try a cheaper model before escalating to a
  stronger one.
- **On-demand VC generation** – adapts Code2Inv's VC builder with Solidity bindings so initiation, consecution, and safety
  obligations are generated during the run instead of relying on pre-built templates.
- **EVM-aware predicate filtering** – invokes a Solidity bounded model checker during predicate filtering so blatantly spurious
  clauses are eliminated before the SMT-based verifier discharges the VC obligations, with counterexamples feeding back into
  later prompts.
- **Benchmark parity** – automatically cross-checks every inferred invariant against the canonical LaM4Inv templates bundled in
  `benchmarks/cross-checks-templates/` to ensure compatibility with the upstream suite.

## Supported Solidity loop shape

The tool analyses a single loop per function: the `while` loop enclosed in the function targeted by the harness.
The function must follow this shape:

1. All variables must be integers, local to the function, and declared either as parameters or as local variables.
2. Assignments or `require` statements modelling the preconditions for entering the loop.
3. A single `while` loop.
4. An assert statement must appear immediately after the while loop (it may be nested under conditionals) and should express a property that the inferred loop invariant is intended to prove.

## Invariant synthesis pipeline

1. **Prompt construction** – gather Solidity context, previously failed invariants, and the VC obligations for the active loop.
2. **Presence-penalty shaping** – record each failed predicate and raise the presence penalty on later prompts for models that
   support it so repeated mistakes become less likely.
3. **Predicate splitting and filtering** – expand `assert(...)` answers into atomic predicates, discard obviously spurious ones
   with the Solidity bounded model checker, and build the conjecture set for SMT solving.
4. **VC generation and SMT solving** – instantiate the Solidity-aware VC generator, check initiation/consecution/safety with Z3,
   and turn satisfying assignments into counterexamples when a predicate fails.

## Project layout

```
.
├── benchmarks/                 # Solidity benchmarks, expected results, and VC reference templates
│   ├── code/                   # Solidity contracts evaluated by the harness
│   ├── cross-checks-templates/ # Canonical LaM4Inv VCs templates used for cross-checks
│   └── results/                # Output directory populated by benchmark runs
├── src/
│   ├── bmc/                    # Abstract BMC interface plus the solc-based EVM implementation
│   ├── code_handler/           # Language-agnostic handler interfaces and Solidity-specific implementations
│   ├── generator/              # LLM-facing invariant generator orchestrator
│   ├── inv_smt_solver/         # SMT workflow around VC generation and counterexample extraction
│   ├── llm/                    # Chat abstractions alongside the OpenAI-backed implementations
│   ├── predicate_filtering/    # Predicate filtering pipeline that cooperates with the BMC interface
│   ├── smt/                    # Solver interface and the Z3-backed implementation
│   ├── utils/                  # Miscellaneous helpers (process handling, formatting, etc.)
│   ├── vc/                     # VC generator interfaces plus the Solidity-aware builder
│   ├── config.py               # Runtime configuration (paths, timeouts, environment lookup)
│   ├── main.py                 # CLI entry point for single-run and benchmark execution
│   └── runner.py               # Pipeline orchestrator coordinating LLM, SMT, and BMC components
├── pyproject.toml              # Poetry configuration and project metadata
├── poetry.lock                 # Locked dependency versions
└── README.md
```

## Installation

1. Install Python 3.10 or 3.11 and [Poetry](https://python-poetry.org/docs/).
2. Install the Solidity compiler (`solc`) and ensure it is on your `PATH`. Override the location by editing
   [`src/config.py`](src/config.py).
3. Install Python dependencies:

   ```bash
   poetry install
   ```

## Configuration

The pipeline currently targets OpenAI chat models. Provide credentials through the environment:

- `OPENAI_API_KEY`

The CLI reads a `.env` file automatically, so the key can reside in `./.env` instead of being exported manually.

## Usage

### Run invariant synthesis on a single function loop

```bash
poetry run python src/main.py \
  --file example.sol \
  --contract-name ExampleContract \
  --function-name exampleFunction \
  --pipeline "gpt-5-mini, 300; gpt-5, 600" \
  --smt-timeout 50 \
  --bmc-timeout 5 \
  --bmc-max-steps 10 \
  --output result.txt
```

- `--file` – Solidity contract following the supported function-loop shape. The runner isolates its function loop and
  synthesises an invariant for that scope.
- `--contract-name` – name of the contract containing the target function.
- `--function-name` – name of the function containing the target `while` loop.
- `--smt-timeout` – per-check timeout (in seconds) for the SMT solver.
- `--bmc-timeout` – per-check timeout (in seconds) for the bounded model checker.
- `--bmc-max-steps` – maximum number of loop unrollings performed by the bounded model checker.
- `--pipeline` – semicolon-separated `model, timeout` pairs looked up in `ChatGPTModel` inside [`src/llm/openai.py`](src/llm/openai.py).
  Models share chat history, inherit failure statistics, and can, for example, start on an inexpensive model before escalating
  to a stronger option if you order them that way.
- `--max-chat-interactions` – caps the number of back-and-forth turns across the configured pipeline (`-1` disables the cap).
- `--output` – path to the generated invariant and logs (`stdout` if omitted).
- `--log-level` – standard Python logging level.

### Run the benchmark suite

```bash
mkdir -p benchmarks/results
poetry run python src/main.py --benchmarks 1,10
```

The runner executes each benchmark ID in the provided range, regenerates the Solidity VC obligations during the run, and writes
successful invariants to `benchmarks/results/<id>.txt`. Every benchmark execution also cross-checks the freshly generated VC
with the canonical template stored under `benchmarks/cross-checks-templates/`; mismatches or counterexamples are reported on the
console.

## Development tips

- Increase `--smt-timeout` or `--bmc-timeout` for larger contracts that need additional solver time.
- Adjust `--bmc-max-steps` when the bounded model checker requires deeper exploration to validate predicates.
- Use `--log-level DEBUG` to inspect LLM prompts, solver exchanges, and counterexamples when debugging.
- When adding benchmarks, mirror the folder structure under `benchmarks/code/` and supply the corresponding template under
  `benchmarks/cross-checks-templates/` so the mandatory cross-check can run.

## License

This repository is released for research and experimentation. Contact the authors for licensing beyond personal or academic use.

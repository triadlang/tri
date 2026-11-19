# triadlang-programs

The TriadLang language and its programs. Part of the [TriadLang](https://github.com/triadlang/triadlang) project, separated out so the language itself — the lexer, parser, compiler, interpreter, CLI, and the `.tri` programs you can write and run — lives in one place.

```
i·ℏ·∂_t Ψ = [-ℏ²/(2m)∇² + V_ext + Λ|Ψ|² + V_mem + α(-Δ)^(σ/2) - iΓ]Ψ + η
```

TriadLang is a language whose runtime is the Triad equation. P1 (kinetic and fractional dispersion), P2 (cubic and memory), P3 (dissipation and FDT noise) stay active together. A `.tri` file declares substrates, couples them, evolves the field, and reads observables.

---

## Install

```bash
pip install -e .
```

This installs a `triad` command on your path.

```bash
triad run programs/basic/hello.tri
# Hello from TriadLang
```

---

## A first program

```python
# programs/triad/anti_collapse.tri

@T(18.0)
reg a : anti_collapse = 4;
reg b : anti_collapse = 4;
ring(a, b) kappa=-2.5 for T=18.0;
OBSERVE a k_star, crystallinity, peak, atom_count;
OBSERVE b k_star, crystallinity, peak, atom_count;
```

Running it:

```bash
$ triad run programs/triad/anti_collapse.tri
a = { k_star=6.2832, crystallinity=0.9631, peak=0.6737, atom_count=10.0000 }
b = { k_star=6.2832, crystallinity=0.9631, peak=0.6737, atom_count=10.0000 }
```

What this does: declares two substrates `a` and `b`, both bound to the `anti_collapse` regime (strong attractive cubic + fractional dispersion + memory feedback). The `ring` statement couples them bidirectionally. The runtime evolves both fields through P1+P2+P3 for T=18.0. The `OBSERVE` reads four observables from the final field state. The structure that emerges is whatever the equation arrives at — nothing imposed.

---

## The language

| Construct | Role |
|---|---|
| `let x = 10;` | Variable binding |
| `fn f(x, y) { return x + y; }` | Function definition |
| `class Foo { ... }` | Class definition |
| `if cond { ... } else { ... }` | Conditional |
| `for x in xs { ... }` | Iteration |
| `while cond { ... }` | Loop |
| `match v { case A: ... }` | Pattern matching |
| `import triad.nn as nn;` | Module import |
| `f"x = {x:.4f}"` | f-strings with format specs |
| `try { ... } catch e { ... }` | Exception handling |
| `try { ... } catch e { ... }` | Generators with `yield` |
| `@T(value)` | Triad-time annotation |
| `reg name : regime = N;` | Declare a substrate bound to a regime |
| `couple a -> b kappa=X for T=Y;` | One-way coupling |
| `pair(a, b) kappa=X for T=Y;` | Bidirectional coupling |
| `ring(a, b, c) kappa=X for T=Y;` | Ring topology |
| `OBSERVE name metrics;` | Read observables from the evolved field |

The CLI:

```bash
triad run <file.tri>             # parse, compile, execute
triad check <file.tri>           # type check
triad compile <file.tri> --native -o out   # compile to C and link
triad repl                       # interactive REPL
triad fmt <file.tri>             # format
triad solve --regime B0 --N 128  # run a regime from the command line
triad observables <file.npy>     # compute observables on a saved field
triad docgen <file|dir>          # generate documentation
triad doctor                     # check installation health
```

---

## Programs in this repo

`programs/` is organized by what each program demonstrates:

| Folder | Programs | What they show |
|---|---|---|
| `basic/` | 11 | Language features (functions, loops, types, modules, JSON, files, f-strings) |
| `triad/` | 7 | The field substrates: anti_collapse, calibration, curriculum, custom potentials, memory recall, observables, SAT |
| `solver/` | 7 | Solver-level programs: ablation, benchmark, convergence, native integration, speed |
| `crossdomain/` | 9 | Same equation, different regimes: neuro+climate, origin-of-life, finance+materials, cosmos, the grand tournament |
| `ml/` | 8 | Neural networks via `triad.nn`: tensor ops, MLP, Conv1d, transformer, XOR, GGUF loading |
| `llm/` | 2 | Language model framework: mock runtime, full TriadLM training |
| `quantum/` | 1 | Bell state via `triad.qubits` |
| `games/` | 1 | Lotka-Volterra predator-prey simulation |
| `verification/` | 1 | FDT relation verification |
| `interop/` | 6 | Boundary programs: numpy, click, flask, headless |

Run any of them with `triad run programs/<folder>/<file>.tri`.

---

## How a .tri file becomes a running program

1. **Lex** (`src/triadlang/frontend/lexer_universal.py`) — source becomes a token stream
2. **Parse** (`src/triadlang/frontend/parser_universal.py`) — tokens become an AST (`ast_nodes.Module`)
3. **Type check** (`src/triadlang/compiler/typecheck_universal.py`) — optional, runs on `triad check`
4. **Compile** (`src/triadlang/runtime/compiler_runtime.py`) — AST is lowered to Python source, which is `compile()`d to a code object
5. **Execute** — the code object runs in an environment that provides `_tri_print`, `solver_solve`, MultiRuntime helpers, observables, the `triad` stdlib module, and so on

For `triad compile --native`, the path forks at step 4: `compiler/lower.py` produces IR, `compiler/c_codegen.py` emits C, the C is compiled and linked against the native runtime (`triad_rt.h`, FFTW3, Boehm GC).

---

## Implementation notes

The implementation is in `src/triadlang/`. Subpackages:

| Subpackage | Lines | Role |
|---|---|---|
| `frontend/` | ~5,000 | Lexer (legacy + universal), parser, AST nodes, diagnostics |
| `compiler/` | ~6,000 | IR, lower pass, IR passes (constant fold, DCE), C codegen, docgen, typechecker, formatter, source optimizer |
| `runtime/` | ~3,500 | Interpreter (tree-walking), `compiler_runtime` (Python-emit JIT), VM, debugger, memory manager, JIT tracker, source maps |
| `runtime/core/` | ~3,500 | The Triad equation solver and multi-substrate runtime |
| `runtime/physics/` | ~2,500 | Observables, atom counting, causal analysis, energy readout, qubits |
| `runtime/codec/` | ~500 | Value ↔ wavefunction codecs |
| `runtime/ml/` | ~5,000 | Tensor library, neural network primitives, TriadSSM |
| `stdlib/` | ~2,000 | What `.tri` files import: `triad`, `triad.nn`, `triad.tensor`, regimes, templates, plot |
| `cli/` | ~1,500 | The `triad` command surface |
| `embed/`, `adapters/` | ~700 | Embedding TriadLang in Python; flask/headless adapters for interop programs |

Total: ~26,000 lines.

The solver and ML stack are included here because `.tri` programs use them. If you want them as standalone Python packages without the language, see [triadlang/pde](https://github.com/triadlang/pde) and [triadlang/machine-learning](https://github.com/triadlang/machine-learning).

---

## Tests

```bash
pytest tests/
```

160 tests pass.

- 148 cover the language internals (lexer, parser, IR, IR passes, typechecker, interpreter, interpreter-compiler parity, stdlib, solver audit)
- 12 run actual `.tri` programs from `programs/` and check their output

The .tri-program tests live in `tests/test_programs.py`. They run hello, loops, anti_collapse, solver ablation, cross-domain origin-of-life, Bell state, predator-prey, FDT verification, mock LLM runtime, calibration demo, and the XOR ML training.

---

## What the language gives you that a Python script does not

You can write a Python script that calls the solver and reads observables. The reason `.tri` files exist is that `reg`, `couple`, `ring`, and `OBSERVE` are first-class statements with a simpler surface than the equivalent Python:

```python
# Python equivalent of `reg a : B0 = 1;`
from triadlang.stdlib.regimes import resolve_regime
from triadlang.runtime.core.multi_runtime import MultiRuntime
rt = MultiRuntime(dt=0.005, record_every=4)
p_a = resolve_regime('B0', seed=0, L=32.0, N=128, dt=0.005)
sub_a = rt.add_substrate('a', p_a)
```

becomes

```python
reg a : B0 = 1;
```

This matters when you want to describe a system of coupled fields and observe what they do. The language pulls the runtime plumbing out of sight so the program reads as the physical specification it is.

---

## What is not in this package

- Detailed PDE research utilities (calibrator advanced modes, sigma curriculum, steering, observers, SAT) live in the main repo. Some are exposed through `.tri` syntax; for deeper Python access see [triadlang/pde](https://github.com/triadlang/pde).
- Standalone ML library without the language: see [triadlang/machine-learning](https://github.com/triadlang/machine-learning).
- The full native C runtime (FFTW3 build system, native CLI, GGUF chat) lives in the main [TriadLang](https://github.com/triadlang/triadlang) repository.

---

## License

TriadLang Proprietary Source-Available License

Copyright © 2026 triadlang.
All rights reserved.

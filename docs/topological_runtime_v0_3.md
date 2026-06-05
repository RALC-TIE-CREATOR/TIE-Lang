# TIE-Lang v0.3.0 — Topological Execution Preview

## Why this version changes direction

Up to `v0.2.x`, TIE-Lang has been a runnable language with TIE-inspired semantics,
but its public execution model is still effectively a compact binary virtual machine.

`v0.3.0` starts a different phase:

- not just more syntax
- not just more compiler features
- but a new execution substrate

The goal is to move from a language *about* TIE to a language that begins to
*execute through topological structure*.

## Source basis

This preview is grounded in two TIE sources used as architectural references:

1. **Teoría de la Infraestructura Espacial (TIE)**  
   Zenodo record `20320490`, published May 21, 2026, DOI `10.5281/zenodo.20320490`.

2. **Bisturí TIE v3.0 aplicado a las constantes fundamentales del SI**  
   local PDF used as a technical design reference.

From the Zenodo record we take the high-level ontological commitments:

- time as absolute, discrete, and universal
- space as a rigid Euclidean container
- matter as structured information over infrastructure
- explicit, axiomatic separation between postulates, derivations, and open problems

From the local Bisturí document we take the more computationally actionable ideas:

- the network scale `a`
- the temporal scale `omega_0`
- the topological coupling `alpha`
- the cubic network as a privileged substrate
- closed self-avoiding paths as structured states
- sine-Gordon style phase dynamics as the deeper continuous target

## Architectural decision

`v0.3.0` does **not** try to replace the stable CPU backend in one jump.

Instead, it introduces a dual-track architecture:

1. **Stable backend**
   - current compiler -> 4-bit CPU path
   - remains the executable reference for the language

2. **Experimental topological backend**
   - lives in `topology/`
   - stores state as topological objects on a lattice
   - acts as the first real execution preview for future hardware simulation

This keeps the language usable while allowing the substrate to evolve.

## First substrate choice

The first `v0.3.0` substrate is intentionally discrete:

- cubic lattice
- periodic boundaries
- self-avoiding closed loops
- orientation as minimal topological state

This is simpler than a full phase-field or sine-Gordon simulator, but it is already
qualitatively different from a conventional RAM bit:

- the state is spatially extended
- it is preserved under translation
- it is defined by topology, not by a single cell value

## Current preview model

The new `topology/` package introduces four concepts:

### 1. `CubicLattice`

The infrastructure carrier.

Responsibilities:

- define the discrete substrate
- provide adjacency
- provide wrapping / periodic boundary behavior

### 2. `ClosedLoop`

The minimal persistent information object.

Responsibilities:

- validate self-avoidance
- validate closure
- compute discrete winding / orientation
- allow topology-preserving translation

### 3. `TopologicalMemoryCell`

The first explicit memory abstraction on top of a loop.

Current encoding:

- `bit = 1` -> positive orientation
- `bit = 0` -> negative orientation

This is not the final ontology of TIE-Lang memory, but it establishes the key rule:
logical value is read from topological state rather than scalar memory alone.

### 4. `TopologicalRuntimePreview`

The first runtime that manipulates those objects.

Current operations:

- write a bit as an oriented loop
- read its encoded bit
- read its winding charge
- translate the loop while preserving state
- apply a topological `NOT` by reversing orientation
- apply local interactions between nearby loops
- project runtime cells into the phase-field backend and re-measure them
- materialize 4-bit values as 4-plane topological registers

## Local interaction rules

The preview now includes the first explicit local rules between nearby structures:

- **same charge + near** -> repulsion
- **opposite charge + near** -> annihilation
- **otherwise** -> coexistence

These are still discrete toy rules, but they move the project from static
topological storage toward topological dynamics.

## Bridge to the existing phase substrate

The preview now also connects into `core/red.py`.

This bridge:

- takes a discrete loop
- projects it to a vortex-like phase defect with matching winding
- evolves it through the damped sine-Gordon-style field
- re-measures the resulting topological charge using `medir_N(...)`

So the project now has both:

- a discrete topological state layer
- and a first measurement loop back into the phase substrate

## First language bridge

The preview now also includes a first lowering path from source code into the
topological runtime.

Supported initial subset:

- `let x = 0/1`
- `let x = true/false`
- `let y = x`
- `let y = not x`
- `print expr`
- `if expr: ... else: ...`
- `while expr: ...`
- `break`
- `continue`
- small arithmetic with `+`, `-`, `*`, `inc`, and `dec`
- bitwise operations `~`, `&`, `|`, `^`
- small boolean combinations with `and` and `or`
- simple comparisons over already known lowered values

This is intentionally small, but it matters because the project now has:

- source text
- AST
- lowering
- topological instruction stream
- topological runtime state

without passing through the binary CPU path.

## Explicit topological instruction layer

The experimental backend now includes a real intermediate instruction layer.

Current instruction families:

- value stores
- unary boolean operations
- binary boolean operations
- arithmetic operations
- bitwise operations
- comparisons
- labels and jumps
- conditional jumps

This is the first point where the project starts to look like a distinct
topological virtual machine rather than only a direct interpreter over loops.

## First step toward a lattice-native ALU

The preview now goes one step beyond scalar temporary arithmetic:

- each lowered value `0..15` is written as a 4-plane topological register
- each plane stores one bit as an oriented closed loop
- each register can be projected into a single shared sine-Gordon-style `Red`
  instead of four unrelated phase simulations
- `+` is resolved through a discrete ripple-carry pass over those planes
- `-` is resolved through two's-complement style bit-plane addition
- `*` is resolved as repeated shifted additions across the same planes
- `&`, `|`, `^`, and `~` operate directly plane by plane
- arithmetic snapshots now expose an `alu_trace` with per-plane carry generation,
  propagation, killing, and the local loop interaction involved in each step

This is still a hybrid design, but it is no longer only "integer math next to
topology". The runtime state for ALU values now exists on the lattice as a
bundle of topological cells.

The phase bridge now measures both per-plane windings after shared evolution and
the reconstructed `measured_value` from those measured planes.

It also computes a stability report:

- `stable`: whether `measured_value == value` with zero bit errors
- `bit_errors`: number of planes whose measured bit changed
- `energy_delta`: final phase energy minus initial phase energy
- `layout`: current register layout used for the projection

## Why loops first

Closed loops are the right first step because they let the project model:

- persistence
- locality
- deformation without value loss
- topological equivalence classes

before taking on the harder continuous problems:

- breather stability
- defect interactions
- phase relaxation
- explicit sine-Gordon evolution

## What this does not do yet

This preview is still intentionally incomplete.

It does **not** yet provide:

- full compiler lowering into topological instructions
- lattice-native arithmetic
- continuous phase evolution
- breather-based particle simulation
- topological timing driven by `omega_0`

## Current ALU boundary

The new ALU layer makes the topological VM meaningfully more executable, but it is
still a transitional design:

- values are normalized to a 4-bit range (`0..15`)
- arithmetic and bitwise operations execute over 4-plane topological bundles
- those bundles are still coordinated by the instruction machine
- timing and relaxation are still discrete rather than continuous field dynamics
- carry propagation is represented as local loop interactions, but it is not yet
  physically timed by the phase substrate
- register phase projection evolves all planes together, but ALU transitions are
  still applied before phase evolution rather than being caused by the field
- the `stable` register layout is only an experimental geometry option, not yet
  an optimizer

That means `v0.3.0` now has a real topological register ALU path, but not yet a
fully dynamical lattice-native ALU.

## Post-v0.3.0: phase-causal ALU preview

The next local development track begins `v0.4.0`.

In the first opt-in preview, ALU execution can use the phase substrate
causally:

- the instruction machine computes a tentative ALU register
- the register is projected into the phase field
- the field evolves and is measured
- the VM commits `measured_value` as the final value

This is exposed through:

```bash
python -m compiler.topological_run examples/topologia_phase_causal.tie --phase-causal
```

This mode is deliberately experimental and can change program output when a
compact register layout is unstable under phase evolution.

## Next milestones after the preview

### Phase 1

- `rows`, `cols`, and language-level growth may continue independently
- but substrate work should now live in `topology/`

### Phase 2

- add richer local transition rules between neighboring loops / defects
- introduce interaction primitives beyond repulsion and annihilation

### Phase 3

- enrich the phase-field backend linked to the existing `core/red.py`
- simulate defect motion and relaxation explicitly

### Phase 4

- define a small topological instruction set
- lower a strict subset of TIE-Lang into that backend

### Phase 5

- compare binary backend vs topological backend on the same source programs

## Design principle for v0.3.0

The point of `v0.3.0` is not to claim final topological hardware.

The point is to ensure that from this version onward, TIE-Lang has:

- a stable language path
- an experimental topological execution path
- and a documented bridge between them

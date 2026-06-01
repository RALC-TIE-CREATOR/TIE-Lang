# TIE-Lang Roadmap

This roadmap is intentionally short and concrete.
It tracks the next public-facing layers of the repository.

## Current baseline

Today the project already has:

- a working compiler pipeline
- a runnable 4-bit CPU model
- official CLI entry points
- canonical examples
- compiler and CPU verification
- an experimental neural layer

## v0.3.0 delivered

The `v0.3.0` release starts the experimental topological execution track.

Delivered in `v0.3.0`:

- keep the current compiler/CPU path as the stable backend
- begin a topological execution backend in parallel
- introduce a cubic lattice, closed-loop memory, and local interactions
- lower a small TIE-Lang subset into topological instructions
- add a 4-plane topological ALU preview
- project registers into the phase substrate and report stability

## Topological backend goals

### 1. Topological memory

- represent information as persistent topological structures
- begin with closed loops on a cubic lattice
- preserve state under translation and deformation

### 2. Topological transitions

- define local reversible or quasi-local update rules
- move beyond scalar RAM semantics
- introduce defect interaction primitives
- connect those transition rules to the phase substrate already present in `core/`

### 3. Substrate evolution

- connect the discrete preview to the existing sine-Gordon-style `core/` layer
- add explicit phase evolution and relaxation
- compare discrete loop storage with phase-field dynamics

### 4. Language bridge

- define a subset of TIE-Lang that can lower into the topological backend
- keep the current CPU backend as the reference path during transition

## Next language goals

### 1. Function expressiveness

- explicit writes to global variables from inside functions
- stronger scope behavior and clearer variable lifetime rules
- more reliable temporary values inside nested expressions and control flow

### 2. Language surface

- richer expressions and operators
- more ergonomic function usage
- more polished examples that show real program structure

### 3. Machine growth

- expand beyond the strict 4-bit baseline where appropriate
- improve memory model flexibility
- preserve the current machine as a documented reference profile

## Next tooling goals

- clearer CLI help and public-facing command polish
- better example discovery and execution flows
- stronger public release notes for future tags

## Next neural goals

- larger and noisier datasets
- more training instrumentation
- stronger connection between neural abstractions and the TIE conceptual model

## Public release direction

The next strong public release should feel like:

- a cleaner repository front page
- a more expressive language core
- the first explicit topological execution preview
- a better defined boundary between stable language features and experimental substrate work

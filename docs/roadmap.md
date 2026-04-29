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
- a better defined boundary between stable language features and experimental neural work

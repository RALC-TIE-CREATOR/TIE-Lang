# TIE-Lang v1.0 Specification

## Scope

This document defines the behavior of the current TIE-Lang implementation.
It is a technical reference for the language as it exists in the repository today.

## Execution model

TIE-Lang compiles high-level source into instructions for a 4-bit virtual CPU.

Pipeline:

`source -> lexer -> parser -> AST -> compiler -> CPU instructions -> execution`

## Numeric model

- All immediate values loaded into registers are truncated to 4 bits.
- Registers `R0`, `R1`, `R2`, and `R3` store values in the range `0..15`.
- RAM stores 4-bit values.
- CPU arithmetic is modular at 4 bits.
- ALU helper functions may expose carry or extended intermediate values, but CPU-visible register results are 4-bit.

## Booleans

- `1` means true.
- `0` means false.
- Comparison expressions compile to `1` or `0`.
- `if` and `while` treat `0` as false and any nonzero value as true.

## Statements

Supported statements:

- `let name = expr`
- `name = expr`
- `print expr`
- `if expr:`
- `else:`
- `while expr:`
- `def name(args):`
- `return expr`

Blocks are delimited by indentation, following a Python-style layout rule.

## Expressions

Supported expression forms:

- integer literals
- identifiers
- unary `~`
- binary `+`, `-`, `&`, `|`, `^`
- comparisons `==`, `!=`, `<`, `>`, `<=`, `>=`
- function calls

## Functions

Function behavior in v1.0:

- Up to 4 positional arguments are supported.
- Arguments are passed through registers `R0` to `R3`.
- On function entry, arguments are stored into the function's variable slots in RAM.
- Return values are produced in `R3`.
- A call used inside an expression is moved from `R3` into the requested destination register.

Accepted call syntax:

- `f(a, b)`
- `f(a b)`

Official v1.0 syntax is comma-separated:

- `f(a, b)`

Legacy whitespace-separated calls remain accepted for compatibility in v1.0:

- `f(a b)`

This legacy form should be treated as compatibility syntax, not as the preferred public style.

## Control flow

### If

- The condition is compiled as an expression.
- The result is compared against `0`.
- `0` selects the `else` branch.
- Nonzero selects the main branch.

### While

- The loop condition is reevaluated on every iteration.
- The loop exits when the condition evaluates to `0`.

## Comparison semantics

Comparison operators return normalized booleans:

- true -> `1`
- false -> `0`

Supported comparisons:

- equality: `==`
- inequality: `!=`
- less-than: `<`
- greater-than: `>`
- less-or-equal: `<=`
- greater-or-equal: `>=`

## Arithmetic semantics

### Addition

- CPU addition writes the low 4 bits into the destination register.
- Carry is reflected in the CPU `C` flag.

### Subtraction

- CPU subtraction writes the low 4 bits into the destination register.
- Negative results wrap modulo 16.
- The CPU `N` flag indicates that the conceptual result was negative before wrapping.

Example:

- `7 - 3 = 4`
- `3 - 7 = 12` with `N = 1`

## Memory model

- Variables are assigned fixed RAM slots by name during compilation.
- A variable first appears when assigned or referenced.
- RAM is shared across the current compiled program.
- Function parameters are materialized into RAM on function entry.

## Current limits

Known implementation limits in v1.0:

- 4-bit registers and RAM cells
- 16 RAM cells in the current CPU memory model
- up to 4 function arguments
- no floating point
- no strings
- no arrays
- no lexical scopes beyond the current RAM-based variable allocation model

## Recommended source style

Recommended style for v1.0 programs:

- use commas in function signatures and calls
- keep numeric expectations within 4-bit CPU semantics
- treat wrapped arithmetic as part of the machine model, not an error

## Stability statement

This specification describes the repository's current executable behavior and should be treated as the reference for TIE-Lang v1.0 until a later spec supersedes it.

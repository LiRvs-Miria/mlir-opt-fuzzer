# ADR-0001: Scope and IP firewall

Status: accepted, 2026-10-28

## Context

This project feeds bugs and infrastructure into `llvm-project` upstream
under a personal identity, while the author's employer operates a
compiler toolchain in the same space. Mixing the two would create IP
attribution ambiguity and disqualify the work from clean upstream
review.

## Decision

1. **Public formats and upstream public code only.** Inputs and
   outputs are limited to: MLIR text/bytecode, LLVM IR/bitcode,
   LLVM's public fuzzing interfaces (`FuzzMutate`, `FuzzerCLI`),
   and public test corpora (`mlir/test`).
2. **No employer code, dialects, or private know-how.** Any IR that
   derives from a proprietary stack stays outside this repository and
   outside every bug report. Campaign corpora are drawn from public
   test suites or synthesized from public dialect definitions.
3. **Personal identity, personal time, personal devices.** All
   upstream interaction (discourse, PRs, issue reports) is conducted
   as an individual contributor.
4. **License**: Apache-2.0 WITH LLVM-exception, matching the
   destination ecosystem.

## Consequences

- Bug reports are restricted to crashes reproducible on public inputs;
  this is also what maximizes upstream engagement (crashes on valid,
  real-world-shaped IR are the valuable kind per the fuzzer-issue
  guidelines).
- Any finding that touches a private stack is recorded nowhere here
  and handled under the employer's own processes.

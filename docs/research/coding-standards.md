# Coding standards survey — LLVM/MLIR code and review conventions

Not yet researched. Questions this file must answer before writing the
fuzzer target; sources listed where known.

## Questions

1. LLVM Coding Standards as applied to `mlir/tools/` targets: naming,
   error handling (`llvm::Error` vs ad-hoc), include order,
   RTTI/extensions discipline.
2. MLIR-specific conventions: `mlir::` C++ API idioms relevant to a
   fuzzer driver (parser entry points, pass-manager invocation,
   verifier calls), diagnostics verbosity control (a fuzzer must not
   spam stderr).
3. Test conventions: does an in-tree fuzz target come with lit tests?
   What do existing targets ship (`llvm-isel-fuzzer` has
   `llvm/test/...`?)?
4. Review etiquette: RFC-first threshold (which changes need discourse
   pre-approval), patch size norms, how new tools directories get
   approved (OWNERS? area reviewers?).

## Candidate sources

- `llvm/docs/CodingStandards.rst`, `llvm/docs/CodeReview.rst`,
  `llvm/docs/DeveloperPolicy.rst`, `llvm/docs/Contributing.rst`
- `mlir/docs/` (PassManagement, LangRef, DialectCreation)
- `llvm/tools/llvm-opt-fuzzer/` and `mlir/tools/mlir-parser-fuzzer/`
  as code exemplars
- discourse threads archived in this repository (guidelines RFC)

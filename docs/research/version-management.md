# Version management survey — upstream branching, releases, backports

Not yet researched. Questions this file must answer before the first
PR; sources listed where known.

## Questions

1. Branch/release model: release branch cut cadence, what lands on
   main vs release, backport (cherry-pick) norms and approval process.
2. PR lifecycle: review requirements (who reviews MLIR PRs), CI
   pipelines (pre-merge/post-merge), commit squash/merge conventions,
   commit message format for mlir/ changes.
3. Fork workflow mechanics: keeping a fork's main synced, branch
   naming conventions seen in accepted contributor PRs.
4. LLVM CLA: signing flow, how the PR check manifests.
5. Issue tracker conventions: labels relevant to us
   (`fuzzer-generated` — does it exist yet per PR #112372?),
   `mlir` issue routing, triage roles.

## Candidate sources

- `llvm/docs/` (ReleaseProcess, CodeReview, DeveloperPolicy,
  GettingInvolved, SourceManagement?)
- llvm-dev / discourse release announcements
- `google/oss-fuzz/projects/llvm/project.yaml` (fuzzing cadence)
- Recent merged `mlir/` PRs as convention exemplars

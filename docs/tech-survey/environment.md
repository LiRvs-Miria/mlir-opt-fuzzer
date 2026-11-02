# Campaign environment facts

Moved here from `research/build-toolchain.md` in the 2026-11-02
restructure — these addenda are campaign-era measurements and belong
to the tech-survey stage (each stage keeps its own environment facts).

## Addendum 2026-10-29 — build complete

`ninja -C ~/mlir-fuzz-build mlir-opt mlir-reduce -j 14` finished
(EXIT:0; two shards from the 1547-step freeze). All four binaries of
interest now exist and run: `bin/mlir-text-parser-fuzzer`,
`bin/mlir-bytecode-parser-fuzzer`, `bin/mlir-opt`,
`bin/mlir-reduce`. Build facts above unchanged.

## Addendum 2026-10-29 — libFuzzer fork-mode startup cost (measured)

Fork mode (`-fork=N`) runs a `CrashResistantMerge` pass over the whole
seed corpus before the first fuzzing job starts, executing every unit
serially. Measured on this machine (10.4k-unit `corpus-seeded`,
MLIR-sized inputs): ~2390 units processed in the first ~40s
(≈60–70 units/s incl. process start), no fuzzing job started within
45s. Practical consequences:

- Short runs (<5 min) are infeasible on a 10k-unit corpus; use a
  ~200-unit corpus subset (startup ≈ seconds).
- Long campaigns absorb the cost (six 540s shards each paid it within
  their tool windows); it scales linearly with corpus size.
- `-max_len` caps unit cost during merge; without it, merge runs with
  the 1 MB default per-unit cap.
- Stale `/tmp/libFuzzerTemp.FuzzWithFork.*.dir` directories are left
  behind when a run is killed mid-merge; safe to remove.

#!/usr/bin/env python3
"""Executable acceptance net for mlir/tools/mlir-opt-fuzzer.

Drives the acceptance table in docs/design/acceptance-criteria.md:
one probe per row, objective verdicts only (exit code + libFuzzer
artifact files; no output text is parsed). Contract and verdict
semantics: driver/README.md.

RED state: the target binary does not exist yet — every row reports
RED. As rows of the target land, probes flip to PASS; the net never
enters the PR (AC-9).
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# libFuzzer's default -error_exitcode (FuzzerFlags.def); the driver
# never overrides it. A recorded-abort verdict is keyed to this value.
LIBFUZZER_ERROR_EXITCODE = 77

# D-1: pipeline selection is a process-static command-line flag, and
# the input is module-only. Flag name pinned to the mlir-opt
# convention; if the landed PR chooses a different name, this is the
# single constant to update.
TARGET_FLAG = "--pass-pipeline"

FIXTURES = Path(__file__).resolve().parent / "fixtures"

AC5_PIPELINE = "builtin.module(func.func(cse))"
AC6_PIPELINE = "builtin.module(remove-dead-values)"

VERDICTS = ("PASS", "FAIL", "RED")


def run_target(bin_path, artifact_dir, args, timeout):
    """Run the target once; return (rc, timed_out, new_artifacts).

    Objective signals only: the process exit code and the directory
    diff of libFuzzer's artifact prefix. Output text is captured and
    discarded, never parsed.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    before = set(artifact_dir.glob("*"))
    cmd = [str(bin_path), f"-artifact_prefix={artifact_dir}/", *args]
    try:
        cp = subprocess.run(cmd, capture_output=True, timeout=timeout)
        rc, timed_out = cp.returncode, False
    except subprocess.TimeoutExpired:
        rc, timed_out = None, True
    new = sorted(p.name for p in artifact_dir.glob("*") if p not in before)
    return rc, timed_out, new


def expect_exit0(probe_id, input_path, pipeline=None):
    """AC-2/3/5: the input is consumed and rejected/accepted cleanly."""
    def probe(bin_path, workdir, timeout):
        args = ([f"{TARGET_FLAG}={pipeline}"] if pipeline else []) + [str(input_path)]
        rc, timed_out, new = run_target(
            bin_path, workdir / f"{probe_id}-artifacts", args, timeout)
        if timed_out:
            return "FAIL", "timeout — no exit"
        if rc == 0 and not new:
            return "PASS", "rc=0, no artifacts"
        return "FAIL", f"rc={rc}, artifacts={new}"
    return probe


def expect_recorded_abort(probe_id, input_path, pipeline):
    """AC-6: post-pipeline verify failure → abort(), recorded by libFuzzer.

    Runs in corpus mode (-runs=1, trigger as a one-file corpus):
    libFuzzer records artifacts only in fuzzing/corpus mode — in
    single-file mode the deadly-signal handler deliberately skips
    artifact writing (the input is already on disk).
    """
    def probe(bin_path, workdir, timeout):
        art = workdir / f"{probe_id}-artifacts"
        corpus = workdir / f"{probe_id}-corpus"
        art.mkdir(parents=True, exist_ok=True)
        corpus.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_path, corpus / input_path.name)
        args = [f"{TARGET_FLAG}={pipeline}",
                f"-artifact_prefix={art}/", "-runs=1", str(corpus)]
        rc, timed_out, new = run_target(bin_path, art, args, timeout)
        if timed_out:
            return "FAIL", "timeout — no exit"
        if rc == LIBFUZZER_ERROR_EXITCODE and len(new) == 1:
            return "PASS", f"rc={rc}, artifact {new[0]}"
        if rc is not None and rc < 0:
            # subprocess reports a raw death as -signal (shell would say
            # 128+n, e.g. SIGABRT = -6 / 134): the process died without
            # libFuzzer recording it — the abort is not attributable to
            # the oracle.
            return "FAIL", (f"killed by signal {-rc} — abort not routed "
                            "through libFuzzer; attribution failed")
        return "FAIL", f"rc={rc}, artifacts={new}"
    return probe


PROBES = [
    ("AC-2", "garbage bytes → exit 0",
     expect_exit0("ac2a", FIXTURES / "ac2-garbage.bin",
                  pipeline=AC5_PIPELINE)),
    ("AC-2", "module + pipeline tail → exit 0 (absorbed AC-4)",
     expect_exit0("ac2b", FIXTURES / "ac2-pipeline-tail.mlir",
                  pipeline=AC5_PIPELINE)),
    ("AC-3", "bytecode magic → exit 0",
     expect_exit0("ac3", FIXTURES / "ac3-bytecode.bin",
                  pipeline=AC5_PIPELINE)),
    ("AC-5", "good module + pipeline → exit 0",
     expect_exit0("ac5", FIXTURES / "ac5-good.mlir", pipeline=AC5_PIPELINE)),
    ("AC-6", "verify failure → recorded abort",
     expect_recorded_abort("ac6", FIXTURES / "ac6-mf007-min-private.mlir",
                           pipeline=AC6_PIPELINE)),
]


def report_all_red(reason):
    for pid, promise, _ in PROBES:
        print(f"  {pid:<5} RED   {promise}  [{reason}]")
    print(f"summary: 0/{len(PROBES)} probes PASS, all RED — {reason}")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="acceptance net for mlir-opt-fuzzer (see driver/README.md)")
    ap.add_argument("--bin", required=True, type=Path,
                    help="path to the built mlir-opt-fuzzer binary")
    ap.add_argument("--workdir", type=Path, default=None,
                    help="dir for libFuzzer artifacts (default: fresh temp dir)")
    ap.add_argument("--timeout", type=int, default=60,
                    help="per-probe timeout in seconds")
    args = ap.parse_args(argv)

    bin_path = args.bin
    if not (bin_path.is_file() and os.access(bin_path, os.X_OK)):
        return report_all_red(f"target not built: {bin_path}")

    workdir = args.workdir or Path(tempfile.mkdtemp(prefix="ac-driver-"))
    workdir.mkdir(parents=True, exist_ok=True)

    results = []
    for pid, promise, probe in PROBES:
        try:
            verdict, detail = probe(bin_path, workdir, args.timeout)
        except Exception as exc:  # driver bug: loud, attributable, table continues
            verdict, detail = "FAIL", f"DRIVER BUG: {exc!r}"
        results.append(verdict)
        print(f"  {pid:<5} {verdict:<5} {promise}  [{detail}]")

    npass, nfail, nred = (results.count(v) for v in VERDICTS)
    print(f"workdir: {workdir}")
    print(f"summary: {npass}/{len(PROBES)} probes PASS, {nfail} FAIL, {nred} RED")
    return 0 if npass == len(PROBES) else 1


if __name__ == "__main__":
    sys.exit(main())

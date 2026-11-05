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

# D-1: pipeline selection is process-static. The channel is the
# `--pipeline` cl flag, enabled after libFuzzer's
# -ignore_remaining_args=1 marker; the slug resolves against the
# target's closed vocabulary (MlirOptFuzzerPipelines.def in-tree).
AC5_SLUG = "cse"
AC6_SLUG = "remove-dead-values"

FIXTURES = Path(__file__).resolve().parent / "fixtures"

VERDICTS = ("PASS", "FAIL", "RED")


def run_target(bin_path, artifact_dir, args, timeout, slug):
    """Run the target once; return (rc, timed_out, new_artifacts).

    The pipeline is selected by slug through the target's cl flag,
    enabled after libFuzzer's -ignore_remaining_args=1 marker (the
    FuzzerCLI.h parseFuzzerCLOpts boundary). Objective signals only:
    the process exit code and the directory diff of libFuzzer's
    artifact prefix. Output text is captured and discarded, never
    parsed.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    before = set(artifact_dir.glob("*"))
    cmd = [str(bin_path), f"-artifact_prefix={artifact_dir}/", *args,
           "-ignore_remaining_args=1", f"--pipeline={slug}"]
    try:
        cp = subprocess.run(cmd, capture_output=True, timeout=timeout)
        rc, timed_out = cp.returncode, False
    except subprocess.TimeoutExpired:
        rc, timed_out = None, True
    new = sorted(p.name for p in artifact_dir.glob("*") if p not in before)
    return rc, timed_out, new


def expect_exit0(probe_id, input_path, slug):
    """AC-2/3/5: the input is consumed and rejected/accepted cleanly."""
    def probe(bin_path, workdir, timeout):
        rc, timed_out, new = run_target(
            bin_path, workdir / f"{probe_id}-artifacts", [str(input_path)],
            timeout, slug)
        if timed_out:
            return "FAIL", "timeout — no exit"
        if rc == 0 and not new:
            return "PASS", "rc=0, no artifacts"
        return "FAIL", f"rc={rc}, artifacts={new}"
    return probe


def expect_recorded_abort(probe_id, input_path, slug):
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
        args = ["-runs=1", str(corpus)]
        rc, timed_out, new = run_target(bin_path, art, args, timeout, slug)
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


def expect_reproducible_abort(probe_id, input_path, slug, runs=10):
    """AC-8: same input, same outcome — the crash reproduces 10/10.

    The AC-6 corpus-mode run, repeated `runs` times as independent
    processes, each with a FRESH artifact dir: libFuzzer names crash
    artifacts after the input (crash-<sha1>), so a shared dir collides
    on the name from run 2 onward and the directory diff goes silent.
    Every run must record exactly one artifact.
    """
    def probe(bin_path, workdir, timeout):
        corpus = workdir / f"{probe_id}-corpus"
        corpus.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_path, corpus / input_path.name)
        args = ["-runs=1", str(corpus)]
        misses = []
        for i in range(runs):
            rc, timed_out, new = run_target(
                bin_path, workdir / f"{probe_id}-artifacts-{i}", args,
                timeout, slug)
            if timed_out:
                misses.append(f"run {i}: timeout — no exit")
            elif rc != LIBFUZZER_ERROR_EXITCODE or len(new) != 1:
                misses.append(f"run {i}: rc={rc}, artifacts={new}")
        if misses:
            return "FAIL", f"{len(misses)}/{runs} runs missed: " + "; ".join(misses)
        return "PASS", f"{runs}/{runs} runs recorded an abort"
    return probe


PROBES = [
    ("AC-2", "garbage bytes → exit 0",
     expect_exit0("ac2a", FIXTURES / "ac2-garbage.bin",
                  slug=AC5_SLUG)),
    ("AC-2", "module + pipeline tail → exit 0 (absorbed AC-4)",
     expect_exit0("ac2b", FIXTURES / "ac2-pipeline-tail.mlir",
                  slug=AC5_SLUG)),
    ("AC-3", "bytecode magic → exit 0",
     expect_exit0("ac3", FIXTURES / "ac3-bytecode.bin",
                  slug=AC5_SLUG)),
    ("AC-5", "good module + pipeline → exit 0",
     expect_exit0("ac5", FIXTURES / "ac5-good.mlir", slug=AC5_SLUG)),
    ("AC-6", "verify failure → recorded abort",
     expect_recorded_abort("ac6", FIXTURES / "ac6-mf007-min-private.mlir",
                           slug=AC6_SLUG)),
    ("AC-8", "crash reproduces 10/10 single-process",
     expect_reproducible_abort("ac8", FIXTURES / "ac6-mf007-min-private.mlir",
                               slug=AC6_SLUG)),
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

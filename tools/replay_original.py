"""Replay the reviewed legacy script without overwriting frozen source files.

Requires NumPy. Redirects only the script's OUT assignment; all forecasting and
sampling code is executed unchanged. Outputs and provenance are saved separately.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import platform
from pathlib import Path

SCRIPT_SHA256 = "78dbce559f8d40820b4e58850b8aee54de40d632fdee80880833498dd352c7ce"
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "private" / "continuity"
FILENAMES = ("ufc_forecast_lab_2026-10-10_frozen.csv", "ufc_forecast_lab_2026-10-10_frozen.json")


def replay(output):
    import numpy as np
    output = Path(output).resolve()
    if output == ARCHIVE.resolve():
        raise ValueError("Replay requires a separate output directory")
    output.mkdir(parents=True, exist_ok=True)
    for name in (*FILENAMES, "replay-report.json"):
        if (output / name).exists():
            raise ValueError("Replay output already exists; choose a fresh directory")
    source = (ARCHIVE / "ufc_forecast_lab_2026-10-10.py").read_bytes()
    if hashlib.sha256(source).hexdigest() != SCRIPT_SHA256:
        raise ValueError("Original script hash differs from reviewed version")
    before = {name: hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() for name in FILENAMES}
    tree = ast.parse(source)
    redirects = 0
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "OUT" for t in node.targets):
            if ast.unparse(node.value) != "Path('/mnt/data')":
                raise ValueError("Unexpected output declaration")
            node.value.args[0] = ast.Constant(str(output))
            redirects += 1
    if redirects != 1:
        raise ValueError("Expected exactly one output assignment")
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(ast.fix_missing_locations(tree), "legacy_forecast_script", "exec"), {"__name__": "__main__"})
    assert before == {name: hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() for name in FILENAMES}
    original = json.loads((ARCHIVE / FILENAMES[1]).read_bytes())
    rerun = json.loads((output / FILENAMES[1]).read_bytes())
    pairs = list(zip(original["fights"], rerun["fights"]))
    report = {
        "script_sha256": SCRIPT_SHA256,
        "execution_date": "2026-10-08",
        "python_version": platform.python_version(), "numpy_version": np.__version__,
        "rng": "numpy.random.default_rng (PCG64), sequential multinomial calls in original fight order",
        "seed": 2026100801, "draws_per_fight": 100000, "total_draws": rerun["total_draws"],
        "execution_change": "Only OUT redirected to a fresh directory; source bytes unchanged",
        "original_files_unchanged": True,
        "same_fight_count": len(original["fights"]) == len(rerun["fights"]),
        "exact_count_array_matches": sum(a["mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC"] == b["mc_outcomes_aKO_aSUB_aDEC_bKO_bSUB_bDEC"] for a,b in pairs),
        "json_structure_equal": original == rerun,
        "byte_equal": {name: (ARCHIVE / name).read_bytes() == (output / name).read_bytes() for name in FILENAMES},
        "output_sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in FILENAMES},
        "execution_stdout": stdout.getvalue(),
        "original_environment_version": "not recorded; this is the verified replay environment"
    }
    (output / "replay-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = replay(args.output)
    print(json.dumps({k: result[k] for k in ("numpy_version", "exact_count_array_matches", "json_structure_equal", "byte_equal")}, indent=2))

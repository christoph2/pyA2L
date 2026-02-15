#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import statistics
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pya2l import import_a2l
from pya2l.api.validate import Validator
from pya2l.imex import export_a2l_db, export_json_dict, open_a2l_database


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASETS: List[Path] = [
    PROJECT_ROOT / "examples" / "example-a2l-file.a2l",
]


@dataclass
class IterationTimings:
    import_seconds: float
    export_a2l_seconds: float
    export_json_seconds: float
    validate_seconds: Optional[float]


def _aggregate(values: Iterable[Optional[float]]) -> Dict[str, Optional[float]]:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return {"mean": None, "median": None, "min": None, "max": None}
    return {
        "mean": statistics.mean(filtered),
        "median": statistics.median(filtered),
        "min": min(filtered),
        "max": max(filtered),
    }


def run_iteration(dataset: Path, module: Optional[str], loglevel: str) -> IterationTimings:
    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset}")

    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        try:
            t0 = time.perf_counter()
            session = import_a2l(str(dataset), loglevel=loglevel, progress_bar=False, local=True)
            import_seconds = time.perf_counter() - t0
            session.close()
            try:
                bind = session.bind
            except Exception:
                bind = None
            if bind is not None:
                try:
                    bind.dispose()
                except Exception:
                    pass

            db_path = Path(tempdir) / dataset.with_suffix(".a2ldb").name
            db = open_a2l_database(db_path, loglevel)
            try:
                t1 = time.perf_counter()
                export_a2l_db(db, Path(tempdir) / "out.a2l", module)
                export_a2l_seconds = time.perf_counter() - t1

                t2 = time.perf_counter()
                json_dict = export_json_dict(db, module)
                json_to_dict_seconds = time.perf_counter() - t2

                try:
                    t3 = time.perf_counter()
                    Validator(db.session)()
                    validate_seconds = time.perf_counter() - t3
                except Exception:
                    validate_seconds = None

                t4 = time.perf_counter()
                json.dumps(json_dict, ensure_ascii=False, separators=(",", ":"))
                json_serialize_seconds = time.perf_counter() - t4

                export_json_seconds = json_to_dict_seconds + json_serialize_seconds
            finally:
                db.close()
        finally:
            os.chdir(original_cwd)

    return IterationTimings(
        import_seconds=import_seconds,
        export_a2l_seconds=export_a2l_seconds,
        export_json_seconds=export_json_seconds,
        validate_seconds=validate_seconds,
    )


def run_benchmark(
    datasets: List[Path], iterations: int, module: Optional[str], loglevel: str
) -> Dict[str, Dict[str, float]]:
    results: Dict[str, Dict[str, float]] = {}
    for ds in datasets:
        timings: List[IterationTimings] = []
        for _ in range(iterations):
            timings.append(run_iteration(ds, module, loglevel))

        results[str(ds)] = {
            "iterations": iterations,
            "import": _aggregate(t.import_seconds for t in timings),
            "export_a2l": _aggregate(t.export_a2l_seconds for t in timings),
            "export_json": _aggregate(t.export_json_seconds for t in timings),
            "validate": _aggregate(t.validate_seconds for t in timings),
        }
    return results


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark import/export/validation flows.")
    parser.add_argument(
        "-d",
        "--dataset",
        dest="datasets",
        action="append",
        type=Path,
        help="Datasets to benchmark (A2L files). Can be given multiple times.",
    )
    parser.add_argument(
        "-n",
        "--iterations",
        dest="iterations",
        type=int,
        default=3,
        help="Number of iterations per dataset (default: 3).",
    )
    parser.add_argument(
        "-m",
        "--module",
        dest="module",
        type=str,
        default=None,
        help="Optional: restrict export to a single module.",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        dest="loglevel",
        type=str,
        default="ERROR",
        help="Log level for import/export/validation (default: ERROR).",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=Path,
        help="Optional JSON file to store benchmark results.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    datasets = args.datasets or DEFAULT_DATASETS
    resolved = [d.resolve() for d in datasets]

    results = run_benchmark(resolved, args.iterations, args.module, args.loglevel)

    def _fmt(value: Optional[float]) -> str:
        return "n/a" if value is None else f"{value:.4f}s"

    for path_str, data in results.items():
        print(f"Dataset: {path_str}")
        for key in ("import", "export_a2l", "export_json", "validate"):
            agg = data[key]
            print(
                f"  {key}: mean={_fmt(agg['mean'])} median={_fmt(agg['median'])} "
                f"min={_fmt(agg['min'])} max={_fmt(agg['max'])}"
            )

    if args.output:
        args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Test different flush strategies for A2L import optimization.
Compares memory usage and performance across strategies.
"""

import shutil
import sys
import tempfile
import time
import uuid
from pathlib import Path

from memory_profiler import memory_usage


sys.path.insert(0, str(Path(__file__).parent))

from configurable_parser import (
    AdaptiveStrategy,
    ConfigurableParser,
    CurrentStrategy,
    FixedIntervalStrategy,
    MemoryThresholdStrategy,
)


def import_with_strategy(a2l_path, strategy, label=""):
    """Import A2L file with specific flush strategy and track memory."""
    temp_a2l = None
    db_path = None

    try:
        # Setup temp files
        temp_dir = Path(tempfile.gettempdir())
        temp_name = f"flush_test_{uuid.uuid4().hex[:8]}"
        temp_a2l = temp_dir / f"{temp_name}.a2l"
        db_path = temp_dir / f"{temp_name}.a2ldb"

        for path in [temp_a2l, db_path]:
            if path.exists():
                path.unlink()

        shutil.copy2(a2l_path, temp_a2l)

        def do_import():
            parser = ConfigurableParser(flush_strategy=strategy)
            return parser.load(str(temp_a2l), in_memory=False, loglevel="CRITICAL", progress_bar=False)

        start_time = time.perf_counter()

        # Track memory during import
        mem_usage = memory_usage(do_import, interval=0.1, max_usage=True, retval=True, include_children=True)

        peak_mem = mem_usage[0]
        db_obj = mem_usage[1]

        elapsed = time.perf_counter() - start_time

        # Get stats
        file_size_mb = a2l_path.stat().st_size / (1024 * 1024)
        throughput = file_size_mb / elapsed

        total_objects = 0
        if db_obj:
            # Use SessionProxy API
            import pya2l

            try:
                num_measurements = db_obj.session.query(pya2l.model.Measurement).count()
                num_characteristics = db_obj.session.query(pya2l.model.Characteristic).count()
                num_axis_pts = db_obj.session.query(pya2l.model.AxisPts).count()
                total_objects = num_measurements + num_characteristics + num_axis_pts
            finally:
                db_obj.close()

        return {
            "strategy": strategy.name,
            "label": label,
            "file_size_mb": file_size_mb,
            "elapsed_sec": elapsed,
            "throughput_mbps": throughput,
            "peak_memory_mib": peak_mem,
            "total_objects": total_objects,
        }

    finally:
        # Cleanup
        time.sleep(0.5)
        for path in [temp_a2l, db_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass


def format_comparison(results):
    """Format results comparison table."""
    print("\n" + "=" * 120)
    print(f"{'Strategy':<30} {'File':<20} {'Size':<10} {'Time':<10} {'Throughput':<12} {'Peak Mem':<12} {'vs Baseline':<12}")
    print("=" * 120)

    # Group by file
    by_file = {}
    for r in results:
        file_label = r["label"]
        if file_label not in by_file:
            by_file[file_label] = []
        by_file[file_label].append(r)

    for file_label, file_results in by_file.items():
        # Find baseline (Current strategy)
        baseline = next((r for r in file_results if "Current" in r["strategy"]), file_results[0])
        baseline_mem = baseline["peak_memory_mib"]
        baseline_time = baseline["elapsed_sec"]

        print(f"\n--- {file_label} ({baseline['file_size_mb']:.2f} MB) ---")

        for r in file_results:
            mem_diff = ((r["peak_memory_mib"] - baseline_mem) / baseline_mem) * 100
            time_diff = ((r["elapsed_sec"] - baseline_time) / baseline_time) * 100

            vs_baseline = f"Mem: {mem_diff:+.1f}%, Time: {time_diff:+.1f}%"

            print(
                f"{r['strategy']:<30} {r['label']:<20} {r['file_size_mb']:>8.2f}MB "
                f"{r['elapsed_sec']:>8.2f}s {r['throughput_mbps']:>10.2f}MB/s "
                f"{r['peak_memory_mib']:>10.1f}MiB {vs_baseline:<30}"
            )

    print("=" * 120 + "\n")


def main():
    """Test all flush strategies."""
    repo_root = Path(__file__).parent.parent

    test_files = [
        (repo_root / "examples" / "ASAP2_Demo_V161.a2l", "Small (0.15MB)"),
        (repo_root / "examples" / "C350U701_00_13_4cyl.a2l", "Medium (8.73MB)"),
        (repo_root / "examples" / "5091.a2l", "Large (16.21MB)"),
    ]

    strategies = [
        CurrentStrategy(),
        FixedIntervalStrategy(500),
        FixedIntervalStrategy(1000),
        FixedIntervalStrategy(2000),
        AdaptiveStrategy(),
        MemoryThresholdStrategy(1000),
        MemoryThresholdStrategy(2000),
    ]

    print("=" * 120)
    print("FLUSH STRATEGY COMPARISON")
    print("=" * 120)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Strategies to test: {len(strategies)}")
    print(f"Test files: {len(test_files)}")
    print()

    results = []

    for file_path, file_label in test_files:
        if not file_path.exists():
            print(f"SKIP {file_label}: File not found")
            continue

        print(f"\n{'='*120}")
        print(f"Testing: {file_label}")
        print(f"Path: {file_path}")
        print(f"{'='*120}")

        for strategy in strategies:
            print(f"\n  Strategy: {strategy.name}")
            print(f"    Running... ", end="", flush=True)

            try:
                result = import_with_strategy(file_path, strategy, file_label)
                results.append(result)
                print(f"OK {result['elapsed_sec']:.2f}s, {result['peak_memory_mib']:.1f}MiB")
            except Exception as e:
                print(f"FAILED: {e}")
                import traceback

                traceback.print_exc()

    if results:
        format_comparison(results)

        # Summary
        print("\nSUMMARY:")
        print("-" * 120)

        # Find best strategy for each metric
        by_file = {}
        for r in results:
            file_label = r["label"]
            if file_label not in by_file:
                by_file[file_label] = []
            by_file[file_label].append(r)

        for file_label, file_results in by_file.items():
            print(f"\n{file_label}:")

            best_mem = min(file_results, key=lambda x: x["peak_memory_mib"])
            best_time = min(file_results, key=lambda x: x["elapsed_sec"])

            print(f"  Best memory: {best_mem['strategy']} ({best_mem['peak_memory_mib']:.1f} MiB)")
            print(f"  Best time:   {best_time['strategy']} ({best_time['elapsed_sec']:.2f}s)")

            baseline = next((r for r in file_results if "Current" in r["strategy"]), None)
            if baseline and best_mem["strategy"] != baseline["strategy"]:
                mem_saved = baseline["peak_memory_mib"] - best_mem["peak_memory_mib"]
                mem_pct = (mem_saved / baseline["peak_memory_mib"]) * 100
                print(f"  → Memory saved: {mem_saved:.1f} MiB ({mem_pct:.1f}%)")

        print("-" * 120)
    else:
        print("\n⚠️  No results to display")


if __name__ == "__main__":
    main()

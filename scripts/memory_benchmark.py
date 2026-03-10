#!/usr/bin/env python
"""
Memory-profiling benchmark for A2L import.
Tests different flush strategies with small/medium/large files.
"""

import os
import sys
import tempfile
import time
from pathlib import Path

from memory_profiler import memory_usage


# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pya2l


def import_with_memory_tracking(a2l_path, label=""):
    """Import A2L file and track peak memory usage."""
    db_path = None
    temp_a2l = None
    try:
        # Create unique temporary names
        import uuid

        temp_dir = Path(tempfile.gettempdir())
        temp_name = f"memory_test_{uuid.uuid4().hex[:8]}"
        temp_a2l = temp_dir / f"{temp_name}.a2l"
        db_path = temp_dir / f"{temp_name}.a2ldb"

        # Clean up any existing
        for path in [temp_a2l, db_path]:
            if path.exists():
                path.unlink()

        # Copy A2L to temp location
        import shutil

        shutil.copy2(a2l_path, temp_a2l)

        start_time = time.perf_counter()

        # Track memory during import
        mem_usage = memory_usage(
            (pya2l.import_a2l, (str(temp_a2l),), {"loglevel": "CRITICAL", "in_memory": False, "progress_bar": False}),
            interval=0.1,
            max_usage=True,
            retval=True,
            include_children=True,
        )

        peak_mem = mem_usage[0]  # Peak memory in MiB
        db_obj = mem_usage[1]  # Return value

        elapsed = time.perf_counter() - start_time

        # Get file size
        file_size_mb = a2l_path.stat().st_size / (1024 * 1024)
        throughput = file_size_mb / elapsed

        # Count objects
        total_objects = 0
        if db_obj:
            try:
                # SessionProxy has query() method directly
                num_measurements = db_obj.query(pya2l.model.Measurement).count()
                num_characteristics = db_obj.query(pya2l.model.Characteristic).count()
                num_axis_pts = db_obj.query(pya2l.model.AxisPts).count()
                total_objects = num_measurements + num_characteristics + num_axis_pts
            finally:
                db_obj.close()
                db_obj = None  # Mark as closed

        return {
            "label": label,
            "file_size_mb": file_size_mb,
            "elapsed_sec": elapsed,
            "throughput_mbps": throughput,
            "peak_memory_mib": peak_mem,
            "total_objects": total_objects,
            "mem_per_object_kib": (peak_mem * 1024) / total_objects if total_objects > 0 else 0,
        }
    finally:
        # Cleanup - wait a bit for Windows file locks
        import time as time_mod

        time_mod.sleep(0.5)
        for path in [temp_a2l, db_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors


def format_results(results):
    """Pretty-print results table."""
    print("\n" + "=" * 100)
    print(f"{'File':<30} {'Size':<10} {'Time':<10} {'Throughput':<12} {'Peak Mem':<12} {'Objects':<10} {'Mem/Obj':<10}")
    print("=" * 100)

    for r in results:
        print(
            f"{r['label']:<30} {r['file_size_mb']:>8.2f}MB {r['elapsed_sec']:>8.2f}s "
            f"{r['throughput_mbps']:>10.2f}MB/s {r['peak_memory_mib']:>10.1f}MiB "
            f"{r['total_objects']:>9} {r['mem_per_object_kib']:>8.2f}KiB"
        )

    print("=" * 100 + "\n")


def main():
    """Run memory profiling on available test files."""
    repo_root = Path(__file__).parent.parent

    # Find test files
    test_files = [
        (repo_root / "examples" / "ASAP2_Demo_V161.a2l", "Small (0.15MB)"),
        (repo_root / "examples" / "C350U701_00_13_4cyl.a2l", "Medium (8.73MB)"),
        (repo_root / "examples" / "5091.a2l", "Large (16.21MB)"),
    ]

    print("=" * 100)
    print("MEMORY PROFILING: A2L Import with current flush strategy")
    print("=" * 100)
    print(f"Python: {sys.version.split()[0]}")
    print(f"pya2l: {pya2l.__version__}")
    print(f"Test files: {len(test_files)}")
    print()

    results = []

    for file_path, label in test_files:
        if not file_path.exists():
            print(f"SKIP {label}: File not found")
            continue

        print(f"\nProfiling: {label}")
        print(f"  Path: {file_path}")
        print(f"  Tracking memory usage...")

        try:
            result = import_with_memory_tracking(file_path, label)
            results.append(result)
            print(f"  OK Done: {result['elapsed_sec']:.2f}s, Peak: {result['peak_memory_mib']:.1f}MiB")
        except Exception as e:
            print(f"  FAILED: {e}")

    if results:
        format_results(results)

        # Analysis
        print("\nANALYSIS:")
        print("-" * 100)

        if len(results) >= 2:
            small = results[0]
            medium = results[1]

            mem_ratio = medium["peak_memory_mib"] / small["peak_memory_mib"]
            size_ratio = medium["file_size_mb"] / small["file_size_mb"]

            print(f"Memory scaling: {mem_ratio:.2f}x memory for {size_ratio:.2f}x file size")
            print(f"  -> {'LINEAR' if 0.8 <= mem_ratio/size_ratio <= 1.2 else 'NON-LINEAR'} scaling")

            if len(results) >= 3:
                large = results[2]
                mem_ratio_lg = large["peak_memory_mib"] / medium["peak_memory_mib"]
                size_ratio_lg = large["file_size_mb"] / medium["file_size_mb"]
                print(f"\nMedium->Large: {mem_ratio_lg:.2f}x memory for {size_ratio_lg:.2f}x file size")
                print(f"  -> {'LINEAR' if 0.8 <= mem_ratio_lg/size_ratio_lg <= 1.2 else 'NON-LINEAR'} scaling")

                # Projection for very large files
                if large["peak_memory_mib"] > 100:
                    print(f"\nWARNING: Large files use {large['peak_memory_mib']:.0f}MiB")
                    projected_50mb = large["peak_memory_mib"] * (50 / large["file_size_mb"])
                    print(f"  Projected for 50MB file: ~{projected_50mb:.0f}MiB ({projected_50mb/1024:.1f}GiB)")

        print("-" * 100)
    else:
        print("\nNo results to display")


if __name__ == "__main__":
    main()

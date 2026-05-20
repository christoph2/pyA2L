#!/usr/bin/env python
"""
Simple flush strategy tester - modifies parser temporarily and measures impact.
Tests by changing line 423 of a2lparser.py: self.advance = keyword_counter // X
"""

import shutil
import sys
import tempfile
import time
import tracemalloc
import uuid
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


def test_flush_strategy(a2l_path, divisor, label):
    """Test a specific flush strategy by modifying parser advance calculation."""
    import pya2l
    from pya2l import a2lparser

    # Backup original
    original_code = a2lparser.A2LParser.load.__code__

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

        # Monkey-patch the advance calculation
        original_load = a2lparser.A2LParser.load

        def patched_load(self, file_name, in_memory=False, local=False, remove_existing=False, loglevel="INFO", progress_bar=True):
            # Call original but override self.advance after parsing
            from os import unlink
            from time import perf_counter

            from rich.console import Console
            from rich.progress import (
                BarColumn,
                Progress,
                SpinnerColumn,
                TaskProgressColumn,
                TimeElapsedColumn,
                TimeRemainingColumn,
            )

            import pya2l.a2lparser_ext as ext
            from pya2l.a2lparser import FakeRoot, path_components, update_tables
            from pya2l.utils import detect_encoding

            loglevel = loglevel.upper()
            effective_progress = progress_bar and sys.stderr.isatty() and loglevel not in ("ERROR", "CRITICAL")
            self.silent = not effective_progress
            a2l_fn, db_fn = path_components(in_memory, file_name, local)

            if not in_memory:
                if remove_existing:
                    try:
                        unlink(str(db_fn))
                    except Exception:
                        pass
                elif db_fn.exists():
                    raise OSError(f"file {db_fn!r} already exists.")

            if not self.encoding:
                self.encoding = detect_encoding(file_name=a2l_fn)

            start_time = perf_counter()
            self.db = pya2l.model.A2LDatabase(str(db_fn), debug=self.debug)

            try:
                keyword_counter, values, tables, aml_data = ext.parse(str(a2l_fn), self.encoding, loglevel)
            except Exception as e:
                print(f"{e!r}", file=sys.stderr)
                try:
                    unlink(str(db_fn))
                except Exception:
                    pass
                raise

            self.counter = 0

            progress_columns = (
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                TaskProgressColumn(),
                "Elapsed:",
                TimeElapsedColumn(),
                "Remaining:",
                TimeRemainingColumn(),
            )
            self.progress_bar = Progress(*progress_columns, console=Console(stderr=True), disable=self.silent)

            if not self.silent:
                self.task = self.progress_bar.add_task("[blue]writing to DB...", total=keyword_counter)

            # CUSTOM ADVANCE CALCULATION
            if divisor == "adaptive":
                # Adaptive strategy
                if keyword_counter < 10000:
                    self.advance = 100
                elif keyword_counter < 100000:
                    self.advance = min(500, 200 + (keyword_counter - 10000) // 300)
                else:
                    self.advance = 1000
            elif isinstance(divisor, int):
                # Fixed interval
                if divisor < 0:
                    # Divisor mode (original style): keyword_counter // X
                    self.advance = keyword_counter // abs(divisor) if keyword_counter >= abs(divisor) else 1
                else:
                    # Fixed interval mode
                    self.advance = divisor
            else:
                # Fallback to original
                self.advance = keyword_counter // 100 if keyword_counter >= 100 else 1

            fr = FakeRoot()
            with self.progress_bar:
                self.traverse(values, fr, None, False)

            self.db.session.commit()
            update_tables(self.db.session, tables)
            self.db.session.commit()

            return self.db

        a2lparser.A2LParser.load = patched_load

        def do_import():
            parser = a2lparser.A2LParser()
            return parser.load(str(temp_a2l), in_memory=False, loglevel="CRITICAL", progress_bar=False)

        start_time = time.perf_counter()

        tracemalloc.start()
        db_obj = do_import()
        _, peak_mem_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mem = peak_mem_bytes / (1024 * 1024)  # Convert to MiB

        elapsed = time.perf_counter() - start_time

        # Get stats
        file_size_mb = a2l_path.stat().st_size / (1024 * 1024)
        throughput = file_size_mb / elapsed

        total_objects = 0
        if db_obj:
            try:
                num_measurements = db_obj.session.query(pya2l.model.Measurement).count()
                num_characteristics = db_obj.session.query(pya2l.model.Characteristic).count()
                num_axis_pts = db_obj.session.query(pya2l.model.AxisPts).count()
                total_objects = num_measurements + num_characteristics + num_axis_pts
            finally:
                db_obj.close()

        return {
            "strategy": label,
            "file_size_mb": file_size_mb,
            "elapsed_sec": elapsed,
            "throughput_mbps": throughput,
            "peak_memory_mib": peak_mem,
            "total_objects": total_objects,
        }

    finally:
        # Restore original
        a2lparser.A2LParser.load = original_load

        # Cleanup
        time.sleep(0.5)
        for path in [temp_a2l, db_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass


def main():
    repo_root = Path(__file__).parent.parent

    test_files = [
        (repo_root / "examples" / "ASAP2_Demo_V161.a2l", "Small (0.15MB)"),
        (repo_root / "examples" / "C350U701_00_13_4cyl.a2l", "Medium (8.73MB)"),
        (repo_root / "examples" / "5091.a2l", "Large (16.21MB)"),
    ]

    # Test configurations: (divisor/interval, label)
    # Negative = divisor mode (keyword_counter // X)
    # Positive = fixed interval mode
    # "adaptive" = adaptive strategy
    strategies = [
        (-100, "Current (1%)"),
        (-50, "Flush-2%"),
        (-20, "Flush-5%"),
        (500, "Fixed-500"),
        (1000, "Fixed-1000"),
        (2000, "Fixed-2000"),
        ("adaptive", "Adaptive"),
    ]

    print("=" * 120)
    print("FLUSH STRATEGY COMPARISON")
    print("=" * 120)
    print()

    results = []

    for file_path, file_label in test_files:
        if not file_path.exists():
            print(f"SKIP {file_label}")
            continue

        print(f"\n{'='*120}")
        print(f"Testing: {file_label}")
        print(f"{'='*120}")

        for divisor, strategy_label in strategies:
            print(f"  {strategy_label:<20} ... ", end="", flush=True)

            try:
                result = test_flush_strategy(file_path, divisor, strategy_label)
                result["file_label"] = file_label
                results.append(result)
                print(f"OK {result['elapsed_sec']:>6.2f}s, {result['peak_memory_mib']:>7.1f}MiB")
            except Exception as e:
                print(f"FAILED: {e}")
                import traceback

                traceback.print_exc()

    # Print comparison table
    if results:
        print("\n" + "=" * 120)
        print("SUMMARY")
        print("=" * 120)

        by_file = {}
        for r in results:
            file_label = r["file_label"]
            if file_label not in by_file:
                by_file[file_label] = []
            by_file[file_label].append(r)

        for file_label, file_results in by_file.items():
            print(f"\n{file_label}:")
            print(f"{'Strategy':<20} {'Time':<10} {'Memory':<12} {'vs Baseline Time':<18} {'vs Baseline Mem':<18}")
            print("-" * 120)

            baseline = next((r for r in file_results if "Current" in r["strategy"]), file_results[0])
            baseline_time = baseline["elapsed_sec"]
            baseline_mem = baseline["peak_memory_mib"]

            for r in file_results:
                time_diff = ((r["elapsed_sec"] - baseline_time) / baseline_time) * 100
                mem_diff = ((r["peak_memory_mib"] - baseline_mem) / baseline_mem) * 100

                print(
                    f"{r['strategy']:<20} {r['elapsed_sec']:>8.2f}s {r['peak_memory_mib']:>10.1f}MiB "
                    f"{time_diff:>+7.1f}%            {mem_diff:>+7.1f}%"
                )

            # Find best
            best_mem = min(file_results, key=lambda x: x["peak_memory_mib"])
            best_time = min(file_results, key=lambda x: x["elapsed_sec"])

            print(
                f"\n  Best memory: {best_mem['strategy']} ({best_mem['peak_memory_mib']:.1f} MiB, {((best_mem['peak_memory_mib'] - baseline_mem) / baseline_mem * 100):+.1f}%)"
            )
            print(
                f"  Best time:   {best_time['strategy']} ({best_time['elapsed_sec']:.2f}s, {((best_time['elapsed_sec'] - baseline_time) / baseline_time * 100):+.1f}%)"
            )

        print("\n" + "=" * 120)
    else:
        print("\nNo results to display")


if __name__ == "__main__":
    main()

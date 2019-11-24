#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import linecache
import os
import tracemalloc

"""Memory allocation profiler.

Note
----
 - Requires Python >= 3.4
"""


def display_top(snapshot, key_type = 'lineno', limit = 15):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)
    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

def allocprof(func):
    @functools.wraps(func)
    def inner(*args, **kws):
        tracemalloc.start()
        try:
            res = func(*args, **kws)
        finally:
            snapshot = tracemalloc.take_snapshot()
            display_top(snapshot)
        return res
    return inner


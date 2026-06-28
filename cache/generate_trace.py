"""Synthetic cache-workload generator for the AdvNet cache domain.

Instead of letting the adversary search a raw multi-million-request trace
(astronomically high-dimensional), AdvNet evolves a small set of *workload
knobs* per time segment and this module expands them into a concrete request
trace that libCacheSim can simulate.

Trace encoding
--------------
This module consumes the per-segment knobs only: ``T`` segments laid out
back-to-back, ``5`` integer knobs each (so the segment part has length
``5 * T``)::

    [a1, n1, s1, c1, k1,  a2, n2, s2, c2, k2,  ...]

(The optional global cache-size *fraction* knob is handled one level up, in
``cache.evaluate``; it is stripped before the vector reaches this module.)

Per-segment knobs (integer-encoded; decoded here):

==========  ==================================  ===========================
knob        meaning                             decoding
==========  ==================================  ===========================
a (alpha)   Zipf popularity skew                alpha = a / 100   (e.g. 50->0.5)
n (n_objs)  size of the popularity pool         n_objs = n * 1000 objects
s (size)    object size for this segment        size   = s * 512 bytes
c (churn)   % of requests to brand-new objects  churn  = c / 100  (0..1)
k (scan)    one-shot unique objects (LRU scan)  scan   = k * 100  objects
==========  ==================================  ===========================

Each segment emits a contiguous ``scan`` burst (unique one-shot objects, the
classic LRU-polluting pattern) followed by ``REQS_PER_SEGMENT`` requests drawn
from a Zipf popularity distribution, with a ``churn`` fraction diverted to
never-seen objects (compulsory misses / locality drift).

Object-id namespaces are disjoint so they don't collide across kinds:
  - popularity pool ids:  ``0 .. n_objs-1``  (hot ids shared across segments,
    giving cross-segment temporal locality)
  - churn (new) ids:      ``>= 10_000_000``
  - scan ids:             ``>= 100_000_000``

Generation is deterministic for a given ``(trace, seed)`` so the optimizer sees
a stable objective and runs are reproducible.
"""

import os
import tempfile

import numpy as np

# Knobs per segment in the encoded decision vector.
KNOBS_PER_SEGMENT = 5

# Decoding scales (encoded integer -> physical quantity).
ALPHA_SCALE = 0.01   # alpha  = a * 0.01
NOBJ_SCALE = 1000    # n_objs = n * 1000 objects
SIZE_SCALE = 512     # size   = s * 512 bytes
SCAN_SCALE = 100     # scan   = k * 100 one-shot objects

# Number of popularity-driven requests per segment (excludes the scan burst).
# Kept fixed so per-evaluation cost is predictable; libCacheSim runs millions of
# requests per second, so ~10^5 per segment is cheap.
REQS_PER_SEGMENT = 50000

# Disjoint object-id base offsets (see module docstring).
CHURN_ID_BASE = 10_000_000
SCAN_ID_BASE = 100_000_000


def _zipf_weights(n_objs: int, alpha: float) -> np.ndarray:
    """Normalized Zipf probability over ranks ``1..n_objs`` (rank 1 = hottest)."""
    ranks = np.arange(1, n_objs + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, alpha)
    weights /= weights.sum()
    return weights


def generate_trace(trace, seed: int = 42):
    """Expand an encoded knob vector into a CSV trace file for libCacheSim.

    Args:
        trace: Flat list of ``5 * T`` integers (segment knobs; see module docstring).
        seed: RNG seed; fixed by default so identical knobs -> identical trace.

    Returns:
        ``(path, footprint_bytes)`` where ``path`` is a newly written CSV trace
        (columns ``time,obj,size`` with a header) and ``footprint_bytes`` is the
        total size of all *distinct* objects in the trace (the working-set size,
        used by the caller to scale the cache). The caller must delete the file.
    """
    if len(trace) % KNOBS_PER_SEGMENT != 0:
        raise ValueError(
            f"trace length ({len(trace)}) must be a multiple of "
            f"{KNOBS_PER_SEGMENT} (one segment = {KNOBS_PER_SEGMENT} knobs)"
        )

    rng = np.random.default_rng(seed)
    n_segments = len(trace) // KNOBS_PER_SEGMENT

    # Decode all segments first so we can size the pool-footprint accumulator.
    segments = []
    for seg in range(n_segments):
        base = seg * KNOBS_PER_SEGMENT
        segments.append({
            "alpha": max(trace[base + 0] * ALPHA_SCALE, 1e-3),
            "n_objs": max(int(trace[base + 1]) * NOBJ_SCALE, 1),
            "size": max(int(trace[base + 2]) * SIZE_SCALE, 1),
            "churn": min(max(trace[base + 3] / 100.0, 0.0), 1.0),
            "scan": max(int(trace[base + 4]) * SCAN_SCALE, 0),
        })
    max_n_objs = max(s["n_objs"] for s in segments)

    # First-seen size of each distinct popularity-pool object (0 = not yet seen).
    pool_first_size = np.zeros(max_n_objs, dtype=np.int64)
    footprint = 0  # distinct bytes from scan + churn objects (pool added at end)

    churn_id = CHURN_ID_BASE
    scan_id = SCAN_ID_BASE
    clock = 0

    fd, path = tempfile.mkstemp(prefix="advnet_cache_", suffix=".csv")
    with os.fdopen(fd, "w") as f:
        f.write("time,obj,size\n")
        for s in segments:
            size = s["size"]

            # Contiguous one-shot scan burst (pollutes recency-based caches).
            for _ in range(s["scan"]):
                clock += 1
                f.write(f"{clock},{scan_id},{size}\n")
                scan_id += 1
            footprint += s["scan"] * size  # every scan object is unique

            # Popularity-driven requests with a churn fraction of new objects.
            weights = _zipf_weights(s["n_objs"], s["alpha"])
            pool_ids = rng.choice(s["n_objs"], size=REQS_PER_SEGMENT, p=weights)
            is_new = rng.random(REQS_PER_SEGMENT) < s["churn"]

            # Footprint: churn objects are all unique; pool objects counted once.
            footprint += int(is_new.sum()) * size
            drawn_pool = pool_ids[~is_new]
            if drawn_pool.size:
                uniq = np.unique(drawn_pool)
                fresh = uniq[pool_first_size[uniq] == 0]
                pool_first_size[fresh] = size

            for j in range(REQS_PER_SEGMENT):
                clock += 1
                if is_new[j]:
                    obj = churn_id
                    churn_id += 1
                else:
                    obj = int(pool_ids[j])
                f.write(f"{clock},{obj},{size}\n")

    footprint += int(pool_first_size.sum())
    return path, int(footprint)

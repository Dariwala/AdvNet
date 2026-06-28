"""libCacheSim evaluation backend for the AdvNet cache domain.

Generates a synthetic workload from the encoded knob vector (see
``cache.generate_trace``), runs libCacheSim's ``cachesim`` for a *reference* and
a *target* eviction policy at a chosen cache size, scores each policy by its
(byte) hit rate, and returns the *relative difference* between the reference and
target scores (via ``scoring.compute_score``). Higher score means the discovered
workload is more adversarial for the target policy.

Cache sizing (``cache_size`` argument)
--------------------------------------
  - An absolute string like ``"100MB"`` / ``"1GB"`` -> fixed cache size; the
    whole trace vector is segment knobs (length ``5 * T``).
  - ``"absolute"`` -> fixed cache at the default size (``DEFAULT_ABS_CACHE_SIZE``).
  - ``"knob"`` -> the cache size is *searchable*: the LAST element of the trace
    vector is a fraction knob, decoded as ``fraction = enc / FRACTION_SCALE``,
    and the cache is sized to ``fraction * footprint`` (footprint = total bytes
    of all distinct objects). The segment part is therefore length ``5 * T`` and
    the full vector length is ``5 * T + 1``. Suggested bounds for the knob:
    ``5 .. 500`` -> 0.5% .. 50% of the footprint.

The ``cachesim`` binary location is read from the ``ADVNET_CACHESIM`` environment
variable (with a fallback to the local build).
"""

import os
import re
import subprocess

from cache.generate_trace import generate_trace
from scoring.scoring import compute_score

# Location of libCacheSim's cachesim binary. Override with ADVNET_CACHESIM.
CACHESIM_BIN = os.environ.get(
    "ADVNET_CACHESIM",
    "/Users/shehaba2/Documents/PhD Research/libcachesim/_build/bin/cachesim",
)

# CSV reader parameters for our generated traces (1-indexed columns, comma
# delimiter by default). Params are comma-separated for libCacheSim's parser.
CSV_TRACE_PARAMS = "time-col=1,obj-id-col=2,obj-size-col=3,obj-id-is-num=true,has-header=true"

# Sentinel for the searchable-cache-size mode.
KNOB_CACHE_SIZE = "knob"
# Sentinel meaning "use the default fixed cache size" (DEFAULT_ABS_CACHE_SIZE).
ABSOLUTE_CACHE_SIZE = "absolute"
DEFAULT_ABS_CACHE_SIZE = "100MB"
# Fraction knob decoding: fraction = encoded_value / FRACTION_SCALE.
FRACTION_SCALE = 1000.0
# Never ask cachesim for a degenerate (sub-object) cache.
MIN_CACHE_BYTES = 1024

# Matches the final summary line, anchored on ", throughput" so the per-interval
# progress lines (".. miss ratio X, interval miss ratio Y") never match. The
# "byte miss ratio" field is optional: some libCacheSim builds (this fork's
# `cachesim`) print only the object/request miss ratio.
#   old:  "... miss ratio 0.8056, byte miss ratio 0.9577, throughput ..."
#   fork: "... miss ratio 0.0662, throughput ..."
_MISS_RE = re.compile(
    r"miss ratio\s+([\d.]+)(?:,\s+byte miss ratio\s+([\d.]+))?,\s+throughput"
)


def _run_cachesim(trace_path, policy, cache_size, debug=False):
    """Run cachesim for one policy; return ``(req_miss_ratio, byte_miss_ratio)``.

    ``cache_size`` is passed straight to cachesim, which accepts an absolute
    string ("100MB") or a raw integer number of bytes. Returns ``None`` on
    failure or if the output can't be parsed.
    """
    cmd = [CACHESIM_BIN, trace_path, "csv", policy, str(cache_size), "-t", CSV_TRACE_PARAMS]
    if debug:
        print("    $", " ".join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        if debug:
            print(f"    cachesim failed: {e}")
        return None

    output = result.stdout + result.stderr
    match = None
    for line in output.splitlines():
        found = _MISS_RE.search(line)
        if found:
            match = found  # keep the last (final summary) line
    if match is None:
        if debug:
            print("    could not parse miss ratio from cachesim output")
        return None
    obj_miss = float(match.group(1))
    byte_miss = float(match.group(2)) if match.group(2) is not None else None
    return obj_miss, byte_miss


def evaluate(trace, ref_policy, tar_policy, cache_size="100MB",
             metric="byte", seed=42, debug=False):
    """Score a workload by how much worse ``tar_policy`` is than ``ref_policy``.

    Args:
        trace: Encoded decision vector. In fixed-size mode it is ``5 * T``
            segment knobs; in ``cache_size="knob"`` mode the last element is the
            cache-size fraction knob (so length ``5 * T + 1``). See module docs.
        ref_policy / tar_policy: libCacheSim eviction algorithms, e.g. "LRU",
            "FIFO", "ARC", "LFU", "LeCaR", "Cacheus".
        cache_size: Absolute string ("100MB"), "absolute" for the default fixed
            size, or "knob" to make the size a searchable fraction of the
            workload footprint.
        metric: "byte" (byte hit rate, default) or "req"/"obj" (object hit rate).
        seed: Trace-generation seed (fixed -> deterministic objective).
        debug: Print the cache size, per-policy hit rates and the final score.

    Returns:
        float: relative difference ``(ref_hit - tar_hit) / max(ref_hit, tar_hit)``
        of the per-policy (byte) hit rates. Positive means the target policy is
        worse on this workload (adversarial). 0.0 on build/sim failure.
    """
    if str(cache_size) == KNOB_CACHE_SIZE:
        if len(trace) < 1:
            raise ValueError("knob mode needs a trailing cache-size fraction element")
        segment_knobs = list(trace[:-1])
        fraction = max(trace[-1] / FRACTION_SCALE, 1e-4)
        trace_path, footprint = generate_trace(segment_knobs, seed=seed)
        cache_arg = max(int(fraction * footprint), MIN_CACHE_BYTES)
        if debug:
            print(f"    footprint: {footprint} B, fraction: {fraction:.4f}, "
                  f"cache: {cache_arg} B")
    else:
        trace_path, _ = generate_trace(list(trace), seed=seed)
        cache_arg = DEFAULT_ABS_CACHE_SIZE if str(cache_size) == ABSOLUTE_CACHE_SIZE else cache_size

    try:
        ref = _run_cachesim(trace_path, ref_policy, cache_arg, debug)
        tar = _run_cachesim(trace_path, tar_policy, cache_arg, debug)
    finally:
        try:
            os.remove(trace_path)
        except OSError:
            pass

    if ref is None or tar is None:
        if debug:
            print("    evaluation failed; returning neutral score 0.0")
        return 0.0

    # Per-policy score = hit rate, as in the Vulcan evaluator. Prefer byte hit
    # rate, but fall back to object hit rate when the build (e.g. this fork's
    # `cachesim`) doesn't report a byte miss ratio.
    use_byte = metric == "byte" and ref[1] is not None and tar[1] is not None
    if use_byte:
        ref_score, tar_score = 1.0 - ref[1], 1.0 - tar[1]
    else:
        ref_score, tar_score = 1.0 - ref[0], 1.0 - tar[0]

    # Main adversarial score = relative difference between the two policy scores
    # (same convention as scoring.compute_score, used by the other AdvNet
    # domains): positive when the reference outperforms the target, i.e. the
    # workload is adversarial for the target.
    if max(ref_score, tar_score) <= 1e-9:
        score = 0.0   # both policies hit ~nothing -> no differentiation
    else:
        score = float(compute_score([ref_score], [tar_score]))

    if debug:
        label = "byte hit rate" if use_byte else "obj hit rate"
        print(f"    {ref_policy} {label}: {ref_score:.4f}")
        print(f"    {tar_policy} {label}: {tar_score:.4f}")
        print(f"    score (relative diff): {score:.4f}")
    return score


if __name__ == "__main__":
    # Manual smoke test of the searchable-cache-size (knob) mode.
    # 2 segments x 5 knobs, then a trailing cache-size fraction knob.
    # [alpha, n_objs, size, churn, scan] x2  +  [fraction]
    example_trace = [120, 50, 8, 10, 5,
                     90, 200, 4, 40, 20,
                     100]  # fraction knob: 100/1000 = 10% of footprint
    print("Example cache trace (knob mode):", example_trace)
    s = evaluate(example_trace, ref_policy="LRU", tar_policy="FIFO",
                 cache_size="knob", debug=True)
    print("Returned adversarial score:", s)

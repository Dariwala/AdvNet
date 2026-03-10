# AdvNet: Searching for Adversarial Traces

AdvNet searches for adversarial traces using evolutionary algorithms. The main entry point for running the search is:

```
search_adv_traces.py
```

This script initializes the search process and runs the optimization algorithm to find traces that maximize the target score defined in a user-provided evaluation function.

---

# Running AdvNet

To start searching for adversarial traces, run:

```
python search_adv_traces.py [arguments]
```

## Arguments

### `--type`

A **unique integer identifier** representing the domain in which adversarial traces are being searched.

Inside `search_adv_traces.py`, each domain corresponds to a block:

```
if args.type == X:
```

If you want to use AdvNet for a new domain, you must add a new `if` block with a unique `type`.

---

### `--alg`

Specifies the algorithm used for searching adversarial traces.

Currently supported:

```
0 -> Random Generation (RG)
1 -> Genetic Algorithm (GA)
```

---

### `--trace_length`

Length of the trace to search.

Example:

```
--trace_length=5
```

---

### `--l_bounds`

Lower bound for each dimension of the trace.

Example:

```
--l_bounds 1 1 1 1 1
```

---

### `--u_bounds`

Upper bound for each dimension of the trace.

Example:

```
--u_bounds 10 10 10 10 10
```

---

### `--seed`

Random seed for reproducibility.

Example:

```
--seed=42
```

---

### `--total_time`

Total search time in seconds.

Example:

```
--total_time=3600
```

---

### `--initial_pop_file`

Optional file containing an **initial population of traces** to start the search.

```
--initial_pop_file=file_name
```

---

# Evaluation Function

Users must implement an **evaluation function** that computes the score of a given trace.

The function will be called by AdvNet during the search.

### Required Input

The evaluation function must accept the trace. Currently we support only 1D array and integer values.

---

### Additional Parameters

The evaluation function can accept **additional parameters** beyond the trace.

To pass those parameters, include them when instantiating the `CCProblem` class.

Example location:

```
search_adv_traces.py
    elif args.type == 1:
        elif args.alg == 1:
            if args.initial_pop_file == "None":
```

When calling `CCProblem`, pass the additional arguments at the end.

Example:

```
problem = CCProblem(..., extra_param1, extra_param2)
```

These parameters will be forwarded to the evaluation function via `*args`.

---

# Adding a New Domain

To use AdvNet in a new domain, follow these steps.

---

## Step 1: Add a New Domain Block

Open:

```
search_adv_traces.py
```

Add a new block:

```
if args.type == NEW_TYPE:
```

Inside this block:

- Configure the algorithm
- Instantiate `CCProblem`
- Provide required parameters

---

## Step 2: Modify `GA/problem.py`

Open:

```
GA/problem.py
```

Inside the `_evaluate` method, add a block for your domain:

```
if self.type == NEW_TYPE:
```

Call your evaluation function here.

Example:

```
score = evaluate(x, *args)
```

Where:

- `x` is the trace (NumPy 1D array)
- `*args` are the additional parameters passed from `CCProblem`

---

## Step 3: Logging

Inside `GA/problem.py`, implement logging for the search process.

### `update_max_score`

This method logs only when **a better trace is discovered**.

```
update_max_score(...)
```

Use it to record improvements in the best score found so far.

---

### `log`

This method logs **every trace evaluated during the search**.

```
log(...)
```

This provides a full history of the search process.

---

# Example Command

```
python search_adv_traces.py \
    --type=1 \
    --alg=1 \
    --trace_length=5 \
    --l_bounds 1 1 1 1 1 \
    --u_bounds 10 10 10 10 10 \
    --seed=42 \
    --total_time=3600
```

---

# Summary

To extend AdvNet to a new domain:

1. Add a new `args.type` block in `search_adv_traces.py`
2. Implement your evaluation function
3. Pass any additional parameters via `CCProblem`
4. Add a new case in `GA/problem.py::_evaluate`
5. Implement logging via `update_max_score` and `log`
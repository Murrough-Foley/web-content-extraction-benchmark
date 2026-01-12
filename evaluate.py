#!/usr/bin/env python3
"""
Web Content Extraction Benchmark - Evaluation Script

Evaluates article body extraction quality by comparing predictions against
ground truth using shingle-based matching (4-gram) for precision/recall/F1,
and exact token matching for accuracy.

No external dependencies required - uses only Python standard library.

Usage:
    python3 evaluate.py                     # Evaluate all output/*.json files
    python3 evaluate.py --output results.json  # Save results to JSON
    python3 evaluate.py --snippets          # Include snippet coverage metrics

Based on methodology from:
https://github.com/scrapinghub/article-extraction-benchmark
"""

import argparse
import gzip
import json
import random
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate content extraction predictions against ground truth'
    )
    parser.add_argument(
        '--n-bootstrap', type=int, default=1000,
        help='Number of bootstrap iterations for confidence intervals (default: 1000)'
    )
    parser.add_argument(
        '--output', type=Path,
        help='Save results to JSON file'
    )
    parser.add_argument(
        '--snippets', action='store_true',
        help='Include snippet coverage metrics (with/without)'
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help='Random seed for reproducible bootstrap estimates'
    )
    args = parser.parse_args()

    random.seed(args.seed)

    # Load ground truth
    ground_truth_path = Path('ground-truth.json')
    if not ground_truth_path.exists():
        print(f"Error: {ground_truth_path} not found")
        print("Make sure you're running from the benchmark directory")
        return 1

    ground_truth = load_json(ground_truth_path)
    print(f"Loaded {len(ground_truth)} ground truth entries\n")

    # Find all prediction files
    output_dir = Path('output')
    if not output_dir.exists():
        print(f"Error: {output_dir}/ directory not found")
        print("Create an output/ directory and add your prediction JSON files")
        return 1

    prediction_files = sorted(output_dir.glob('*.json'))
    if not prediction_files:
        print(f"Error: No JSON files found in {output_dir}/")
        print("Add your extractor output as JSON files in the output/ directory")
        return 1

    # Print header
    if args.snippets:
        print(f"{'Extractor':<24} {'F1':<14} {'Precision':<14} {'Recall':<14} {'Accuracy':<14} {'With%':<8} {'Without%':<8}")
        print("-" * 106)
    else:
        print(f"{'Extractor':<24} {'F1':<14} {'Precision':<14} {'Recall':<14} {'Accuracy':<14}")
        print("-" * 80)

    metrics_by_name = {}

    for path in prediction_files:
        name = path.stem
        predictions = load_json(path)

        # Validate keys match
        if set(ground_truth.keys()) != set(predictions.keys()):
            gt_keys = set(ground_truth.keys())
            pred_keys = set(predictions.keys())
            missing = gt_keys - pred_keys
            extra = pred_keys - gt_keys
            print(f"Warning: {name} - key mismatch")
            if missing:
                print(f"  Missing {len(missing)} keys: {list(missing)[:5]}...")
            if extra:
                print(f"  Extra {len(extra)} keys: {list(extra)[:5]}...")
            # Use intersection for evaluation
            common_keys = gt_keys & pred_keys
            if not common_keys:
                print(f"  Skipping {name} - no common keys")
                continue
        else:
            common_keys = set(ground_truth.keys())

        metrics = evaluate(
            ground_truth, predictions, common_keys,
            args.n_bootstrap, include_snippets=args.snippets
        )

        # Format output
        if args.snippets:
            print(
                f"{name:<24} "
                f"{metrics['f1']:.3f} +/- {metrics['f1_std']:.3f}  "
                f"{metrics['precision']:.3f} +/- {metrics['precision_std']:.3f}  "
                f"{metrics['recall']:.3f} +/- {metrics['recall_std']:.3f}  "
                f"{metrics['accuracy']:.3f} +/- {metrics['accuracy_std']:.3f}  "
                f"{metrics.get('with_pct', 0)*100:>5.1f}%  "
                f"{metrics.get('without_pct', 0)*100:>5.1f}%"
            )
        else:
            print(
                f"{name:<24} "
                f"{metrics['f1']:.3f} +/- {metrics['f1_std']:.3f}  "
                f"{metrics['precision']:.3f} +/- {metrics['precision_std']:.3f}  "
                f"{metrics['recall']:.3f} +/- {metrics['recall_std']:.3f}  "
                f"{metrics['accuracy']:.3f} +/- {metrics['accuracy_std']:.3f}"
            )

        # Remove internal data before storing
        metrics_clean = {k: v for k, v in metrics.items() if not k.startswith('_')}
        metrics_by_name[name] = metrics_clean

    print()

    if args.output:
        args.output.write_text(json.dumps(metrics_by_name, indent=2, sort_keys=True))
        print(f"Results saved to {args.output}")

    return 0


def evaluate(
    ground_truth: Dict[str, Dict],
    predictions: Dict[str, Dict],
    keys: set,
    n_bootstrap: int,
    include_snippets: bool = False
) -> Dict[str, Any]:
    """
    Evaluate predictions against ground truth.

    Uses 4-gram shingle matching for precision/recall/F1 (handles word order).
    Uses exact token matching for accuracy.
    """
    tp_fp_fns = []
    accuracies = []
    with_scores = []
    without_scores = []

    for key in keys:
        gt_entry = ground_truth[key]
        pred_entry = predictions[key]

        # Get article body text
        true_text = gt_entry.get('articleBody', '')
        pred_text = pred_entry.get('articleBody', '')

        # Calculate shingle-based metrics
        tp_fp_fns.append(string_shingle_matching(true=true_text, pred=pred_text))
        accuracies.append(get_accuracy(true=true_text, pred=pred_text))

        # Snippet coverage (optional)
        if include_snippets:
            with_snippets = gt_entry.get('with', [])
            without_snippets = gt_entry.get('without', [])

            if with_snippets:
                found = sum(1 for s in with_snippets if s.lower() in pred_text.lower())
                with_scores.append(found / len(with_snippets))

            if without_snippets:
                found = sum(1 for s in without_snippets if s.lower() in pred_text.lower())
                without_scores.append(found / len(without_snippets))

    # Calculate base metrics
    metrics: Dict[str, Any] = metrics_from_tp_fp_fns(tp_fp_fns)
    metrics['accuracy'] = statistics.mean(accuracies) if accuracies else 0.0

    # Add snippet metrics
    if include_snippets:
        metrics['with_pct'] = statistics.mean(with_scores) if with_scores else 0.0
        metrics['without_pct'] = statistics.mean(without_scores) if without_scores else 0.0

    # Bootstrap confidence intervals
    b_values: Dict[str, List[float]] = {}
    for _ in range(n_bootstrap):
        n = len(tp_fp_fns)
        indices = [random.randint(0, n - 1) for _ in range(n)]

        b_metrics = metrics_from_tp_fp_fns([tp_fp_fns[i] for i in indices])
        for key in b_metrics:
            b_values.setdefault(key, []).append(b_metrics[key])

        b_values.setdefault('accuracy', []).append(
            statistics.mean([accuracies[i] for i in indices])
        )

    for key, values in b_values.items():
        metrics[f'{key}_std'] = statistics.stdev(values) if len(values) > 1 else 0.0

    return metrics


def metrics_from_tp_fp_fns(tp_fp_fns: List[Tuple[float, float, float]]) -> Dict[str, float]:
    """Calculate precision, recall, F1 from list of (TP, FP, FN) tuples."""
    precisions = [
        precision_score(tp, fp, fn)
        for tp, fp, fn in tp_fp_fns
        if tp + fp > 0
    ]
    recalls = [
        recall_score(tp, fp, fn)
        for tp, fp, fn in tp_fp_fns
        if tp + fn > 0
    ]

    precision = statistics.mean(precisions) if precisions else 0.0
    recall = statistics.mean(recalls) if recalls else 0.0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return {
        'f1': f1,
        'precision': precision,
        'recall': recall,
    }


def precision_score(tp: float, fp: float, fn: float) -> float:
    if fp == fn == 0:
        return 1.0
    if tp == fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall_score(tp: float, fp: float, fn: float) -> float:
    if fp == fn == 0:
        return 1.0
    if tp == fn == 0:
        return 0.0
    return tp / (tp + fn)


def get_accuracy(true: str, pred: str) -> float:
    """Exact match accuracy after tokenization."""
    return float(_tokenize(true) == _tokenize(pred))


def string_shingle_matching(
    true: str, pred: str, ngram_n: int = 4
) -> Tuple[float, float, float]:
    """
    Compute normalized TP/FP/FN using shingle (n-gram) matching.

    This method accounts for word order (unlike simple word overlap) and is
    the standard approach used in content extraction benchmarks.

    Based on: https://moz.com/devblog/benchmarking-python-content-extraction-algorithms-dragnet-readability-goose-and-eatiht/
    """
    true_shingles = _all_shingles(true, ngram_n)
    pred_shingles = _all_shingles(pred, ngram_n)

    tp = fp = fn = 0.0

    for key in set(true_shingles) | set(pred_shingles):
        true_count = true_shingles.get(key, 0)
        pred_count = pred_shingles.get(key, 0)
        tp += min(true_count, pred_count)
        fp += max(0, pred_count - true_count)
        fn += max(0, true_count - pred_count)

    tp_fp_fn = [tp, fp, fn]
    total = sum(tp_fp_fn)

    # Normalize so longer texts don't have more weight
    if total > 0:
        tp_fp_fn = [x / total for x in tp_fp_fn]

    return tuple(tp_fp_fn)


def _all_shingles(text: str, ngram_n: int) -> Dict[Tuple[str, ...], int]:
    return dict(Counter(_ngrams(text, ngram_n)))


_TOKEN_RE = re.compile(r'\w+', re.UNICODE | re.MULTILINE | re.IGNORECASE | re.DOTALL)


def _tokenize(text: str) -> List[str]:
    """Simple unicode-aware tokenization."""
    return _TOKEN_RE.findall(text or '')


def _ngrams(text: str, n: int) -> List[Tuple[str, ...]]:
    tokens = _tokenize(text)
    result = []
    for i in range(max(1, len(tokens) - n + 1)):
        shingle = tuple(tokens[i:i + n])
        if shingle:
            result.append(shingle)
    return result


def load_json(path: Path) -> Dict:
    """Load JSON file (supports .json and .json.gz)."""
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == '__main__':
    exit(main())

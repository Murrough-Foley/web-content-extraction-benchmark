# Web Content Extraction Benchmark

A benchmark dataset for evaluating article body extraction quality, containing **1,507 modern web pages** with AI-generated ground truth annotations.

## Quick Start

```bash
# 1. Clone or download this repository
git clone https://github.com/user/web-content-extraction-benchmark.git
cd web-content-extraction-benchmark

# 2. Run your extractor on the HTML files and save output
python your_extractor.py  # outputs to output/your-extractor.json

# 3. Evaluate
python evaluate.py
```

## Dataset

- **1,507 web pages** from diverse sources (news, blogs, documentation, etc.)
- **HTML files** in `html/` directory (gzip-compressed)
- **Ground truth** in `ground-truth.json`

### Ground Truth Format

```json
{
  "0001": {
    "articleBody": "Full article text...",
    "url": "https://example.com/article",
    "title": "Article Title",
    "with": ["Sentences that MUST be included"],
    "without": ["Boilerplate that must NOT be included"]
  }
}
```

## Running Your Extractor

### 1. Process HTML Files

Read each HTML file from `html/`, extract the article body, and save results:

```python
import gzip
import json
from pathlib import Path

results = {}

for html_path in Path('html').glob('*.html.gz'):
    file_id = html_path.stem.replace('.html', '')

    with gzip.open(html_path, 'rt', encoding='utf-8') as f:
        html = f.read()

    # Your extraction logic here
    extracted_text = your_extractor(html)

    results[file_id] = {'articleBody': extracted_text}

# Save to output directory
with open('output/my-extractor.json', 'w') as f:
    json.dump(results, f)
```

### 2. Output Format

Your output JSON must have this structure:

```json
{
  "0001": {"articleBody": "Extracted text for file 0001..."},
  "0002": {"articleBody": "Extracted text for file 0002..."},
  ...
}
```

- Keys must match the file IDs (e.g., `0001`, `0002`)
- Each entry must have an `articleBody` field with the extracted text

### 3. Evaluate

```bash
python evaluate.py
```

Output:
```
Extractor                F1             Precision      Recall         Accuracy
--------------------------------------------------------------------------------
my-extractor             0.945 +/- 0.008  0.932 +/- 0.010  0.958 +/- 0.007  0.215 +/- 0.030
```

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Precision** | Fraction of extracted content that matches ground truth |
| **Recall** | Fraction of ground truth content that was extracted |
| **F1 Score** | Harmonic mean of precision and recall |
| **Accuracy** | Exact match (extracted tokens == ground truth tokens) |

Metrics use **4-gram shingle matching** which accounts for word order. Bootstrap resampling provides confidence intervals (±).

### Additional Metrics

Run with `--snippets` to evaluate snippet coverage:

```bash
python evaluate.py --snippets
```

- **With%**: Percentage of "must include" sentences found in extraction
- **Without%**: Percentage of boilerplate found (lower is better)

## Command-Line Options

```bash
python evaluate.py [OPTIONS]

Options:
  --n-bootstrap N    Bootstrap iterations (default: 1000)
  --output FILE      Save results to JSON file
  --snippets         Include snippet coverage metrics
  --seed N           Random seed for reproducibility (default: 42)
```

## Directory Structure

```
benchmark/
├── README.md           # This file
├── LICENSE             # Apache 2.0
├── evaluate.py         # Evaluation script (zero dependencies)
├── ground-truth.json   # Ground truth annotations
├── html/               # HTML files (gzip-compressed)
│   ├── 0001.html.gz
│   ├── 0002.html.gz
│   └── ...
└── output/             # Put your extractor results here
    └── _example_format.json
```

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Methodology

Ground truth was generated using AI models (DeepSeek, MiniMax) with human review. The benchmark focuses on **article body extraction** - extracting the main content while excluding navigation, ads, and boilerplate.

### Dataset Filtering

Pages were filtered to exclude:
- Category/archive pages
- Shopping/product listing pages
- Directory pages
- Very short content (<500 characters)
- Pages where multiple extractors failed

### Comparison with ScrapingHub Benchmark

This benchmark uses the same evaluation methodology as the [ScrapingHub Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark), enabling direct comparison. Key differences:

| Aspect | ScrapingHub | This Benchmark |
|--------|-------------|----------------|
| Pages | 184 | 1,507 |
| Year | 2019 | 2025 |
| Ground Truth | Manual | AI + Review |
| Extra Metrics | No | Snippet coverage |

## License

Apache 2.0

## Citation

If you use this benchmark in your research, please cite:

```
@misc{web-content-extraction-benchmark,
  title={Web Content Extraction Benchmark},
  year={2025},
  url={https://github.com/user/web-content-extraction-benchmark}
}
```

## Acknowledgments

- Evaluation methodology based on [ScrapingHub Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark)
- Shingle matching approach from [Moz Content Extraction Benchmark](https://moz.com/devblog/benchmarking-python-content-extraction-algorithms-dragnet-readability-goose-and-eatiht/)

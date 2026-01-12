# Tau-Bench Analysis Workflow

This guide explains the two-step workflow for analyzing benchmark results and generating visualizations.

## Overview

The analysis has been separated into two scripts:
1. **`analyze_results.py`** - Calculates metrics and saves results
2. **`generate_figures.py`** - Generates visualizations from saved results

This separation allows you to:
- Calculate metrics once, regenerate figures multiple times
- Adjust figure parameters without re-entering model names
- Skip re-running expensive analysis when tweaking visualizations

## Step 1: Analyze Results

Run the analysis script to calculate metrics and save results:

```bash
python3 analyze_results.py results/model1.json results/model2.json --output analysis_dir
```

You'll be prompted to enter a model name for each file. The script will:
- Calculate Pass^k and Pass@k scores
- Calculate RDI (Retry Dependency Index)
- Analyze error tasks, action counts, and reward components
- Save results to:
  - `analysis_dir/analysis_results.json` (for figure generation)
  - `analysis_dir/individual_results/*.csv` (per-model metrics)
  - `analysis_dir/comparison_tables/*.csv` (multi-model comparisons)

### Options

- `--output DIR` - Custom output directory (default: `analysis_results`)
- `--no-csv` - Skip CSV output
- `--individual-only` - Skip multi-model comparison
- `--exclude-tasks IDS` - Comma-separated task IDs to exclude (e.g., `--exclude-tasks 5,23,72`)

### Excluding Tasks

If you've spotted errors in specific tasks, you can exclude them from the analysis:

```bash
python3 analyze_results.py results/*.json --exclude-tasks 5,23,72 --output analysis_clean
```

Excluded tasks are:
- Removed from all metric calculations (Pass^k, Pass@k, RDI, etc.)
- Not counted in error analysis or task-level comparisons
- Recorded in `analysis_results.json` for reference

## Step 2: Generate Figures

Generate visualizations from saved analysis results:

```bash
python3 generate_figures.py analysis_dir
```

This will create visualizations in `analysis_dir/visualizations/`:
- `pass_scores_comparison.png` - Pass^k vs Pass@k comparison
- `pass_curves_by_k.png` - Pass scores across k values
- `cost_vs_performance.png` - Cost efficiency scatter plot
- `latency_vs_performance.png` - Latency vs performance
- `success_by_action_count.png` - Success rate by task complexity
- `component_distribution_heatmap.png` - Reward component distribution
- `component_correlation_heatmap.png` - Component correlation matrix
- `cost_efficiency.png` - Performance per dollar
- `radar_comparison.png` - Multi-metric radar chart
- Task-level visualizations (if multiple models)

### Options

- `--output DIR` - Custom output directory for figures (default: same as analysis_dir)

## Workflow Benefits

### Iterate on Figures Without Re-analysis

```bash
# Step 1: Run analysis once (enter model names)
python3 analyze_results.py results/*.json --output my_analysis

# Step 2: Generate figures
python3 generate_figures.py my_analysis

# Later: Regenerate figures without re-entering model names
python3 generate_figures.py my_analysis --output my_figures_v2
```

### Modify Figure Generation

You can edit `generate_figures.py` to:
- Adjust plot styles, colors, sizes
- Add new visualizations
- Modify existing plots
- Change DPI or output format

Then regenerate figures without rerunning the analysis:

```bash
python3 generate_figures.py my_analysis
```

## Requirements

- **`analyze_results.py`** requires: `numpy`, `pandas`
- **`generate_figures.py`** requires: `numpy`, `pandas`, `matplotlib`, `seaborn`

## Example Complete Workflow

```bash
# Analyze three models
python3 analyze_results.py \
  results/base/model1.json \
  results/disambiguation/model2.json \
  results/hallucination/model3.json \
  --output analysis_v1

# Enter model names when prompted:
# - Model A
# - Model B  
# - Model C

# Generate initial figures
python3 generate_figures.py analysis_v1

# Review figures in analysis_v1/visualizations/

# Edit generate_figures.py to adjust plot styles

# Regenerate figures (no model name prompts!)
python3 generate_figures.py analysis_v1
```

## Data Format

The `analysis_results.json` file contains:
- `all_results` - Per-model metrics and analysis
- `task_analysis` - Task-level performance patterns
- `comparison_tables` - Multi-model comparison data

This JSON file is the bridge between analysis and visualization, allowing you to regenerate figures without recomputing metrics.

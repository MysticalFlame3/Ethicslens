import numpy as np
import pandas as pd
from scipy import stats
from audit.category_distribution import parse_categories


def test_severity_validation(df: pd.DataFrame, col_map: dict) -> dict:
    if 'severity_score' not in col_map or col_map['severity_score'] not in df.columns:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No severity_score column found.',
            'recommendations': ['Add a severity_score column with numeric scores (0-1) to enable validation.'],
            'reason': 'Missing severity_score column',
        }

    sev_col = col_map['severity_score']
    severity_series = pd.to_numeric(df[sev_col], errors='coerce').dropna()

    if len(severity_series) < 5:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Not enough valid severity scores for analysis.',
            'recommendations': ['Ensure severity_score column has sufficient numeric values.'],
            'reason': 'Insufficient data',
        }

    scores = severity_series.values.astype(float)
    mean_val = round(float(np.mean(scores)), 4)
    median_val = round(float(np.median(scores)), 4)
    std_val = round(float(np.std(scores)), 4)
    min_val = round(float(np.min(scores)), 4)
    max_val = round(float(np.max(scores)), 4)

    # KS test against uniform(0, 1)
    ks_stat, p_value = stats.kstest(scores, 'uniform')
    ks_stat = round(float(ks_stat), 4)
    p_value = round(float(p_value), 6)
    is_nonuniform = bool(p_value < 0.05)

    # Correlation with category count per sample
    corr = 0.0
    if 'categories' in col_map and col_map['categories'] in df.columns:
        cat_col = col_map['categories']
        valid_idx = severity_series.index
        cat_counts = df.loc[valid_idx, cat_col].apply(
            lambda v: len(parse_categories(v))
        )
        if cat_counts.std() > 0:
            corr_result = np.corrcoef(scores, cat_counts.values)
            corr = round(float(corr_result[0, 1]), 4) if not np.isnan(corr_result[0, 1]) else 0.0

    if is_nonuniform and abs(corr) < 0.7:
        score = 85
        status = 'good'
    elif is_nonuniform or abs(corr) < 0.7:
        score = 60
        status = 'warning'
    else:
        score = 35
        status = 'critical'

    # Histogram with bins [0.0, 0.1, ..., 0.9]
    bin_labels = [f'{i/10:.1f}' for i in range(10)]
    bin_counts = [0] * 10
    for s in scores:
        idx = min(int(s * 10), 9)
        bin_counts[idx] += 1

    chart_data = {
        'type': 'bar',
        'labels': bin_labels,
        'data': [int(c) for c in bin_counts],
    }

    recommendations = []
    if not is_nonuniform:
        recommendations.append(
            'Severity scores appear uniformly distributed (p >= 0.05). '
            'Consider reviewing scoring methodology for more meaningful differentiation.'
        )
    if abs(corr) >= 0.7:
        recommendations.append(
            f'High correlation ({corr}) between severity and category count. '
            'Scores may be mechanically derived rather than independently assessed.'
        )
    if std_val < 0.1:
        recommendations.append('Low standard deviation in severity scores suggests insufficient granularity.')
    if not recommendations:
        recommendations.append(
            'Severity scores show good distribution and independence. Validation passed.'
        )

    return {
        'score': score,
        'status': status,
        'metrics': {
            'total_valid_scores': int(len(scores)),
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'min': min_val,
            'max': max_val,
            'ks_statistic': ks_stat,
            'ks_p_value': p_value,
            'is_nonuniform': is_nonuniform,
            'correlation_with_category_count': corr,
        },
        'chart_data': chart_data,
        'description': (
            f'Validated {int(len(scores))} severity scores. '
            f'KS test p-value: {p_value} ({"non-uniform" if is_nonuniform else "uniform"}). '
            f'Mean: {mean_val}, Std: {std_val}.'
        ),
        'recommendations': recommendations,
    }

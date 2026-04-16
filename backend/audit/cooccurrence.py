import numpy as np
import pandas as pd
from collections import Counter
from audit.category_distribution import parse_categories


def test_cooccurrence(df: pd.DataFrame, col_map: dict) -> dict:
    if 'categories' not in col_map or col_map['categories'] not in df.columns:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No categories column found for co-occurrence analysis.',
            'recommendations': ['Add a categories column with multi-label annotations.'],
            'reason': 'Missing categories column',
        }

    cat_col = col_map['categories']
    all_cats_per_row = [parse_categories(val) for val in df[cat_col]]
    flat_all = [c for row in all_cats_per_row for c in row]

    if not flat_all:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Categories column is empty.',
            'recommendations': ['Ensure categories column contains valid data.'],
            'reason': 'Empty categories',
        }

    counter = Counter(flat_all)
    top20 = [cat for cat, _ in counter.most_common(20)]

    # Build binary indicator matrix
    matrix_rows = []
    for row_cats in all_cats_per_row:
        row_cats_set = set(row_cats)
        matrix_rows.append([1 if cat in row_cats_set else 0 for cat in top20])

    binary_matrix = np.array(matrix_rows, dtype=float)

    # Only keep columns with variance > 0
    variances = binary_matrix.var(axis=0)
    valid_mask = variances > 0
    valid_cats = [cat for cat, v in zip(top20, valid_mask) if v]
    binary_matrix = binary_matrix[:, valid_mask]

    if binary_matrix.shape[1] < 2:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Not enough category variance to compute co-occurrence.',
            'recommendations': ['Ensure dataset has multi-label samples with varying categories.'],
            'reason': 'Insufficient variance',
        }

    # Pearson correlation matrix
    corr_matrix = np.corrcoef(binary_matrix.T)
    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

    n = corr_matrix.shape[0]
    high_corr_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(corr_matrix[i, j]) > 0.8:
                high_corr_pairs += 1

    if high_corr_pairs < 10:
        score = 95
        status = 'excellent'
    elif high_corr_pairs < 20:
        score = 80
        status = 'good'
    elif high_corr_pairs < 50:
        score = 60
        status = 'warning'
    else:
        score = 30
        status = 'critical'

    rounded_matrix = [[round(float(corr_matrix[i][j]), 2) for j in range(n)] for i in range(n)]

    chart_data = {
        'type': 'heatmap',
        'labels': valid_cats,
        'matrix': rounded_matrix,
    }

    recommendations = []
    if high_corr_pairs >= 10:
        recommendations.append(
            f'{high_corr_pairs} category pairs show high correlation (|r|>0.8). Consider merging redundant categories.'
        )
    if high_corr_pairs >= 50:
        recommendations.append('Severe co-occurrence redundancy detected. Review annotation guidelines.')
    if not recommendations:
        recommendations.append('Category co-occurrence patterns look healthy. No redundancy detected.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'categories_analyzed': len(valid_cats),
            'high_correlation_pairs': int(high_corr_pairs),
            'correlation_threshold': 0.8,
            'total_pairs_checked': int(n * (n - 1) / 2),
        },
        'chart_data': chart_data,
        'description': (
            f'Analyzed co-occurrence patterns among top {len(valid_cats)} categories. '
            f'Found {high_corr_pairs} pairs with |r| > 0.8.'
        ),
        'recommendations': recommendations,
    }

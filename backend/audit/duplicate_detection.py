from hashlib import md5
import pandas as pd


def test_duplicates(df: pd.DataFrame, col_map: dict) -> dict:
    available_cols = [
        col_map[k]
        for k in ['text', 'response', 'label', 'categories', 'severity_score', 'explanation']
        if k in col_map and col_map[k] in df.columns
    ]

    if not available_cols:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No suitable columns found for duplicate detection.',
            'recommendations': ['Ensure dataset has at least one text or label column.'],
            'reason': 'No columns available',
        }

    fingerprints = df[available_cols].astype(str).apply(
        lambda row: md5('|'.join(row).encode('utf-8')).hexdigest(), axis=1
    )

    total = len(fingerprints)
    unique_count = int(fingerprints.nunique())
    duplicate_count = int(total - unique_count)
    duplicate_pct = round((duplicate_count / total) * 100, 2) if total > 0 else 0.0

    if duplicate_pct < 5:
        score = 100
        status = 'excellent'
    elif duplicate_pct < 10:
        score = 80
        status = 'good'
    elif duplicate_pct < 15:
        score = 60
        status = 'warning'
    else:
        score = 30
        status = 'critical'

    chart_data = {
        'type': 'pie',
        'labels': ['Unique', 'Duplicate'],
        'data': [unique_count, duplicate_count],
        'colors': ['#22c55e', '#ef4444'],
    }

    recommendations = []
    if duplicate_pct >= 5:
        recommendations.append(f'Remove {duplicate_count} duplicate records to improve dataset quality.')
    if duplicate_pct >= 15:
        recommendations.append('High duplication rate detected. Review data collection pipeline for errors.')
    if not recommendations:
        recommendations.append('Duplication rate is within acceptable bounds. No action needed.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'total_rows': total,
            'unique_count': unique_count,
            'duplicate_count': duplicate_count,
            'duplicate_pct': duplicate_pct,
            'columns_checked': available_cols,
        },
        'chart_data': chart_data,
        'description': (
            f'Analyzed {total} records across {len(available_cols)} columns. '
            f'Found {duplicate_count} duplicates ({duplicate_pct}% of dataset).'
        ),
        'recommendations': recommendations,
    }

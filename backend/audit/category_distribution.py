import ast
import pandas as pd
from collections import Counter


def parse_categories(val):
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if pd.isna(val):
        return []
    val_str = str(val).strip()
    if not val_str:
        return []
    # Try Python literal eval for lists like "['cat1', 'cat2']"
    if val_str.startswith('['):
        try:
            parsed = ast.literal_eval(val_str)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except (ValueError, SyntaxError):
            pass
    # Comma-separated
    if ',' in val_str:
        return [v.strip() for v in val_str.split(',') if v.strip()]
    return [val_str]


def test_category_distribution(df: pd.DataFrame, col_map: dict) -> dict:
    if 'categories' not in col_map or col_map['categories'] not in df.columns:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No categories column found in dataset.',
            'recommendations': ['Add a categories or labels column to enable distribution analysis.'],
            'reason': 'Missing categories column',
        }

    cat_col = col_map['categories']
    all_cats = []
    for val in df[cat_col]:
        all_cats.extend(parse_categories(val))

    if not all_cats:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Categories column is empty or could not be parsed.',
            'recommendations': ['Ensure categories column contains valid category data.'],
            'reason': 'Empty categories',
        }

    counter = Counter(all_cats)
    total_labeled = len(all_cats)

    rare_count = int(sum(1 for c in counter.values() if c < 10))
    dominant_count = int(sum(1 for c in counter.values() if c > 2000))

    top5 = counter.most_common(5)
    top5_concentration = round(sum(v for _, v in top5) / total_labeled * 100, 2) if total_labeled > 0 else 0.0

    if rare_count < 50 and top5_concentration < 60:
        score = 85
        status = 'good'
    elif rare_count < 100 or top5_concentration < 80:
        score = 60
        status = 'warning'
    else:
        score = 40
        status = 'critical'

    top20 = counter.most_common(20)
    chart_data = {
        'type': 'bar',
        'labels': [item[0] for item in top20],
        'data': [int(item[1]) for item in top20],
    }

    recommendations = []
    if rare_count > 0:
        recommendations.append(
            f'{rare_count} categories have fewer than 10 samples. Consider merging or collecting more data.'
        )
    if dominant_count > 0:
        recommendations.append(
            f'{dominant_count} categories dominate the dataset (>2000 samples). This may bias model training.'
        )
    if top5_concentration >= 60:
        recommendations.append(
            f'Top 5 categories account for {top5_concentration}% of labels. Consider balancing the distribution.'
        )
    if not recommendations:
        recommendations.append('Category distribution appears balanced. No action needed.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'total_category_instances': total_labeled,
            'unique_categories': int(len(counter)),
            'rare_categories': rare_count,
            'dominant_categories': dominant_count,
            'top5_concentration_pct': top5_concentration,
            'top_category': top20[0][0] if top20 else None,
            'top_category_count': int(top20[0][1]) if top20 else None,
        },
        'chart_data': chart_data,
        'description': (
            f'Analyzed {len(counter)} unique categories across {total_labeled} labeled instances. '
            f'Top 5 categories account for {top5_concentration}% of all labels.'
        ),
        'recommendations': recommendations,
    }

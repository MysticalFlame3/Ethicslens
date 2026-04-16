import pandas as pd
from audit.category_distribution import parse_categories


def test_class_balance(df: pd.DataFrame, col_map: dict) -> dict:
    has_label = 'label' in col_map and col_map['label'] in df.columns
    has_categories = 'categories' in col_map and col_map['categories'] in df.columns

    if not has_label:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No label column found for class balance analysis.',
            'recommendations': ['Add a label column (ethical/unethical or 0/1) to enable class balance analysis.'],
            'reason': 'Missing label column',
        }

    label_col = col_map['label']
    labels = df[label_col].astype(str).str.lower().str.strip()

    ethical_mask = labels.isin(['1', 'true', 'ethical', 'yes'])
    unethical_mask = labels.isin(['0', 'false', 'unethical', 'no'])

    ethical_count = int(ethical_mask.sum())
    unethical_count = int(unethical_mask.sum())

    if ethical_count == 0 and unethical_count == 0:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Could not identify ethical/unethical labels in label column.',
            'recommendations': [
                'Ensure label column uses: 1/0, true/false, ethical/unethical, or yes/no.'
            ],
            'reason': 'Unrecognized label values',
        }

    min_count = min(ethical_count, unethical_count) if min(ethical_count, unethical_count) > 0 else 1
    max_count = max(ethical_count, unethical_count)
    imbalance_ratio = round(max_count / min_count, 2)

    # Single-class categories
    single_class_count = 0
    if has_categories:
        cat_col = col_map['categories']
        ethical_cats = set()
        unethical_cats = set()

        for idx, row_cats in df[cat_col][ethical_mask].items():
            for c in parse_categories(row_cats):
                ethical_cats.add(c)

        for idx, row_cats in df[cat_col][unethical_mask].items():
            for c in parse_categories(row_cats):
                unethical_cats.add(c)

        ethical_only = ethical_cats - unethical_cats
        unethical_only = unethical_cats - ethical_cats
        single_class_count = int(len(ethical_only) + len(unethical_only))

    if imbalance_ratio < 1.5 and single_class_count < 20:
        score = 95
        status = 'excellent'
    elif imbalance_ratio < 2 and single_class_count < 40:
        score = 80
        status = 'good'
    elif imbalance_ratio < 3:
        score = 65
        status = 'warning'
    else:
        score = 45
        status = 'critical'

    chart_data = {
        'type': 'bar',
        'labels': ['Ethical', 'Unethical'],
        'data': [ethical_count, unethical_count],
    }

    recommendations = []
    if imbalance_ratio >= 1.5:
        majority_class = 'Ethical' if ethical_count > unethical_count else 'Unethical'
        recommendations.append(
            f'Class imbalance ratio of {imbalance_ratio}:1. '
            f'{majority_class} class is over-represented. '
            'Consider resampling or collecting more minority class samples.'
        )
    if single_class_count >= 20:
        recommendations.append(
            f'{single_class_count} categories appear in only one class. '
            'This may cause the model to learn class-specific features rather than ethical reasoning.'
        )
    if imbalance_ratio >= 3:
        recommendations.append(
            'Severe class imbalance detected. Model trained on this data may have poor minority class recall.'
        )
    if not recommendations:
        recommendations.append('Class balance is within acceptable bounds. Dataset looks well-balanced.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'ethical_count': ethical_count,
            'unethical_count': unethical_count,
            'total_labeled': ethical_count + unethical_count,
            'imbalance_ratio': imbalance_ratio,
            'single_class_categories': single_class_count,
            'has_category_analysis': has_categories,
        },
        'chart_data': chart_data,
        'description': (
            f'Found {ethical_count} ethical and {unethical_count} unethical samples '
            f'(imbalance ratio: {imbalance_ratio}:1). '
            f'{single_class_count} categories appear in only one class.'
        ),
        'recommendations': recommendations,
    }

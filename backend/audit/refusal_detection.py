import re
import pandas as pd


REFUSAL_PATTERNS = [
    "I cannot",
    "I'm not able to",
    "as an AI",
    "I must refuse",
    "it would be inappropriate",
    "I don't think it's appropriate",
    "I'm not comfortable",
    "against my guidelines",
    "I have to decline",
    "not something I can help with",
    "I wouldn't recommend",
    "this is not appropriate",
    "I can't assist",
    "I should not",
    "it's not ethical for me to",
]

PATTERN_REGEX = re.compile(
    '|'.join(re.escape(p) for p in REFUSAL_PATTERNS),
    re.IGNORECASE,
)


def _is_refusal(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    return bool(PATTERN_REGEX.search(text))


def test_refusal_detection(df: pd.DataFrame, col_map: dict) -> dict:
    if 'response' not in col_map or col_map['response'] not in df.columns:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No response column found for refusal detection.',
            'recommendations': ['Add a response/output column to enable refusal pattern analysis.'],
            'reason': 'Missing response column',
        }

    resp_col = col_map['response']
    df = df.copy()
    df['_is_refusal'] = df[resp_col].apply(_is_refusal)

    total = len(df)
    total_refusal_count = int(df['_is_refusal'].sum())
    total_refusal_pct = round(total_refusal_count / total * 100, 2) if total > 0 else 0.0

    ethical_clean = ethical_refusal = unethical_clean = unethical_refusal = 0

    has_label = 'label' in col_map and col_map['label'] in df.columns
    if has_label:
        label_col = col_map['label']
        df['_label_lower'] = df[label_col].astype(str).str.lower().str.strip()

        ethical_mask = df['_label_lower'].isin(['1', 'true', 'ethical', 'yes'])
        unethical_mask = df['_label_lower'].isin(['0', 'false', 'unethical', 'no'])

        ethical_df = df[ethical_mask]
        unethical_df = df[unethical_mask]

        ethical_refusal = int(ethical_df['_is_refusal'].sum())
        ethical_clean = int(len(ethical_df) - ethical_refusal)
        unethical_refusal = int(unethical_df['_is_refusal'].sum())
        unethical_clean = int(len(unethical_df) - unethical_refusal)

    if total_refusal_pct < 5:
        score = 100
        status = 'excellent'
    elif total_refusal_pct < 15:
        score = 85
        status = 'good'
    elif total_refusal_pct < 30:
        score = 65
        status = 'warning'
    else:
        score = 40
        status = 'critical'

    chart_data = {
        'type': 'bar',
        'labels': ['Ethical', 'Unethical'],
        'datasets': [
            {
                'label': 'Clean',
                'data': [ethical_clean, unethical_clean],
                'backgroundColor': '#22c55e',
            },
            {
                'label': 'Refusal',
                'data': [ethical_refusal, unethical_refusal],
                'backgroundColor': '#ef4444',
            },
        ],
    }

    recommendations = []
    if total_refusal_pct >= 5:
        recommendations.append(
            f'{total_refusal_count} responses ({total_refusal_pct}%) contain refusal patterns. '
            'Review whether these are appropriate for the dataset context.'
        )
    if total_refusal_pct >= 30:
        recommendations.append(
            'High refusal rate may indicate over-cautious model behavior or mislabeled data.'
        )
    if not recommendations:
        recommendations.append('Refusal rate is within acceptable bounds. Dataset responses look natural.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'total_responses': total,
            'refusal_count': total_refusal_count,
            'refusal_pct': total_refusal_pct,
            'ethical_clean': ethical_clean,
            'ethical_refusal': ethical_refusal,
            'unethical_clean': unethical_clean,
            'unethical_refusal': unethical_refusal,
            'has_label_breakdown': has_label,
        },
        'chart_data': chart_data,
        'description': (
            f'Scanned {total} responses for {len(REFUSAL_PATTERNS)} refusal patterns. '
            f'Found {total_refusal_count} refusals ({total_refusal_pct}% of responses).'
        ),
        'recommendations': recommendations,
    }

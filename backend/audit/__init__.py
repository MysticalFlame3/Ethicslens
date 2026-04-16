import pandas as pd
from audit.duplicate_detection import test_duplicates
from audit.category_distribution import test_category_distribution
from audit.cooccurrence import test_cooccurrence
from audit.refusal_detection import test_refusal_detection
from audit.lexical_diversity import test_lexical_diversity
from audit.explanation_consistency import test_explanation_consistency
from audit.severity_validation import test_severity_validation
from audit.class_balance import test_class_balance

COLUMN_MAPPINGS = {
    'text': ['text', 'prompt', 'input', 'question', 'scenario', 'content'],
    'response': ['response', 'output', 'answer', 'completion', 'reply'],
    'label': ['label', 'class', 'ethical', 'is_ethical', 'target', 'ethics_label'],
    'categories': ['categories', 'category', 'ethics_categories', 'labels', 'tags'],
    'severity_score': ['severity_score', 'severity', 'severity_level', 'risk_score'],
    'explanation': ['explanation', 'reason', 'rationale', 'justification'],
}

TEST_METADATA = {
    'duplicate_detection': 'Duplicate Detection',
    'category_distribution': 'Category Distribution',
    'cooccurrence': 'Category Co-occurrence',
    'refusal_detection': 'Refusal Detection',
    'lexical_diversity': 'Lexical Diversity',
    'explanation_consistency': 'Explanation Consistency',
    'severity_validation': 'Severity Validation',
    'class_balance': 'Class Balance',
}


def detect_columns(df: pd.DataFrame) -> dict:
    normalized = {col.lower().strip().replace(' ', '_'): col for col in df.columns}
    col_map = {}
    for field, candidates in COLUMN_MAPPINGS.items():
        for candidate in candidates:
            if candidate in normalized:
                col_map[field] = normalized[candidate]
                break
    return col_map


def _get_status_from_score(score):
    if score is None:
        return 'skipped'
    if score >= 85:
        return 'excellent'
    if score >= 70:
        return 'good'
    if score >= 50:
        return 'warning'
    return 'critical'


def run_all_tests(df: pd.DataFrame, col_map: dict) -> dict:
    test_functions = [
        ('duplicate_detection', test_duplicates),
        ('category_distribution', test_category_distribution),
        ('cooccurrence', test_cooccurrence),
        ('refusal_detection', test_refusal_detection),
        ('lexical_diversity', test_lexical_diversity),
        ('explanation_consistency', test_explanation_consistency),
        ('severity_validation', test_severity_validation),
        ('class_balance', test_class_balance),
    ]

    results = {}
    scores = []

    for test_key, test_fn in test_functions:
        try:
            result = test_fn(df, col_map)
            # Ensure status is consistent with score
            if 'score' in result and result['score'] is not None:
                result['status'] = _get_status_from_score(result['score'])
                scores.append(result['score'])
            elif 'status' not in result:
                result['status'] = 'skipped'
        except Exception as e:
            result = {
                'score': None,
                'status': 'skipped',
                'metrics': {},
                'chart_data': None,
                'description': f'Test failed with an unexpected error.',
                'recommendations': [f'Review data format. Error: {str(e)[:200]}'],
                'reason': str(e),
            }

        # Normalize result fields
        result.setdefault('metrics', {})
        result.setdefault('chart_data', None)
        result.setdefault('description', '')
        result.setdefault('recommendations', [])
        results[test_key] = result

    # Composite score
    composite = round(sum(scores) / len(scores), 1) if scores else None
    results['composite'] = composite

    return results

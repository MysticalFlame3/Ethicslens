import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from audit.category_distribution import parse_categories


def test_explanation_consistency(df: pd.DataFrame, col_map: dict) -> dict:
    has_categories = 'categories' in col_map and col_map['categories'] in df.columns
    has_explanation = 'explanation' in col_map and col_map['explanation'] in df.columns

    if not has_categories or not has_explanation:
        missing = []
        if not has_categories:
            missing.append('categories')
        if not has_explanation:
            missing.append('explanation')
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': f'Missing required columns: {", ".join(missing)}.',
            'recommendations': [
                'Add both categories and explanation columns to enable consistency analysis.'
            ],
            'reason': f'Missing columns: {", ".join(missing)}',
        }

    cat_col = col_map['categories']
    exp_col = col_map['explanation']

    work_df = df[[cat_col, exp_col]].dropna(subset=[exp_col]).copy()
    work_df['_exp_str'] = work_df[exp_col].astype(str).str.strip()
    work_df = work_df[work_df['_exp_str'].str.len() > 0].copy()

    if len(work_df) == 0:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Explanation column has no usable text.',
            'recommendations': ['Ensure explanation column contains non-empty text data.'],
            'reason': 'Empty explanation column',
        }

    # Sample for TF-IDF
    sample_df = work_df.sample(min(2000, len(work_df)), random_state=42)
    total = len(sample_df)

    # Circular detection: check if any category name appears verbatim in explanation
    def has_circular(row):
        cats = parse_categories(row[cat_col])
        exp_lower = row['_exp_str'].lower()
        for cat in cats:
            if cat.lower() in exp_lower:
                return True
        return False

    sample_df = sample_df.copy()
    sample_df['_circular'] = sample_df.apply(has_circular, axis=1)
    circular_count = int(sample_df['_circular'].sum())
    circular_pct = round(circular_count / total * 100, 2) if total > 0 else 0.0

    # TF-IDF cosine similarity between category string and explanation
    cat_strings = sample_df[cat_col].apply(
        lambda v: ' '.join(parse_categories(v)) if not isinstance(v, float) else ''
    ).tolist()
    exp_strings = sample_df['_exp_str'].tolist()

    combined = cat_strings + exp_strings
    try:
        vectorizer = TfidfVectorizer(max_features=10000, stop_words='english', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(combined)
    except ValueError:
        avg_similarity = 0.0
        high_sim_pct = 0.0
        similarities = []
    else:
        cat_vecs = tfidf_matrix[:total]
        exp_vecs = tfidf_matrix[total:]
        sims = []
        batch_size = 200
        for i in range(0, total, batch_size):
            batch_sims = cosine_similarity(
                cat_vecs[i:i + batch_size], exp_vecs[i:i + batch_size]
            ).diagonal()
            sims.extend(batch_sims.tolist())
        similarities = sims
        avg_similarity = round(float(np.mean(similarities)), 4) if similarities else 0.0
        high_sim_pct = round(
            sum(1 for s in similarities if s > 0.7) / len(similarities) * 100, 2
        ) if similarities else 0.0

    # Score
    if circular_pct < 30 and avg_similarity < 0.4:
        score = 95
        status = 'excellent'
    elif circular_pct < 50 and avg_similarity < 0.5:
        score = 75
        status = 'good'
    elif circular_pct < 70:
        score = 55
        status = 'warning'
    else:
        score = 30
        status = 'critical'

    # Histogram of similarity scores
    bins = [f'{i/10:.1f}-{(i+1)/10:.1f}' for i in range(10)]
    bin_counts = [0] * 10
    for s in similarities:
        idx = min(int(s * 10), 9)
        bin_counts[idx] += 1

    chart_data = {
        'type': 'bar',
        'labels': bins,
        'data': bin_counts,
    }

    recommendations = []
    if circular_pct >= 30:
        recommendations.append(
            f'{circular_pct}% of explanations contain category names verbatim. '
            'This suggests circular reasoning in annotations.'
        )
    if avg_similarity >= 0.5:
        recommendations.append(
            f'Average TF-IDF similarity of {avg_similarity} is high. '
            'Explanations may be too closely paraphrasing category labels.'
        )
    if high_sim_pct >= 20:
        recommendations.append(
            f'{high_sim_pct}% of explanations have >0.7 similarity to their category labels.'
        )
    if not recommendations:
        recommendations.append(
            'Explanations appear sufficiently independent from category labels. Good consistency.'
        )

    return {
        'score': score,
        'status': status,
        'metrics': {
            'total_analyzed': total,
            'circular_count': circular_count,
            'circular_pct': circular_pct,
            'avg_cosine_similarity': avg_similarity,
            'high_similarity_pct': high_sim_pct,
        },
        'chart_data': chart_data,
        'description': (
            f'Analyzed {total} explanation-category pairs. '
            f'{circular_pct}% contain circular reasoning. '
            f'Average TF-IDF similarity: {avg_similarity}.'
        ),
        'recommendations': recommendations,
    }

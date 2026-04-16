import math
import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer


def test_lexical_diversity(df: pd.DataFrame, col_map: dict) -> dict:
    if 'text' not in col_map or col_map['text'] not in df.columns:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'No text column found for lexical diversity analysis.',
            'recommendations': ['Add a text/prompt column to enable lexical diversity analysis.'],
            'reason': 'Missing text column',
        }

    text_col = col_map['text']
    texts = df[text_col].dropna().astype(str).tolist()

    if not texts:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {},
            'chart_data': None,
            'description': 'Text column is empty.',
            'recommendations': ['Ensure text column contains non-empty text data.'],
            'reason': 'Empty text column',
        }

    # Vocabulary and token counts
    all_tokens = []
    for t in texts:
        all_tokens.extend(t.lower().split())

    vocab_size = int(len(set(all_tokens)))
    total_tokens = int(len(all_tokens))

    # Sample for LDA
    sample_texts = texts[:10000] if len(texts) > 10000 else texts

    vectorizer = CountVectorizer(
        max_features=5000,
        stop_words='english',
        min_df=2,
    )
    try:
        doc_term_matrix = vectorizer.fit_transform(sample_texts)
    except ValueError:
        return {
            'score': None,
            'status': 'skipped',
            'metrics': {'vocab_size': vocab_size, 'total_tokens': total_tokens},
            'chart_data': None,
            'description': 'Could not build document-term matrix for LDA.',
            'recommendations': ['Ensure text data is diverse enough for topic modeling.'],
            'reason': 'Vectorizer failed',
        }

    n_topics = 10
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=10,
    )
    lda.fit(doc_term_matrix)
    topic_distributions = lda.transform(doc_term_matrix)
    dominant_topics = np.argmax(topic_distributions, axis=1)

    topic_counts = [int(np.sum(dominant_topics == i)) for i in range(n_topics)]
    total_docs = sum(topic_counts)

    # Normalized Shannon entropy
    entropy = 0.0
    if total_docs > 0:
        for count in topic_counts:
            if count > 0:
                p = count / total_docs
                entropy -= p * math.log(p)
        if n_topics > 1:
            entropy = entropy / math.log(n_topics)

    entropy = round(entropy, 4)

    if entropy > 0.8:
        score = 95
        status = 'excellent'
    elif entropy > 0.6:
        score = 80
        status = 'good'
    elif entropy > 0.4:
        score = 60
        status = 'warning'
    else:
        score = 40
        status = 'critical'

    chart_data = {
        'type': 'bar',
        'labels': [f'Topic {i + 1}' for i in range(n_topics)],
        'data': topic_counts,
    }

    recommendations = []
    if entropy < 0.4:
        recommendations.append(
            'Very low topical diversity. Dataset may be dominated by a single topic or theme.'
        )
    elif entropy < 0.6:
        recommendations.append(
            'Moderate topical diversity. Consider adding more varied examples to improve coverage.'
        )
    if vocab_size < 1000:
        recommendations.append('Small vocabulary detected. Dataset may lack linguistic variety.')
    if not recommendations:
        recommendations.append('Lexical and topical diversity are within acceptable ranges.')

    return {
        'score': score,
        'status': status,
        'metrics': {
            'vocab_size': vocab_size,
            'total_tokens': total_tokens,
            'type_token_ratio': round(vocab_size / total_tokens, 4) if total_tokens > 0 else 0.0,
            'num_documents': len(texts),
            'documents_sampled_for_lda': len(sample_texts),
            'normalized_entropy': entropy,
            'num_topics': n_topics,
        },
        'chart_data': chart_data,
        'description': (
            f'Analyzed {len(texts)} documents with {vocab_size} unique words and {total_tokens} total tokens. '
            f'LDA topic model shows normalized entropy of {entropy} across {n_topics} topics.'
        ),
        'recommendations': recommendations,
    }

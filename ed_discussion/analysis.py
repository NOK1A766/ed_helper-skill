"""Deterministic filters and rankings used by both interfaces."""

import pandas as pd


METRICS = {
    'views': 'View count',
    'likes': 'Like count',
    'replies': 'Reply number',
    'stars': 'Star count',
}


def filter_threads(threads, *, days=None, subcategory=None, status='all'):
    filtered = threads.copy()
    filtered['_answered'] = (
        filtered['Is answer resolved'].astype(str).str.strip().str.lower() == 'true'
    )
    filtered['_posted_at'] = pd.to_datetime(filtered['Thread time'], utc=True,
                                            errors='coerce')
    filtered['Thread subcategory'] = filtered['Thread subcategory'].fillna('Uncategorized')
    if days is not None:
        if days < 1:
            raise ValueError('days must be a positive number')
        cutoff = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=days)
        filtered = filtered[filtered['_posted_at'] >= cutoff]
    if subcategory and subcategory != 'All':
        filtered = filtered[filtered['Thread subcategory'] == subcategory]
    if status == 'answered':
        filtered = filtered[filtered['_answered']]
    elif status == 'unanswered':
        filtered = filtered[~filtered['_answered']]
    elif status != 'all':
        raise ValueError(f'Unknown answer status: {status}')
    return filtered.copy()


def rank_threads(threads, metric='views', top=15):
    if metric not in METRICS:
        raise ValueError(f'Unknown ranking metric: {metric}')
    if top < 1:
        raise ValueError('top must be a positive number')
    column = METRICS[metric]
    ranked = threads.copy()
    ranked[column] = pd.to_numeric(ranked[column], errors='coerce').fillna(0)
    return ranked.sort_values(column, ascending=False).head(top)

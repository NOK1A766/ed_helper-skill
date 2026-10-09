"""Compact, machine-readable data inspection for Codex chat."""

import argparse
import json

from .analysis import METRICS, filter_threads, rank_threads
from .store import load_current, load_view


def main(argv=None):
    parser = argparse.ArgumentParser(description='Inspect the current Ed Discussion dataset.')
    subcommands = parser.add_subparsers(dest='command', required=True)
    subcommands.add_parser('inspect', help='Show dataset source and row count')
    ranking = subcommands.add_parser('rank', help='Rank threads in the current dataset')
    ranking.add_argument('--metric', choices=METRICS, default='views')
    ranking.add_argument('--days', type=int)
    ranking.add_argument('--status', choices=('all', 'answered', 'unanswered'), default='all')
    ranking.add_argument('--subcategory')
    ranking.add_argument('--top', type=int, default=15)
    ranking.add_argument('--current-view', action='store_true',
                         help='Use the filters selected in the dashboard')
    args = parser.parse_args(argv)

    try:
        threads, metadata = load_current()
        if args.command == 'inspect':
            result = {'dataset': metadata, 'row_count': len(threads)}
        else:
            filters = {'days': args.days, 'status': args.status,
                       'subcategory': args.subcategory}
            if args.current_view:
                view = load_view()
                if not view or view.get('dataset_sha256') != metadata.get('sha256'):
                    raise ValueError('No matching current dashboard view is available.')
                filters = view['filters']
            filtered = filter_threads(threads, **filters)
            ranked = rank_threads(filtered, metric=args.metric, top=args.top)
            columns = ['Thread number', 'Thread title', 'Thread time',
                       'Thread category', 'Thread subcategory', 'View count',
                       'Like count', 'Star count', 'Reply number',
                       'Is answer resolved', 'Thread url']
            result = {
                'dataset': metadata,
                'filters': filters,
                'matching_threads': len(filtered),
                'ranked_by': args.metric,
                'threads': ranked[columns].where(ranked[columns].notna(), None)
                                 .to_dict(orient='records'),
            }
        print(json.dumps(result, ensure_ascii=False, default=str, indent=2))
    except (FileNotFoundError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt


CSV_PATH = Path(__file__).with_name('threads.csv')
TOP_N = 15
ANSWERED_COLOR = '#2E8B57'
UNANSWERED_COLOR = '#D88632'


def draw_ranking(rows, column, chart_title, x_label, output_path):
    top_threads = sorted(rows, key=lambda item: int(item[column]), reverse=True)[:TOP_N]

    labels = []
    values = []
    colors = []
    statuses = []
    for item in top_threads:
        answered = item['Is answer resolved'].strip().lower() == 'true'
        status = 'Answered' if answered else 'Unanswered'
        title = item['Thread title'].strip()
        if len(title) > 40:
            title = title[:37] + '...'
        posted_date = item['Thread time'][:10]
        labels.append(f"{title} (#{item['Thread number']}) — {posted_date}")
        values.append(int(item[column]))
        colors.append(ANSWERED_COLOR if answered else UNANSWERED_COLOR)
        statuses.append(status)

    fig, ax = plt.subplots(figsize=(13, max(5, len(top_threads) * 0.55)))
    bars = ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.bar_label(bars, padding=3)
    for bar, status in zip(bars, statuses):
        ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
                status, ha='center', va='center', color='white', fontweight='bold')
    ax.margins(x=0.12)
    ax.set_title(chart_title)
    ax.set_xlabel(x_label)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create top-thread PNG charts from a threads CSV.')
    parser.add_argument('--input', type=Path, default=CSV_PATH, help='Input CSV (default: threads.csv)')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).parent, help='Directory for PNG charts')
    args = parser.parse_args(argv)
    if not args.input.is_file():
        parser.error(f'CSV not found: {args.input}. Fetch data or use --input examples/sample_threads.csv')
    with open(args.input, encoding='utf-8-sig', newline='') as file:
        rows = list(csv.DictReader(file))
    if not rows:
        parser.error('The CSV contains no threads')
    required = {'Thread title', 'Thread number', 'Thread time', 'Is answer resolved',
                'View count', 'Reply number', 'Like count'}
    missing = required - rows[0].keys()
    if missing:
        parser.error('Missing CSV columns: ' + ', '.join(sorted(missing)))

    args.output_dir.mkdir(parents=True, exist_ok=True)

    draw_ranking(rows, 'View count', 'Top threads by views', 'Views', args.output_dir / 'views_top15.png')
    draw_ranking(rows, 'Reply number', 'Top threads by replies', 'Replies', args.output_dir / 'replies_top15.png')
    draw_ranking(rows, 'Like count', 'Top threads by likes', 'Likes', args.output_dir / 'likes_top15.png')
    print(f'Saved three charts to {args.output_dir}')


if __name__ == '__main__':
    main()

import csv
from pathlib import Path

import matplotlib.pyplot as plt


CSV_PATH = Path(__file__).with_name('threads.csv')
TOP_N = 15
ANSWERED_COLOR = '#2E8B57'
UNANSWERED_COLOR = '#D88632'


def draw_ranking(rows, column, chart_title, x_label, output_name):
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

    fig, ax = plt.subplots(figsize=(13, 8))
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
    fig.savefig(Path(__file__).with_name(output_name), dpi=150, bbox_inches='tight')
    plt.close(fig)


def main():
    with open(CSV_PATH, encoding='utf-8-sig', newline='') as file:
        rows = list(csv.DictReader(file))

    draw_ranking(rows, 'View count', 'Top threads by views', 'Views', 'views_top15.png')
    draw_ranking(rows, 'Reply number', 'Top threads by replies', 'Replies', 'replies_top15.png')
    draw_ranking(rows, 'Like count', 'Top threads by likes', 'Likes', 'likes_top15.png')
    print('Saved views_top15.png, replies_top15.png, and likes_top15.png')


if __name__ == '__main__':
    main()

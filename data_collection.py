import os
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
import time

COURSE_ID = 36387
PAGE_SIZE = 30
FILTER_DAYS = (7, 14, 30)
CSV_PATH = Path(__file__).with_name('threads.csv')


def get_data(offset):
    api_token = os.getenv('ED_API_TOKEN')
    if not api_token:
        raise RuntimeError('Set the ED_API_TOKEN environment variable before running the script.')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36',
        'Authorization': f'Bearer {api_token}',
    }
    params = {
        'limit': PAGE_SIZE,
        'offset': offset,
        'sort': 'new',
    }
    url = f'https://edstem.org/api/courses/{COURSE_ID}/threads'
    response = requests.get(url=url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    threads = response.json()['threads']
    if not isinstance(threads, list):
        raise ValueError('The Ed API response does not contain a list of threads.')
    return threads


def init_csv(writer):
    writer.writerow([
        'Thread id', 'Thread number', 'Thread type', 'Thread title', 'Thread content',
        'Thread category', 'Thread subcategory', 'View count', 'Like count',
        'Star count', 'Reply number', 'Is answer resolved',
        'Thread time', 'Updated time', 'Thread url',
    ])


def save_csv(all_threads, path=CSV_PATH):
    with open(path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        init_csv(writer)
        for item in all_threads:
            tid = item['id']
            thread_number = item['number']
            thread_type = item.get('type', '')
            title = item.get('title', '')
            document = item.get('document', '')
            category = item.get('category', '')
            subcategory = item.get('subcategory', '')
            view_count = item.get('view_count', 0)
            vote_count = item.get('vote_count', 0)
            star_count = item.get('star_count', 0)
            reply_count = item.get('reply_count', 0)
            is_answered = item.get('is_answered', False)
            created_time = item.get('created_at', '')
            updated_time = item.get('updated_at', '')
            detail_url = f'https://edstem.org/au/courses/{COURSE_ID}/discussion/{tid}'

            writer.writerow([
                tid, thread_number, thread_type, title, document, category, subcategory,
                view_count, vote_count, star_count, reply_count, is_answered,
                created_time, updated_time, detail_url,
            ])


def main():
    all_threads = []
    page = 0
    while True:
        offset = page * PAGE_SIZE
        items = get_data(offset)
        print(f'Page {page + 1}: received {len(items)} threads')
        if not items:
            break

        all_threads.extend(items)
        if len(items) < PAGE_SIZE:
            break

        page += 1
        time.sleep(1)

    if not all_threads:
        print('No threads were retrieved. The existing CSV was not changed.')
        return

    save_csv(all_threads)
    print(f'Saved {len(all_threads)} threads to {CSV_PATH}')


# ai
    now = datetime.now(timezone.utc)
    for days in FILTER_DAYS:
        cutoff = now - timedelta(days=days)
        recent_threads = []
        for item in all_threads:
            try:
                created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
            except (KeyError, TypeError, ValueError):
                continue
            if created_at.tzinfo and cutoff <= created_at.astimezone(timezone.utc) <= now:
                recent_threads.append(item)

        recent_path = CSV_PATH.with_name(f'threads_{days}d.csv')
        save_csv(recent_threads, recent_path)
        print(f'Saved {len(recent_threads)} threads from the last {days} days to {recent_path}')


if __name__ == '__main__':
    main()

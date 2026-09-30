import os
import csv
import tempfile
from pathlib import Path
import requests
import time

COURSE_ID = 36387
PAGE_SIZE = 30
PAGE_COUNT = 3
CSV_PATH = Path(__file__).with_name('threads.csv')



def get_data(offset):
    api_token = os.getenv('ED_API_TOKEN')
    if not api_token:
        raise RuntimeError('请先设置 ED_API_TOKEN 环境变量，再运行脚本。')

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
        raise ValueError('Ed API 返回的 threads 不是列表。')
    return threads


def init_csv(writer):
    writer.writerow([
        'Thread id', 'Thread type', 'Thread title', 'Thread content',
        'Thread category', 'Thread subcategory', 'View count', 'Like count',
        'Star count', 'Reply number', 'Is answer resolved',
        'Thread time', 'Updated time', 'Thread url',
    ])

def save_csv(all_threads):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', encoding='utf-8', newline='',
            dir=CSV_PATH.parent, prefix='threads-', suffix='.tmp', delete=False,
        ) as file:
            temporary_path = Path(file.name)
            writer = csv.writer(file)
            init_csv(writer)
            for item in all_threads:
                writer.writerow([
                    item['id'],
                    item.get('type', ''),
                    item.get('title', ''),
                    item.get('document', ''),
                    item.get('category', ''),
                    item.get('subcategory', ''),
                    item.get('view_count', 0),
                    item.get('vote_count', 0),
                    item.get('star_count', 0),
                    item.get('reply_count', 0),
                    item.get('is_answered', False),
                    item.get('created_at', ''),
                    item.get('updated_at', ''),
                    f'https://edstem.org/au/courses/{COURSE_ID}/discussion/{item["id"]}',
                ])
        os.replace(temporary_path, CSV_PATH)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def main():
    all_threads = []
    seen_ids = set()
    for page in range(PAGE_COUNT):
        offset = page * PAGE_SIZE
        items = get_data(offset)
        print(f'第 {page + 1} 页：返回 {len(items)} 条帖子')
        if not items:
            break

        for item in items:
            if item['id'] not in seen_ids:
                seen_ids.add(item['id'])
                all_threads.append(item)

        if page + 1 < PAGE_COUNT:
            time.sleep(1)

    if not all_threads:
        print('没有取得帖子，现有 CSV 未改动。')
        return

    save_csv(all_threads)
    print(f'已保存 {len(all_threads)} 条帖子到 {CSV_PATH}')


if __name__ == '__main__':
    main()

import os

import requests

def main():
    get_data()

def get_data():
    api_token = os.getenv('ED_API_TOKEN')
    if not api_token:
        raise RuntimeError('请先设置 ED_API_TOKEN 环境变量，再运行脚本。')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36',
        'Authorization': f'Bearer {api_token}',
    }
    params = {
        'limit': 30,
        'offset': 0,
        'sort': "new",
    }
    url = 'https://edstem.org/api/courses/36387/threads'
    response = requests.get(url=url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    res = response.json()
    items = res['threads']
    # loop through every threads
    for item in items:
        type = item['type']     # string
        title = item['title']    # string
        document = item['document']     #string
        category = item['category']     # string
        subcategory = item['subcategory']       # string
        view_count = item['view_count']     # int
        vote_count = item['vote_count']     # int
        reply_count = item['reply_count']   # int
        is_answered = item['is_answered']   # boolean
        created_time = item['created_at']   # time
        updated_time = item['updated_at']   # time
        tid = item['id']
        detail_url = f'https://edstem.org/au/courses/36387/discussion/{tid}'
        print(title, subcategory, view_count)

def init_csv():
    pass

def save_csv():
    pass


if __name__ == '__main__':
    main()


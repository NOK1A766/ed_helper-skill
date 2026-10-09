import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from app import fetch_course, threads_to_table
from ed_discussion.analysis import filter_threads, rank_threads
from ed_discussion.store import DATA_DIR, load_current, load_view, save_dataset, save_view


def sample_threads():
    recent = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    return pd.DataFrame([
        {'Thread number': 1, 'Thread title': 'Needs help', 'Thread time': recent,
         'Thread category': 'Questions', 'Thread subcategory': 'Homework',
         'View count': '20', 'Like count': 2, 'Star count': 0, 'Reply number': 3,
         'Is answer resolved': False, 'Thread url': 'https://example.test/1',
         'Thread content': 'Question'},
        {'Thread number': 2, 'Thread title': 'Old answer', 'Thread time': old,
         'Thread category': 'Questions', 'Thread subcategory': 'Homework',
         'View count': '100', 'Like count': 4, 'Star count': 1, 'Reply number': 5,
         'Is answer resolved': True, 'Thread url': 'https://example.test/2',
         'Thread content': 'Answer'},
    ])


class DatasetTests(unittest.TestCase):
    def test_saved_dataset_can_be_reused_without_changing_load_time(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=DATA_DIR) as directory:
            data_dir = Path(directory)
            threads = sample_threads()
            first = save_dataset(threads, 'upload', filename='course.csv', data_dir=data_dir)
            second = save_dataset(threads, 'upload', filename='course.csv', data_dir=data_dir)
            loaded, metadata = load_current(data_dir=data_dir, allow_legacy=False)
            self.assertEqual(first, second)
            self.assertEqual(metadata['row_count'], 2)
            self.assertEqual(len(loaded), 2)
            self.assertNotIn('token', (data_dir / 'metadata.json').read_text().lower())

            save_view({'days': 7, 'subcategory': None, 'status': 'unanswered'},
                      first['sha256'], data_dir=data_dir)
            self.assertEqual(load_view(data_dir=data_dir)['dataset_sha256'], first['sha256'])

    def test_recent_unanswered_ranking_uses_numeric_counts(self):
        filtered = filter_threads(sample_threads(), days=7, status='unanswered')
        ranked = rank_threads(filtered, metric='views', top=5)
        self.assertEqual(ranked['Thread number'].tolist(), [1])
        self.assertEqual(ranked['View count'].tolist(), [20])

    def test_mocked_ed_fetch_saves_threads_without_token(self):
        item = {'id': 123, 'number': 1, 'title': 'Synthetic Ed thread',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'view_count': 9, 'vote_count': 2, 'reply_count': 1,
                'is_answered': False}
        with patch('app.get_data', return_value=[item]) as request:
            threads = fetch_course(77, 'unit-test-token')
        request.assert_called_once_with(0, course_id=77, api_token='unit-test-token')
        table = threads_to_table(threads, 77)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=DATA_DIR) as directory:
            data_dir = Path(directory)
            metadata = save_dataset(table, 'ed', course_id=77, data_dir=data_dir)
            self.assertEqual(metadata['source'], 'ed')
            self.assertEqual(metadata['course_id'], 77)
            self.assertEqual(metadata['row_count'], 1)
            self.assertNotIn('unit-test-token', (data_dir / 'current.csv').read_text())
            self.assertNotIn('unit-test-token', (data_dir / 'metadata.json').read_text())


if __name__ == '__main__':
    unittest.main()

"""Private local dataset shared by Streamlit and the Codex skill."""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / '.local' / 'ed-discussion'
CURRENT_CSV = DATA_DIR / 'current.csv'
METADATA_JSON = DATA_DIR / 'metadata.json'
VIEW_JSON = DATA_DIR / 'view.json'
REQUIRED_COLUMNS = (
    'Thread number', 'Thread title', 'Thread time', 'Thread category',
    'Thread subcategory', 'View count', 'Like count', 'Star count',
    'Reply number', 'Is answer resolved', 'Thread url', 'Thread content',
)


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        return None


def _atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f'.{path.name}.',
                                         delete=False) as file:
            temporary = Path(file.name)
            file.write(data)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def validate_dataset(threads):
    missing = [column for column in REQUIRED_COLUMNS if column not in threads.columns]
    if missing:
        raise ValueError('The CSV is missing columns: ' + ', '.join(missing))
    if threads.empty:
        raise ValueError('The CSV contains no threads.')


def save_dataset(threads, source, *, filename=None, course_id=None, data_dir=DATA_DIR):
    """Save a validated dataset only when its content or source changes."""
    validate_dataset(threads)
    data_dir = Path(data_dir)
    csv_path = data_dir / 'current.csv'
    metadata_path = data_dir / 'metadata.json'
    content = threads.to_csv(index=False).encode('utf-8-sig')
    digest = hashlib.sha256(content).hexdigest()
    previous = _read_json(metadata_path)
    identity = {'sha256': digest, 'source': source, 'filename': filename,
                'course_id': course_id}
    if csv_path.is_file() and previous and all(previous.get(key) == value
                                                for key, value in identity.items()):
        return previous

    metadata = {
        **identity,
        'row_count': len(threads),
        'loaded_at': datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write(csv_path, content)
    _atomic_write(metadata_path, json.dumps(metadata, indent=2).encode('utf-8'))
    return metadata


def save_view(filters, dataset_sha256, *, data_dir=DATA_DIR):
    """Record the browser's selected filters for 'current page' questions."""
    view_path = Path(data_dir) / 'view.json'
    view = {'dataset_sha256': dataset_sha256, 'filters': filters}
    if _read_json(view_path) != view:
        _atomic_write(view_path, json.dumps(view, indent=2).encode('utf-8'))
    return view


def load_current(*, data_dir=DATA_DIR, allow_legacy=True):
    """Return the active CSV and metadata; support the existing threads.csv."""
    data_dir = Path(data_dir)
    csv_path = data_dir / 'current.csv'
    metadata = _read_json(data_dir / 'metadata.json')
    if csv_path.is_file() and metadata:
        threads = pd.read_csv(csv_path)
        validate_dataset(threads)
        return threads, metadata
    legacy_path = PROJECT_ROOT / 'threads.csv'
    if allow_legacy and legacy_path.is_file():
        threads = pd.read_csv(legacy_path)
        validate_dataset(threads)
        return threads, {
            'source': 'local', 'filename': legacy_path.name, 'course_id': None,
            'row_count': len(threads),
            'loaded_at': datetime.fromtimestamp(legacy_path.stat().st_mtime,
                                                timezone.utc).isoformat(),
        }
    raise FileNotFoundError('No current dataset. Upload a CSV or fetch a course in the dashboard.')


def load_view(*, data_dir=DATA_DIR):
    return _read_json(Path(data_dir) / 'view.json')

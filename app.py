import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

from data_collection import PAGE_SIZE, get_data


CSV_PATH = Path(__file__).with_name('threads.csv')
SAMPLE_PATH = Path(__file__).parent / 'examples' / 'sample_threads.csv'
REQUIRED_COLUMNS = (
    'Thread number', 'Thread title', 'Thread time', 'Thread category',
    'Thread subcategory', 'View count', 'Like count', 'Star count',
    'Reply number', 'Is answer resolved', 'Thread url', 'Thread content',
)
METRICS = {
    'Views': 'View count',
    'Likes': 'Like count',
    'Replies': 'Reply number',
    'Stars': 'Star count',
}
ANSWERED_COLOR = '#2E8B57'
UNANSWERED_COLOR = '#D88632'


def fetch_course(course_id, token):
    threads = []
    page = 0
    while True:
        items = get_data(page * PAGE_SIZE, course_id=course_id, api_token=token)
        if not items:
            break
        threads.extend(items)
        if len(items) < PAGE_SIZE:
            break
        page += 1
        time.sleep(1)
    return threads


def threads_to_table(threads, course_id):
    return pd.DataFrame([{
        'Thread id': item['id'],
        'Thread number': item['number'],
        'Thread type': item.get('type', ''),
        'Thread title': item.get('title', ''),
        'Thread content': item.get('document', ''),
        'Thread category': item.get('category', ''),
        'Thread subcategory': item.get('subcategory', ''),
        'View count': item.get('view_count', 0),
        'Like count': item.get('vote_count', 0),
        'Star count': item.get('star_count', 0),
        'Reply number': item.get('reply_count', 0),
        'Is answer resolved': item.get('is_answered', False),
        'Thread time': item.get('created_at', ''),
        'Updated time': item.get('updated_at', ''),
        'Thread url': f"https://edstem.org/au/courses/{course_id}/discussion/{item['id']}",
    } for item in threads])


def ranking_figure(threads, metric, top_n):
    ranked = threads.sort_values(metric, ascending=False).head(top_n)
    labels = []
    values = []
    colors = []
    statuses = []
    for _, item in ranked.iterrows():
        title = str(item['Thread title']).strip()
        if len(title) > 40:
            title = title[:37] + '...'
        posted_date = str(item['Thread time'])[:10]
        labels.append(f"{title} (#{item['Thread number']}) — {posted_date}")
        values.append(item[metric])
        answered = item['_answered']
        colors.append(ANSWERED_COLOR if answered else UNANSWERED_COLOR)
        statuses.append('Answered' if answered else 'Unanswered')

    fig, ax = plt.subplots(figsize=(12, max(5, len(ranked) * 0.55)))
    bars = ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.bar_label(bars, padding=3)
    for bar, status in zip(bars, statuses):
        if bar.get_width() > 0:
            ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
                    status, ha='center', va='center', color='white', fontweight='bold')
    ax.margins(x=0.12)
    ax.set_xlabel(metric)
    fig.tight_layout()
    return fig


def main():
    st.set_page_config(page_title='Ed Discussion Dashboard', layout='wide')
    st.title('Ed Discussion Dashboard')

    sources = ['Sample data', 'Upload CSV', 'Fetch from Ed']
    if CSV_PATH.exists():
        sources.insert(1, 'Local threads.csv')
    source = st.sidebar.radio('Data source', sources)
    if source == 'Sample data':
        threads = pd.read_csv(SAMPLE_PATH)
        # Keep the example useful for the relative date filters in future years.
        now = pd.Timestamp.now(tz='UTC')
        threads['Thread time'] = [(now - pd.Timedelta(days=i)).isoformat() for i in range(len(threads))]
        st.caption('Fictional example data. Choose another source to view your course.')
    elif source == 'Local threads.csv':
        threads = pd.read_csv(CSV_PATH)
        st.caption(f'Data source: {CSV_PATH.name}')
    elif source == 'Upload CSV':
        uploaded = st.sidebar.file_uploader('Choose a threads CSV', type='csv')
        if uploaded is None:
            st.info('Upload a CSV created by data_collection.py or with the same columns as the sample.')
            st.stop()
        try:
            threads = pd.read_csv(uploaded)
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
            st.error(f'Could not read the CSV: {error}')
            st.stop()
        st.caption(f'Data source: {uploaded.name}')
    else:
        with st.sidebar.form('ed_fetch', clear_on_submit=True, enter_to_submit=False):
            course_id = st.text_input('Course ID').strip()
            token = st.text_input('Ed API token', type='password', autocomplete='off')
            submitted = st.form_submit_button('Fetch course')
        if submitted:
            if not course_id.isdigit() or int(course_id) < 1:
                st.warning('Enter a positive numeric course ID.')
            elif not token:
                st.warning('Enter an Ed API token.')
            else:
                course_id = int(course_id)
                try:
                    with st.spinner('Fetching course threads...'):
                        items = fetch_course(course_id, token)
                    if items:
                        st.session_state['course_threads'] = threads_to_table(items, course_id)
                        st.success(f'Loaded {len(items)} threads from course {course_id}.')
                    else:
                        st.warning('No threads were found in this course.')
                except requests.HTTPError as error:
                    st.error(f'Ed returned HTTP {error.response.status_code}. Check the token and course access.')
                except requests.RequestException:
                    st.error('Could not reach Ed. Check the network connection.')
        if 'course_threads' not in st.session_state:
            st.info('Enter a course ID and API token, then select Fetch course.')
            st.stop()
        threads = st.session_state['course_threads'].copy()
        st.caption('Data source: Ed API (this browser session)')
        st.download_button(
            'Download fetched CSV', threads.to_csv(index=False).encode('utf-8-sig'),
            file_name='threads.csv', mime='text/csv',
        )

    missing = [column for column in REQUIRED_COLUMNS if column not in threads.columns]
    if missing:
        st.error('The CSV is missing columns: ' + ', '.join(missing))
        st.stop()

    threads['_answered'] = (
        threads['Is answer resolved'].astype(str).str.lower() == 'true'
    )
    threads['_posted_at'] = pd.to_datetime(threads['Thread time'], utc=True, errors='coerce')
    threads['Thread subcategory'] = threads['Thread subcategory'].fillna('Uncategorized')

    period = st.sidebar.selectbox('Time range', ['All', 'Last 7 days', 'Last 14 days', 'Last 30 days'])
    metric_name = st.sidebar.selectbox('Rank by', list(METRICS))
    top_n = st.sidebar.selectbox('Top threads', [10, 15], index=1)
    subcategories = ['All'] + sorted(threads['Thread subcategory'].unique().tolist())
    subcategory = st.sidebar.selectbox('Subcategory', subcategories)
    answer_status = st.sidebar.selectbox('Answer status', ['All', 'Answered', 'Unanswered'])

    filtered = threads.copy()
    if period != 'All':
        days = int(period.split()[1])
        filtered = filtered[filtered['_posted_at'] >= pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=days)]
    if subcategory != 'All':
        filtered = filtered[filtered['Thread subcategory'] == subcategory]
    if answer_status != 'All':
        filtered = filtered[filtered['_answered'] == (answer_status == 'Answered')]

    metric = METRICS[metric_name]
    filtered[metric] = pd.to_numeric(filtered[metric], errors='coerce').fillna(0)
    st.metric('Threads in this view', len(filtered))
    if filtered.empty:
        st.info('No threads match the selected filters.')
        return

    st.subheader(f'Top {min(top_n, len(filtered))} threads by {metric_name.lower()}')
    figure = ranking_figure(filtered, metric, top_n)
    st.pyplot(figure)
    plt.close(figure)

    st.subheader('Threads')
    columns = [
        'Thread number', 'Thread title', 'Thread time', 'Thread category',
        'Thread subcategory', 'View count', 'Like count', 'Star count',
        'Reply number', 'Is answer resolved', 'Thread url', 'Thread content',
    ]
    display_threads = filtered.sort_values(metric, ascending=False)[columns].copy()
    display_threads['Thread time'] = (
        display_threads['Thread time'].astype(str).str.replace('T', ' ', regex=False).str[:16]
    )
    st.dataframe(
        display_threads,
        hide_index=True,
        width='stretch',
        column_config={'Thread url': st.column_config.LinkColumn('Open in Ed')},
    )


if __name__ == '__main__':
    main()

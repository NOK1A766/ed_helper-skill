import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

from data_collection import PAGE_SIZE, get_data


CSV_PATH = Path(__file__).with_name('threads.csv')
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


def select_source(source):
    st.session_state['data_source'] = source


def show_guide():
    st.caption('GETTING STARTED')
    st.title('Ed Discussion Dashboard')
    st.write(
        'Load your course discussions, explore the most active threads, '
        'and find questions that still need an answer.'
    )

    st.subheader('1. Choose how to load your data')
    st.write('Pick the path that matches what you already have.')
    csv_col, ed_col = st.columns(2)
    with csv_col, st.container(border=True):
        st.markdown('**I have a CSV file**')
        st.caption('Upload a threads CSV exported from this dashboard or the collection script.')
        st.button('Upload CSV →', on_click=select_source, args=('Upload CSV',))
    with ed_col, st.container(border=True):
        st.markdown('**I have Ed access**')
        st.caption('Enter your course ID and your own Ed API token to fetch threads.')
        st.button('Fetch from Ed →', on_click=select_source, args=('Fetch from Ed',))
    if CSV_PATH.exists():
        st.caption('Already saved threads.csv in this folder? Select Local threads.csv in the sidebar.')

    st.subheader('2. Check the input')
    st.write('The dashboard checks your data before showing charts. Keep your token private.')
    id_col, format_col = st.columns(2)
    with id_col:
        st.markdown('**Course ID**')
        st.caption('The number after /courses/ in your Ed course URL. Use a course you can access.')
    with format_col:
        st.markdown('**CSV format**')
        st.caption('Use the column headers shown in examples/sample_threads.csv.')
    with st.expander('Required CSV columns'):
        st.write(', '.join(REQUIRED_COLUMNS))
        st.caption('Thread time should contain a date and time. Count columns should contain numbers.')

    st.subheader('3. Explore and save results')
    st.write(
        'Once data is loaded, use the sidebar to choose a time range, ranking metric, '
        'subcategory, and answer status. The chart ranks the top threads; the table '
        'shows the matching discussions and links back to Ed.'
    )
    st.write(
        'After fetching from Ed, select **Download fetched CSV** to save a copy. '
        'The fetched data otherwise stays in this browser session.'
    )

    st.divider()
    st.subheader('If something goes wrong')
    st.markdown(
        '- **Ed returns HTTP 401 or 403:** Check your token and course access.\n'
        '- **CSV columns are missing:** Compare the headers with `examples/sample_threads.csv`.\n'
        '- **No threads match the filters:** Change **Time range** to **All**.\n'
        '- **Connection error:** Check your network and try again.'
    )


def show_ed_setup_guide():
    st.subheader('Connect your Ed course')

    st.markdown('**1. Find your course ID**')
    st.write(
        'Open your course in Ed Discussion and look at the browser address. '
        'The course ID is the number immediately after `/courses/`.'
    )
    st.code('https://edstem.org/au/courses/36385/discussion/3516589', language=None)
    st.write(
        'In this example, **36385** is the course ID. The number after '
        '`/discussion/` is a thread ID; do not enter that number.'
    )

    st.markdown('**2. Create an API token**')
    st.write(
        'In Ed, open **Settings → API Tokens**, then select **Create Token**. '
        'Copy the token and paste it into the **Ed API token** field on the left. '
        'Treat the token like a password and do not share or commit it to GitHub.'
    )

    st.markdown('**3. Fetch your threads**')
    st.write(
        'Enter the course ID and API token in the sidebar, then click '
        '**Fetch course**. You do not need to edit the code or create a '
        'configuration file to use this page.'
    )


def main():
    st.set_page_config(page_title='Ed Discussion Dashboard', layout='wide')

    sources = ['Getting started', 'Upload CSV', 'Fetch from Ed']
    if CSV_PATH.exists():
        sources.append('Local threads.csv')
    source = st.sidebar.radio('Data source', sources, key='data_source')
    if source == 'Getting started':
        show_guide()
        return

    st.title('Ed Discussion Dashboard')
    if source == 'Local threads.csv':
        threads = pd.read_csv(CSV_PATH)
        st.caption(f'Data source: {CSV_PATH.name}')
    elif source == 'Upload CSV':
        uploaded = st.sidebar.file_uploader('Choose a threads CSV', type='csv')
        if uploaded is None:
            st.info('Upload a CSV created by data_collection.py or with the columns shown in examples/sample_threads.csv.')
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
            show_ed_setup_guide()
            st.stop()
        threads = st.session_state['course_threads'].copy()
        st.caption('Data source: Ed API (this browser session)')
        with st.expander('How to find your course ID and API token'):
            show_ed_setup_guide()
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

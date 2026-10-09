# Ed Discussion Dashboard

Explore Ed Discussion course threads by views, likes, replies, and answered status. The dashboard opens with a **Getting started** guide, so you can see how to load and explore your own data before entering any credentials.

## Quick start

### Codex desktop: open the dashboard from chat

In a local Codex chat for this repository, ask to open the Ed Discussion dashboard.
The `ed-helper` skill starts the local Streamlit server and returns its clickable
`localhost` URL. Use the dashboard to upload a CSV or fetch a course, then ask
questions about the data in the same Codex chat. The dashboard saves the active
dataset under `.local/ed-discussion/`, which Git ignores. Existing `threads.csv`
is also available as a local source.

For an Ed fetch, enter the numeric course ID and your own API token in the
dashboard sidebar's **Ed API token** password field, then click **Fetch course**.
Do not paste the token into chat. The token is used for the Ed request and is not
written to the saved CSV or metadata.

### Windows: double-click to start

1. If Python is not installed, install Python 3.10 or newer from the [official Python website](https://www.python.org/downloads/windows/). After installation, reopen your terminal or File Explorer window.
2. Download and **extract** the repository ZIP, open the extracted folder, and double-click `start.bat`.
3. On the first run, the script creates a `.venv` folder and installs the packages in `requirements.txt`. This requires internet access and may take a few minutes. The dashboard then opens in your browser. Double-click the same file for later runs.

If `start.bat` cannot find Python, it displays the installation URL. It does not change your system Python environment. Close the command window or press `Ctrl+C` to stop the dashboard.

### macOS / Linux, or manual setup

Install Python 3.10 or newer, then run these commands from the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the address shown in the terminal, usually `http://localhost:8501`.

## Use your own data

The **Data source** menu in the sidebar offers these options:

| Option | What it does |
| --- | --- |
| Getting started | Explains how to load data, use the filters, and resolve common errors |
| Upload CSV | Loads a discussion CSV exported by this dashboard or the collection script |
| Fetch from Ed | Fetches a course you can access using its numeric course ID and your Ed API token; lets you download the resulting CSV |
| Local threads.csv | Appears when `threads.csv` exists in the project directory; useful after running the collection script |

The course ID is the number after `/courses/` in a course URL. An API token is needed only to fetch data from Ed. Use your own credentials, and do not commit tokens or real course data to a public repository. The `.gitignore` file excludes local `threads*.csv` files, `.env`, and Streamlit secrets. Uploaded CSV files must have the same column headers as the sample file.

## Command-line scripts (optional)

The dashboard can fetch threads and download a CSV directly. Use the scripts below if you want to save files in batches or generate PNG charts. Install the dependencies first, as described above.

Windows PowerShell:

```powershell
$env:ED_API_TOKEN = 'your-token'
.\.venv\Scripts\python.exe data_collection.py --course-id 12345
.\.venv\Scripts\python.exe data_visualization.py
```

macOS / Linux:

```bash
export ED_API_TOKEN='your-token'
python data_collection.py --course-id 12345
python data_visualization.py
```

By default, `data_collection.py` creates `threads.csv` plus CSV files for the last 7, 14, and 30 days. Use `--output path/to/file.csv` to change the output location. `data_visualization.py` reads `threads.csv` and creates top-15 charts for views, replies, and likes. Use `--input path/to/file.csv` to analyze an existing CSV or `--output-dir` to choose an image directory. Both scripts support `--help`.

## Troubleshooting

- **Python is not found:** Install Python and open a new terminal or File Explorer window.
- **Package installation fails:** Check your internet connection and run `start.bat` again. If your school or workplace blocks PyPI, use a network that allows access.
- **Ed returns HTTP 401 or 403:** Check your token, course ID, and account access to the course.
- **The dashboard shows the guide:** Select **Upload CSV** or **Fetch from Ed** in the sidebar, or generate `threads.csv` in the project directory with the command-line script.
- **The time filter shows no threads:** There may be no posts in that period. Select **All** to view everything.

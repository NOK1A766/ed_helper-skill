# Ed Helper — Ed Discussion Dashboard and Codex Skill

Ed Helper helps you explore your course's Ed Discussion activity through a local Streamlit dashboard and a Codex skill. Load course threads, find the most viewed or discussed posts, filter by answer status, and ask questions about the same dataset in Codex chat.

Use the webpage to browse charts and tables, then use Codex to investigate patterns, summarize discussions, or create a report from the data you loaded.

## What you can do

- Fetch threads from an Ed course you can access, or upload an existing discussion CSV.
- Rank threads by views, likes, replies, or stars.
- Filter by time range, subcategory, and answered status.
- Follow links back to the original Ed discussions.
- Download fetched data as a CSV.
- Ask Codex questions about the loaded dataset and request charts or CSV reports.

The dashboard and Codex share a saved dataset in the project folder. Streamlit provides the browsing interface; the conversation happens in Codex's chatbox.

## 1. Set up the environment

### Requirements

- Python 3.10 or newer.
- Git, if you want to clone the repository. Downloading and extracting the ZIP also works.
- Internet access to install dependencies and fetch data from Ed.
- An Ed account with access to the course, if fetching directly from Ed.
- Codex with access to the local project folder, if using the chat workflow.

The Python dependencies are `streamlit`, `pandas`, `matplotlib`, and `requests`, listed in `requirements.txt`.

### Get the project

```bash
git clone https://github.com/NOK1A766/ed_helper-skill.git
cd ed_helper-skill
```

Alternatively, select **Code → Download ZIP** on [GitHub](https://github.com/NOK1A766/ed_helper-skill), extract it, and open the extracted folder.

### Windows: easiest setup

Install [Python 3.10 or newer](https://www.python.org/downloads/windows/), then double-click `start.bat` in the project folder.

On the first run, the launcher creates a `.venv` environment, installs missing dependencies, and opens the Streamlit dashboard. Use the same file on later runs. Keep its command window open while using the dashboard; press `Ctrl+C` there to stop it.

### Windows: manual setup

Run these commands in PowerShell from the project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `py` is unavailable but Python is installed, use `python -m venv .venv` for the first command. These commands use the environment directly, so activation is unnecessary.

### macOS / Linux

Run these commands from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`. Keep the terminal running while using the dashboard and press `Ctrl+C` to stop it.

## 2. Find your API key and course code

Fetching data requires an **Ed API token** and the course's **numeric Ed course ID**. CSV upload requires neither. The dashboard does not require an OpenAI API key; Codex uses its own sign-in and configuration.

### Course code / course ID

Open your course in Ed Discussion and inspect the browser address. For example:

```text
https://edstem.org/au/courses/12345/discussion/67890
```

Enter `12345` in the dashboard's **Course ID** field: it is the number immediately after `/courses/`. A university subject code such as `COMP1234` will not work. The number after `/discussion/` identifies a thread.

### Ed API token

The project's built-in setup guide describes this process:

1. Sign in to Ed with the account that can access your course.
2. Open **Settings → API Tokens**.
3. Select **Create Token** and copy the token.
4. Paste it into the dashboard's **Ed API token** password field.

If your Ed account does not show that option, check with your institution's Ed administrator about API access, or use a compatible CSV you already have.

Enter the token in the webpage, not in Codex chat. The dashboard uses it for the Ed request and does not write it to the saved CSV or metadata. You do not need to edit Python files or create a `.env` file for this workflow.

## 3. Use the Streamlit webpage

### Load your discussions

Choose an option under **Data source** in the sidebar:

| Option | How to use it |
| --- | --- |
| **Getting started** | Read the dashboard's setup and usage guide. |
| **Fetch from Ed** | Enter your course ID and Ed API token, then click **Fetch course**. |
| **Upload CSV** | Choose a CSV previously exported by this dashboard or `data_collection.py`. |
| **Local threads.csv** | Load `threads.csv` from the project folder. This option appears only when that file exists. |

After a successful Ed fetch, use **Download fetched CSV** to save a copy for later.

### Explore the results

Use the sidebar controls to change the view:

| Control | Available choices |
| --- | --- |
| **Time range** | All, Last 7 days, Last 14 days, Last 30 days |
| **Rank by** | Views, Likes, Replies, Stars |
| **Top threads** | 10 or 15 |
| **Subcategory** | All or a subcategory found in your dataset |
| **Answer status** | All, Answered, Unanswered |

The page shows the number of matching threads, a ranking chart, and a table with discussion details and links. **Top threads** limits the chart; the table includes all matching threads, sorted by the selected metric. Green bars indicate answered threads and orange bars indicate unanswered threads.

For example, choose **Last 14 days**, **Views**, and **Unanswered** to see which recent unresolved threads have attracted the most views.

**How to interpret the filters:** time ranges use each thread's creation time and a rolling cutoff from the current time. “Unanswered” means the resolved flag is not true. A thread can have replies and still appear unanswered, and announcements can appear in this group too.

The data is a snapshot. Fetch the course again or load an updated CSV when you want newer results.

## 4. Use the Codex chatbox

### Open the local project

Open the cloned repository as a local project in Codex and start a chat in that folder. Use the same checkout as the dashboard so Codex can read its saved data.

The bundled skill is located at:

```text
.codex/skills/ed-helper/SKILL.md
```

Start with this prompt, which also works when the skill is not listed in the skill picker:

```text
Read .codex/skills/ed-helper/SKILL.md and use it to open the Ed Discussion
dashboard. If needed, create a local .venv and install requirements.txt.
```

Codex follows the skill's launcher instructions, starts or reuses the dashboard, and returns a clickable localhost URL. Open that link, then upload a CSV or fetch a course in the webpage.

### Make the skill discoverable, if needed

The repository currently ships its skill under `.codex/skills`. Current [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills) lists `.agents/skills` for repository discovery. If `ed-helper` is missing from your available skills, copy the complete `ed-helper` folder to `.agents/skills/ed-helper` inside this repository, keeping the original folder. Restart Codex if it does not appear.

Keep the full repository available: the skill depends on the dashboard and Python modules here. Once discovered, you can ask “Use the ed-helper skill to open the dashboard.” Codex CLI and IDE users can also mention it as `$ed-helper`.

### Ask questions about the loaded data

After loading data in the webpage, try these prompts in Codex:

```text
What dataset is currently loaded? Tell me its source, load time, and thread count.
```

```text
Show the 15 most-viewed unanswered threads from the last 14 days,
with links back to Ed.
```

```text
Using my current dashboard filters, rank the top 10 threads by likes.
```

```text
Compare discussion activity across subcategories in the loaded dataset.
```

```text
Find unresolved question threads, excluding announcements where thread type
is available. Include their view counts, reply counts, and Ed links.
```

```text
Create a chart of the top 15 threads by replies and give me a link to the file.
```

Codex should inspect the saved data before answering, explain the filters it used, and include Ed links where available. Question-only analysis depends on whether the CSV includes `Thread type`.

### Match the dashboard's filters

When you say “use my current dashboard filters,” Codex can read the last saved time range, answer status, and subcategory. The ranking metric and Top count are not saved, so include them in your prompt when you want to match a chart exactly.

If you use several dashboard tabs, the most recently saved dataset and filters are shared. Reload the intended data and set its filters before asking Codex to analyze that view.

## How the webpage and chat share data

The dashboard saves the most recently loaded dataset under `.local/ed-discussion/`:

| File | Purpose |
| --- | --- |
| `current.csv` | Current discussion dataset |
| `metadata.json` | Data source, load time, row count, and course ID when available |
| `view.json` | Last saved time, answer-status, and subcategory filters |

Loading another dataset replaces the shared current dataset. If saved data or readable metadata is unavailable, the skill can fall back to a root-level `threads.csv` and should identify that fallback in its answer.

These local files are ignored by Git. Course data can contain private discussion content; keep it and generated reports out of public commits. Asking Codex to analyze the dataset involves giving Codex access to that content.

## Optional command-line analysis

With the virtual environment active, you can inspect or rank the saved dataset directly:

```bash
python -X utf8 -m ed_discussion.cli inspect
python -X utf8 -m ed_discussion.cli rank --metric views --days 14 --status unanswered --top 15
python -X utf8 -m ed_discussion.cli rank --current-view --metric likes --top 10
```

On Windows, replace `python` with `.\.venv\Scripts\python.exe` if the environment is not activated. `--current-view` uses the saved time, status, and subcategory filters in place of corresponding command-line filters.

The repository also includes `data_collection.py` for CSV collection and `data_visualization.py` for PNG charts. Run either with `--help` for its options. The collection script reads `ED_API_TOKEN` from the process environment and requires `--course-id`; it does not automatically load a `.env` file. The dashboard is the simplest way to enter your token and fetch data.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Python is not found | Install Python 3.10 or newer, then reopen your terminal or launcher. |
| `No module named streamlit` | Install `requirements.txt` using the same Python environment used to launch the app. |
| Dependency installation fails | Check network access to Python package downloads, then retry installation. |
| Ed returns HTTP 401 or 403 | Check the token, numeric course ID, and your account's access to that course. |
| CSV columns are missing | Use an export from this project, or compare your headers with **Required CSV columns** on the Getting started page. |
| No threads match the filters | Set **Time range**, **Subcategory**, and **Answer status** to **All**, then narrow the view again. |
| Codex cannot find a dataset | Load data in the dashboard and confirm Codex is using the same project folder. |
| Codex cannot match the current view | Load the intended dataset and set the dashboard filters again before retrying. |
| The dashboard link does not open | Use the actual URL printed by Streamlit or returned by Codex; the port may differ from 8501. |

Generated Ed links currently use the `/au/` course URL format. If your institution uses another Ed region, check the links before relying on them.

# Local data contract

## Saved data and view

The Streamlit dashboard writes the most recently loaded dataset to
`.local/ed-discussion/current.csv`. Uploads, successful Ed API fetches, and the
local CSV option use the same format. `.local/ed-discussion/metadata.json`
records `source` (`upload`, `ed`, or `local`), optional `filename` and
`course_id`, `row_count`, UTC `loaded_at`, and the CSV `sha256`. Loading the
same data from the same source preserves the saved load time.

`.local/ed-discussion/view.json` records the last saved `days`, `subcategory`,
and `status` filters with `dataset_sha256`. It does not record the ranking
metric, Top count, browser tab, or whether that page is still open.
`rank --current-view` compares the saved view hash with the metadata hash
and rejects a missing or mismatched view; it does not recompute the CSV hash.
If data integrity is in doubt, compare the actual CSV SHA256 with metadata.

If the saved CSV or readable metadata is unavailable, `load_current` can
fall back to the root `threads.csv`. Its synthesized metadata uses the file's
modification time as `loaded_at` and has no dataset hash or course ID.
Load it through the dashboard to establish a matching saved view. A present
dataset with missing required columns or no rows raises an error.

## Columns and query semantics

The required CSV columns are `Thread number`, `Thread title`, `Thread time`,
`Thread category`, `Thread subcategory`, `View count`, `Like count`,
`Star count`, `Reply number`, `Is answer resolved`, `Thread url`, and
`Thread content`. Ed fetches also provide `Thread id` and `Thread type`, but
these are not required CSV columns and are not returned by `rank`.

- `--days` is a positive integer. The cutoff is the execution time in UTC
  minus that many days, inclusive. This is a rolling interval, not calendar
  days or an interval relative to the newest post. Invalid dates are excluded
  when filtering by time and retained with no time filter. The implementation
  has no upper bound, so future timestamps are included; flag them if present.
- `--status` accepts `all`, `answered`, or `unanswered`. A resolved value is
  true only if its string form, stripped and lowercased, equals `true`.
  Missing and other values count as unanswered. This filter does not check
  thread type, reply count, or whether a question still needs help.
- `--subcategory` matches exactly. Missing subcategories become
  `Uncategorized`; an omitted value or `All` leaves them unrestricted.
- `--metric` accepts `views`, `likes`, `replies`, or `stars`, mapping to
  `View count`, `Like count`, `Reply number`, or `Star count`. The selected
  metric is converted to numbers, with invalid or missing values replaced
  by zero, then sorted descending. Ties have no defined secondary order.
- `--top` is a positive integer (default 15); `--metric` defaults to `views`.
  `matching_threads` counts every filtered row before the Top limit.

Use each row's `Thread url` for links. Ed-generated URLs use
`https://edstem.org/au/courses/{course_id}/discussion/{thread_id}`;
`Thread number` is the displayed course-local number, not the thread ID.
An internally consistent URL does not establish that its content is accessible
without the user's Ed login.

All files under `.local/` are ignored by Git. The Ed API token is used only
for the request and is never stored in the CSV or metadata.

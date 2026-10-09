# Local data contract

The Streamlit dashboard writes the most recently loaded dataset to
`.local/ed-discussion/current.csv`. Uploads and successful Ed API fetches use the
same format. `.local/ed-discussion/metadata.json` records `source`, optional
`filename` and `course_id`, `row_count`, UTC `loaded_at`, and the CSV `sha256`.
`.local/ed-discussion/view.json` records the browser's selected `days`,
`subcategory`, and `status` filters with the matching dataset hash.

The required CSV columns are `Thread number`, `Thread title`, `Thread time`,
`Thread category`, `Thread subcategory`, `View count`, `Like count`,
`Star count`, `Reply number`, `Is answer resolved`, `Thread url`, and
`Thread content`. Counts should be numeric and `Thread time` should be a
parseable date. Invalid dates are excluded from time-window queries.

All files under `.local/` are ignored by Git. The Ed API token is used only
for the request and is never stored in the CSV or metadata.

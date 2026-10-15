# Learning Log — 13 October 2026

- Created a Python canteen tracker.
- Learned input, calculations and conditions.
- Added error handling with try and except.
- Tested sales: Rs. 30 and leftover: 4.
- Next step: GitHub code backup.

## Session 2 — Multiple Food Items
- Added multiple food entries using a while loop.
- Stored records in a list of dictionaries.
- Used q to finish entering items.
- Displayed each item's sales and leftover quantity.
- Tested two items: total sales Rs. 290.
- Records are still temporary.

## Session 3 — JSON Storage
- Saved food records in records.json.
- Loaded existing records when restarting the program.
- Confirmed both records remained after restart.
- Verified total saved sales: Rs. 270.

## Session 4 — Date and Record Details
- Added automatic date to new records.
- Saved price and prepared quantity.
- Kept older records readable.
- Tested Poha sales: Rs. 200.
- Verified total saved sales: Rs. 470.

## Session 5 — Daily Report
- Added reports filtered by date.
- Calculated daily sales and leftover quantity.
- Excluded undated records from daily reports.
- Tested 2026-10-13: Rs. 200 sales and 2 leftover.

## Session 6 — CSV Export
- Exported saved records to CSV.
- Opened the CSV in Excel and checked all three records.

## Session 7 — Functions
- Created save_records() and load_records() functions.
- Confirmed saved records load correctly.
- Verified four records with total sales Rs. 500.

## Session 8 — Report Functions
- Created show_summary() and show_daily_report().
- Verified overall sales: Rs. 500.
- Verified daily sales: Rs. 230 and leftover: 4.

## Session 9 — CSV Export Function
- Created export_csv() to organise CSV export.
- Successfully exported all four saved records.

## Session 10 — Streamlit Web App
- Created a browser interface in web_app.py.
- Connected the form to JSON storage.
- Displayed saved records and total sales.
- Added a Delete button beside each record.
- Added confirmation and cancellation for deletion.

## Session 11 — Web Daily Report
- Added a date selector and daily report.
- Displayed daily sales, sold and leftover totals.
- Removed a duplicate record.
- Verified Rs. 380 sales, 16 sold and 9 leftover.

## Session 12 — Web CSV Download
- Added a Download CSV button to the browser app.
- Exported all saved records.
- Downloaded and checked the CSV file.

## Session 13 — Edit Records
- Added an Edit button beside each record.
- Added Save changes and Cancel options.
- Recalculate sales and leftover after editing.
- Preserve the original record date.

## Session 14 — JSON Backup and Restore
- Added JSON backup download.
- Validated uploaded backup records.
- Restored a backup successfully with confirmation.

## Session 15 — Food Demand Estimation
- Added estimates using up to 7 recent recorded days.
- Combined same-day sales for each food.
- Added an adjustable preparation buffer.
- Verified 10% buffer: Idli 6, Poha 9, Tea 4.
- Verified 0% buffer: Idli 5, Poha 8, Tea 3.
- Current estimates use only one recorded day.

## Session 16 — Food Performance Chart
- Added a food-wise Sold vs Leftover bar chart.
- Combined records for each food across all saved dates.
- Verified chart values against the summary table.

## Session 17 — Food Search
- Added case-insensitive food-name search.
- Displayed matching and total record counts.
- Verified Tea search.
- Kept overall totals independent of search.

## Session 18 — Daily Sales Trend
- Added a date-wise sales line chart and table.
- Excluded undated records.
- Displayed Rs. 380 for October 13 and Rs. 50 for October 14.

## Session 19 — Leftover Analysis
- Calculated food-wise leftover percentages.
- Verified Idli: 50%.
- Verified overall: 21 leftover out of 63 prepared, or 33.3%.

## Session 20 — Record Date Selection
- Added a date selector to the food-entry form.
- Allowed past dates and blocked future dates.
- New records use the selected date.
- Existing record dates remain unchanged.

## Session 21 — Daily CSV Download
- Added CSV download for the selected report date.
- Checked that the export contains only that day's records.

## Session 22 — Tab Navigation
- Organised the app into Records, Reports, Demand and Backup tabs.
- Kept existing features within their relevant tabs.

## Session 23 — Summary Dashboard
- Added four summary cards above the tabs.
- Verified Rs. 700 sales, 42 sold, 21 leftover and 6 records.

## Session 24 — Manual Testing
- Confirmed records remain after browser refresh.
- Tested food search and no-match results.
- Tested Edit Cancel and Delete Cancel.
- Checked the selected-date sales report.
- Checked daily CSV and JSON backup downloads.
- All listed manual checks passed.

## Session 26 — Project Screenshots
- Added dashboard, reports and demand screenshots.
- Embedded screenshots in the GitHub README.

## Session 27 — Fresh Setup Test
- Downloaded the project ZIP from GitHub.
- Created a new virtual environment.
- Installed packages from requirements.txt.
- Successfully launched the app from the downloaded copy.
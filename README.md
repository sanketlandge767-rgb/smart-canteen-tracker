# Smart Canteen Tracker

A beginner Python project to calculate canteen sales and leftover food.

## Current Features
- Enter food name and price
- Enter prepared and sold quantities
- Calculate total sales and leftover food
- Validate negative values and incorrect quantities
- Handle invalid numeric input
- Add multiple food items in one session
- Display item-wise summary and grand total sales
- Save records locally in a JSON file
- Load saved records when restarting
- Automatically date new entries
- Store price and prepared quantity for new records
- View sales and leftover totals for a selected date
- Export all saved records to CSV for Excel
- Browser interface built with Streamlit
- Save food entries from a form
- Delete individual records with confirmation
- Select a date to view daily sales, sold and leftover totals
- Download all saved records as CSV from the browser
- Edit food name, price and quantities with Save or Cancel
- Download and restore JSON backups with validation
- Estimate food preparation using recent sales and an adjustable buffer
- Compare food-wise sold and leftover totals using a bar chart
- Search saved records by food name
- View daily sales trends using a line chart
- View food-wise and overall leftover percentages
- Select today's or a past date when adding food records
- Download the selected day's records as CSV
- Navigate between Records, Reports, Demand and Backup tabs

## How to Run
Requires Python 3.

```bash
python app.py
```

## Example
Price: Rs. 10
Prepared: 7
Sold: 3
Leftover: 4
Total sales: Rs. 30.00

## Current Limitations
- - Runs locally; online deployment is pending
- Records are stored locally; no automatic cloud backup
- Total sales includes all saved records

## Planned Features
- Streamlit interface
- SQLite data storage
- Dashboard and CSV export
- Basic demand estimate using average sales

## Author
Sanket

## Run the Web App on Windows

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run web_app.py
```


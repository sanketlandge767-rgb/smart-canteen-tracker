import json
import csv
import io
from pathlib import Path
from datetime import date

import streamlit as st

st.set_page_config(
    page_title="Smart Canteen Tracker",
    page_icon="🍽️",
    layout="wide"
)

data_file = Path(__file__).parent / "records.json"


def load_records():
    if not data_file.exists():
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        st.error(f"Could not load records: {error}")
        st.stop()


def save_records(records):
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)


def create_csv(records):
    buffer = io.StringIO()
    fields = [
        "date", "food", "price", "prepared",
        "sold", "leftover", "sales"
    ]

    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()

    for record in records:
        writer.writerow({
            "date": record.get("date", ""),
            "food": record["food"],
            "price": record.get("price", ""),
            "prepared": record.get(
                "prepared", record["sold"] + record["leftover"]
            ),
            "sold": record["sold"],
            "leftover": record["leftover"],
            "sales": f"{record['sales']:.2f}"
        })

    return buffer.getvalue().encode("utf-8-sig")


def make_record(food, price, prepared, sold, record_date=None):
    record = {
        "food": food.strip(),
        "price": price,
        "prepared": prepared,
        "sold": sold,
        "leftover": prepared - sold,
        "sales": price * sold
    }

    if record_date is not None:
        record["date"] = record_date

    return record


def reset_actions():
    st.session_state.pending_delete = None
    st.session_state.edit_index = None


st.title("🍽️ Smart Canteen Tracker")
st.caption("Created by Sanket")

records = load_records()

if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "edit_version" not in st.session_state:
    st.session_state.edit_version = 0

if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

# Add a record
with st.form("food_entry"):
    food_name = st.text_input("Food name")

    price = st.number_input(
        "Price per item (Rs.)",
        min_value=0.0,
        value=10.0,
        step=1.0
    )

    prepared = st.number_input(
        "Prepared quantity",
        min_value=0,
        value=10,
        step=1
    )

    sold = st.number_input(
        "Sold quantity",
        min_value=0,
        value=0,
        step=1
    )

    submitted = st.form_submit_button("Save record")

if submitted:
    if not food_name.strip():
        st.error("Enter a food name.")
    elif sold > prepared:
        st.error("Sold quantity cannot exceed prepared quantity.")
    else:
        new_record = make_record(
            food_name, price, prepared, sold,
            date.today().isoformat()
        )

        try:
            save_records(records + [new_record])
        except OSError as error:
            st.error(f"Could not save record: {error}")
        else:
            reset_actions()
            st.session_state.message = "Record saved successfully!"
            st.rerun()

# All records
st.subheader("All saved records")

if records:
    widths = [2, 2, 1, 1, 1, 1, 1.5, 1, 1]

    headings = [
        "Date", "Food", "Price", "Prepared",
        "Sold", "Leftover", "Sales", "Edit", "Delete"
    ]

    for column, heading in zip(st.columns(widths), headings):
        column.write(f"**{heading}**")

    st.divider()

    for index, record in enumerate(records):
        columns = st.columns(widths)

        columns[0].write(record.get("date", "Old record"))
        columns[1].write(record["food"])

        record_price = record.get("price")

        columns[2].write(
            f"{record_price:.2f}"
            if record_price is not None else "—"
        )

        columns[3].write(
            record.get(
                "prepared", record["sold"] + record["leftover"]
            )
        )

        columns[4].write(record["sold"])
        columns[5].write(record["leftover"])
        columns[6].write(f"Rs. {record['sales']:.2f}")

        with columns[7]:
            if st.button("Edit", key=f"edit_{index}"):
                reset_actions()
                st.session_state.edit_index = index
                st.session_state.edit_version += 1
                st.rerun()

        with columns[8]:
            if st.button("Delete", key=f"delete_{index}"):
                reset_actions()
                st.session_state.pending_delete = index
                st.rerun()

        # Edit form for the selected row
        if st.session_state.edit_index == index:
            old_prepared = record.get(
                "prepared", record["sold"] + record["leftover"]
            )

            old_price = record.get("price")

            if old_price is None:
                old_price = (
                    record["sales"] / record["sold"]
                    if record["sold"] else 0.0
                )

            st.info(
                "Edit this record. Its original date will stay the same."
            )

            form_key = (
                f"edit_form_{index}_"
                f"{st.session_state.edit_version}"
            )

            with st.form(form_key):
                edited_food = st.text_input(
                    "Food name",
                    value=record["food"]
                )

                edited_price = st.number_input(
                    "Price per item (Rs.)",
                    min_value=0.0,
                    value=float(old_price),
                    step=1.0
                )

                edited_prepared = st.number_input(
                    "Prepared quantity",
                    min_value=0,
                    value=int(old_prepared),
                    step=1
                )

                edited_sold = st.number_input(
                    "Sold quantity",
                    min_value=0,
                    value=int(record["sold"]),
                    step=1
                )

                save_column, cancel_column = st.columns(2)

                with save_column:
                    save_edit = st.form_submit_button("Save changes")

                with cancel_column:
                    cancel_edit = st.form_submit_button("Cancel")

            if cancel_edit:
                reset_actions()
                st.rerun()

            if save_edit:
                if not edited_food.strip():
                    st.error("Enter a food name.")
                elif edited_sold > edited_prepared:
                    st.error(
                        "Sold quantity cannot exceed prepared quantity."
                    )
                else:
                    edited_record = make_record(
                        edited_food,
                        edited_price,
                        edited_prepared,
                        edited_sold,
                        record.get("date")
                    )

                    updated_records = records.copy()
                    updated_records[index] = edited_record

                    try:
                        save_records(updated_records)
                    except OSError as error:
                        st.error(f"Could not update record: {error}")
                    else:
                        reset_actions()
                        st.session_state.message = "Record updated!"
                        st.rerun()

        # Delete confirmation
        if st.session_state.pending_delete == index:
            st.warning(
                f"Delete {record['food']} | "
                f"Sales: Rs. {record['sales']:.2f}?"
            )

            confirm_column, cancel_column = st.columns(2)

            with confirm_column:
                confirm_delete = st.button(
                    "Confirm delete", key=f"confirm_{index}"
                )

            with cancel_column:
                cancel_delete = st.button(
                    "Cancel", key=f"cancel_delete_{index}"
                )

            if cancel_delete:
                reset_actions()
                st.rerun()

            if confirm_delete:
                remaining_records = (
                    records[:index] + records[index + 1:]
                )

                try:
                    save_records(remaining_records)
                except OSError as error:
                    st.error(f"Could not delete record: {error}")
                else:
                    reset_actions()
                    st.session_state.message = "Record deleted!"
                    st.rerun()

        st.divider()

    total_sales = sum(record["sales"] for record in records)
    st.metric("Total saved sales", f"Rs. {total_sales:.2f}")

else:
    st.info("No records yet. Add your first food item.")

st.caption("Records are saved locally on this laptop.")

# Daily report
st.divider()
st.subheader("📅 Daily Sales Report")

selected_date = st.date_input(
    "Select report date",
    value=date.today()
)

daily_records = [
    record for record in records
    if record.get("date") == selected_date.isoformat()
]

if daily_records:
    sales_column, sold_column, leftover_column = st.columns(3)

    sales_column.metric(
        "Daily sales",
        f"Rs. {sum(r['sales'] for r in daily_records):.2f}"
    )

    sold_column.metric(
        "Items sold",
        sum(r["sold"] for r in daily_records)
    )

    leftover_column.metric(
        "Leftover quantity",
        sum(r["leftover"] for r in daily_records)
    )

    st.dataframe([
        {
            "Food": record["food"],
            "Prepared": record.get(
                "prepared", record["sold"] + record["leftover"]
            ),
            "Sold": record["sold"],
            "Leftover": record["leftover"],
            "Sales": record["sales"]
        }
        for record in daily_records
    ])

else:
    st.info("No records found for the selected date.")

st.caption(
    "Old records without a date are excluded from daily reports."
)

# CSV download
st.divider()
st.subheader("📥 Export Records")

if records:
    st.download_button(
        label="Download all records as CSV",
        data=create_csv(records),
        file_name=f"canteen-records-{date.today().isoformat()}.csv",
        mime="text/csv",
        key="download_all_records"
    )

    st.caption("Downloads all records, regardless of report date.")

else:
    st.info("Add records before exporting.")

st.divider()
st.subheader("💾 Data Backup")

backup_data = json.dumps(
    records,
    indent=4,
    ensure_ascii=False,
    allow_nan=False
).encode("utf-8")

st.download_button(
    label="Download JSON backup",
    data=backup_data,
    file_name=f"canteen-backup-{date.today().isoformat()}.json",
    mime="application/json",
    key="download_json_backup"
)

st.caption("Keep this backup to restore your records later.")

st.subheader("Restore JSON Backup")

uploaded_backup = st.file_uploader(
    "Choose your canteen JSON backup",
    type=["json"],
    key="restore_backup_file"
)

if uploaded_backup is not None:
    try:
        backup_records = json.loads(
            uploaded_backup.getvalue().decode("utf-8-sig")
        )

        if not isinstance(backup_records, list):
            raise ValueError("Backup must contain a list of records.")

        for record in backup_records:
            if not isinstance(record, dict):
                raise ValueError("Each record must be an object.")

            if not isinstance(record.get("food"), str):
                raise ValueError("Each record needs a food name.")

            if not record["food"].strip():
                raise ValueError("Food name cannot be empty.")

            for field in ["sold", "leftover"]:
                value = record.get(field)

                if type(value) is not int or value < 0:
                    raise ValueError(
                        f"{field} must be a non-negative whole number."
                    )

            sales = record.get("sales")

            if (
                type(sales) not in (int, float)
                or not 0 <= sales < float("inf")
            ):
                raise ValueError("Sales must be a valid non-negative number.")

            if "prepared" in record:
                if (
                    type(record["prepared"]) is not int
                    or record["prepared"]
                    != record["sold"] + record["leftover"]
                ):
                    raise ValueError("Prepared quantity is inconsistent.")

            if "price" in record:
                price_value = record["price"]

                if (
                    type(price_value) not in (int, float)
                    or not 0 <= price_value < float("inf")
                ):
                    raise ValueError("Price must be a valid number.")

                if abs(
                    price_value * record["sold"] - sales
                ) > 0.01:
                    raise ValueError("Price and sales do not match.")

            if "date" in record:
                record_date = record["date"]

                if not isinstance(record_date, str):
                    raise ValueError("Date must be text.")

                if date.fromisoformat(record_date).isoformat() != record_date:
                    raise ValueError("Date must use YYYY-MM-DD.")

    except (ValueError, UnicodeError, OverflowError) as error:
        st.error(f"Invalid backup: {error}")

    else:
        st.info(
            f"Current records: {len(records)} | "
            f"Backup records: {len(backup_records)}"
        )

        st.warning(
            "Restore replaces all current records with this backup."
        )

        with st.form("restore_confirmation"):
            confirmed = st.checkbox(
                "I have downloaded my current backup "
                "and want to replace the records."
            )

            restore_clicked = st.form_submit_button("Restore backup")

        if restore_clicked:
            if not confirmed:
                st.warning("Tick the confirmation checkbox first.")
            else:
                try:
                    save_records(backup_records)
                except OSError as error:
                    st.error(f"Could not restore backup: {error}")
                else:
                    reset_actions()
                    st.session_state.message = (
                        "Backup restored successfully!"
                    )
                    st.rerun()

# Food demand estimation
import math

st.divider()
st.subheader("📊 Food Demand Estimation")

st.caption(
    "Uses up to 7 recent recorded days before today. "
    "Today's records are excluded because sales may still be ongoing."
)

food_history = {}

for record in records:
    record_date = record.get("date")

    if not record_date:
        continue

    try:
        sales_date = date.fromisoformat(record_date)
    except (TypeError, ValueError):
        continue

    if sales_date >= date.today():
        continue

    food_name = record["food"].strip()
    food_key = food_name.casefold()

    if food_key not in food_history:
        food_history[food_key] = {
            "name": food_name,
            "daily_sales": {}
        }

    daily_sales = food_history[food_key]["daily_sales"]

    daily_sales[sales_date] = (
        daily_sales.get(sales_date, 0) + record["sold"]
    )

if food_history:
    buffer_percent = st.slider(
        "Extra preparation buffer (%)",
        min_value=0,
        max_value=30,
        value=10,
        step=5
    )

    estimates = []

    for food_key in sorted(food_history):
        history = food_history[food_key]
        daily_sales = history["daily_sales"]

        recent_dates = sorted(daily_sales, reverse=True)[:7]

        average_sold = (
            sum(daily_sales[day] for day in recent_dates)
            / len(recent_dates)
        )

        suggested_quantity = math.ceil(
            average_sold * (1 + buffer_percent / 100)
        )

        estimates.append({
            "Food": history["name"],
            "Recorded days used": len(recent_dates),
            "Average daily sold": round(average_sold, 1),
            "Suggested preparation": suggested_quantity
        })

    st.dataframe(estimates, hide_index=True)

    st.info(
        "This is a simple sales-based estimate. "
        "Adjust it for holidays, events and expected attendance. "
        "Missing dates are not counted as zero-sales days."
    )

else:
    st.info(
        "Demand estimates will appear when you have "
        "dated sales records from before today."
    )
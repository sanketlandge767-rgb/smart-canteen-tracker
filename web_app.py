import json
import csv
import io
import math
from pathlib import Path
from datetime import date

import streamlit as st

st.set_page_config(
    page_title="Smart Canteen Tracker",
    page_icon="🍽️",
    layout="wide"
)

data_file = Path(__file__).parent / "records.json"


def validate_records(items):
    if not isinstance(items, list):
        raise ValueError("Records must be a list.")

    for record in items:
        if not isinstance(record, dict):
            raise ValueError("Each record must be an object.")

        food = record.get("food")
        if not isinstance(food, str) or not food.strip():
            raise ValueError("Each record needs a food name.")

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
                raise ValueError("Price must be a valid non-negative number.")

            if abs(price_value * record["sold"] - sales) > 0.01:
                raise ValueError("Price and sales do not match.")

        if "date" in record:
            record_date = record["date"]

            if not isinstance(record_date, str):
                raise ValueError("Date must be text.")

            if date.fromisoformat(record_date).isoformat() != record_date:
                raise ValueError("Date must use YYYY-MM-DD.")


def load_records():
    if not data_file.exists():
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            items = json.load(file)

        validate_records(items)
        return items

    except (ValueError, OSError, OverflowError) as error:
        st.error(f"Could not load records: {error}")
        st.stop()


def save_records(items):
    validate_records(items)

    with data_file.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=4, allow_nan=False)


def create_csv(items):
    buffer = io.StringIO()

    fields = [
        "date", "food", "price", "prepared",
        "sold", "leftover", "sales"
    ]

    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()

    for record in items:
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

for name, default in [
    ("pending_delete", None),
    ("edit_index", None),
    ("edit_version", 0)
]:
    if name not in st.session_state:
        st.session_state[name] = default

if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

# Overall dashboard
total_revenue = sum(record["sales"] for record in records)
total_sold = sum(record["sold"] for record in records)
total_leftover = sum(record["leftover"] for record in records)

sales_card, sold_card, leftover_card, records_card = st.columns(4)

sales_card.metric("Total sales", f"Rs. {total_revenue:.2f}")
sold_card.metric("Quantity sold", total_sold)
leftover_card.metric("Leftover quantity", total_leftover)
records_card.metric("Saved records", len(records))

st.caption(
    "Totals across all saved records, including undated records."
)
st.divider()

records_tab, reports_tab, demand_tab, backup_tab = st.tabs(
    ["Records", "Reports", "Demand", "Backup"]
)

# RECORDS TAB
with records_tab:
    st.subheader("Add Food Record")

    with st.form("food_entry"):
        entry_date = st.date_input(
            "Record date",
            value=date.today(),
            max_value=date.today(),
            key="entry_date"
        )

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
        elif entry_date > date.today():
            st.error("Record date cannot be in the future.")
        elif sold > prepared:
            st.error("Sold quantity cannot exceed prepared quantity.")
        else:
            new_record = make_record(
                food_name, price, prepared, sold,
                entry_date.isoformat()
            )

            try:
                save_records(records + [new_record])
            except (OSError, ValueError, OverflowError) as error:
                st.error(f"Could not save record: {error}")
            else:
                reset_actions()
                st.session_state.message = (
                    f"Record saved for {entry_date.isoformat()}!"
                )
                st.rerun()

    st.subheader("All saved records")

    search_text = st.text_input(
        "Search food name",
        placeholder="Type Tea, Poha, Idli...",
        key="food_search",
        on_change=reset_actions
    ).strip().casefold()

    visible_records = [
        (index, record)
        for index, record in enumerate(records)
        if search_text in record["food"].strip().casefold()
    ]

    st.caption(
        f"Showing {len(visible_records)} of {len(records)} records. "
        "Search filters this list only."
    )

    if not records:
        st.info("No records yet. Add your first food item.")
    elif not visible_records:
        st.info("No matching food. Clear the search to see all records.")

    if visible_records:
        widths = [2, 2, 1, 1, 1, 1, 1.5, 1, 1]

        headings = [
            "Date", "Food", "Price", "Prepared",
            "Sold", "Leftover", "Sales", "Edit", "Delete"
        ]

        for column, heading in zip(st.columns(widths), headings):
            column.write(f"**{heading}**")

        st.divider()

        for index, record in visible_records:
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
                    "Edit this record. Its original date stays the same."
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
                        except (OSError, ValueError, OverflowError) as error:
                            st.error(f"Could not update record: {error}")
                        else:
                            reset_actions()
                            st.session_state.message = "Record updated!"
                            st.rerun()

            if st.session_state.pending_delete == index:
                st.warning(
                    f"Delete {record['food']} | "
                    f"Sold: {record['sold']} | "
                    f"Sales: Rs. {record['sales']:.2f}?"
                )

                confirm_column, cancel_column = st.columns(2)

                with confirm_column:
                    confirm_delete = st.button(
                        "Confirm delete",
                        key=f"confirm_{index}"
                    )

                with cancel_column:
                    cancel_delete = st.button(
                        "Cancel",
                        key=f"cancel_delete_{index}"
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
                    except (OSError, ValueError, OverflowError) as error:
                        st.error(f"Could not delete record: {error}")
                    else:
                        reset_actions()
                        st.session_state.message = "Record deleted!"
                        st.rerun()

            st.divider()

    total_sales = sum(record["sales"] for record in records)
    st.metric("Total saved sales — all records", f"Rs. {total_sales:.2f}")
    st.caption("Records are saved locally on this laptop.")


# REPORTS TAB
with reports_tab:
    st.subheader("📅 Daily Sales Report")

    selected_date = st.date_input(
        "Select report date",
        value=date.today(),
        key="report_date"
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

        st.download_button(
            label="Download selected day's CSV",
            data=create_csv(daily_records),
            file_name=f"canteen-daily-{selected_date.isoformat()}.csv",
            mime="text/csv",
            key="download_daily_report"
        )
    else:
        st.info("No records found for the selected date.")

    st.caption(
        "Old records without a date are excluded from daily reports."
    )

    st.divider()
    st.subheader("📥 Export All Records")

    if records:
        st.download_button(
            label="Download all records as CSV",
            data=create_csv(records),
            file_name=f"canteen-records-{date.today().isoformat()}.csv",
            mime="text/csv",
            key="download_all_records"
        )
    else:
        st.info("Add records before exporting.")

    st.caption(
        "The charts below use all saved records, "
        "regardless of the selected report date."
    )

    st.divider()
    st.subheader("📊 Food Performance")

    food_totals = {}

    for record in records:
        food_name = record["food"].strip()
        food_key = food_name.casefold()

        if food_key not in food_totals:
            food_totals[food_key] = {
                "Food": food_name,
                "Sold": 0,
                "Leftover": 0
            }

        food_totals[food_key]["Sold"] += record["sold"]
        food_totals[food_key]["Leftover"] += record["leftover"]

    if food_totals:
        chart_rows = list(food_totals.values())

        st.bar_chart(
            chart_rows,
            x="Food",
            y=["Sold", "Leftover"],
            stack=False
        )
        st.dataframe(chart_rows)
    else:
        st.info("Add records to see food performance.")

    st.divider()
    st.subheader("📈 Daily Sales Trend")

    sales_by_date = {}

    for record in records:
        record_date = record.get("date")

        if not record_date:
            continue

        sales_by_date[record_date] = (
            sales_by_date.get(record_date, 0) + record["sales"]
        )

    if sales_by_date:
        trend_rows = [
            {
                "Date": date.fromisoformat(record_date),
                "Sales": total
            }
            for record_date, total in sorted(sales_by_date.items())
        ]

        st.line_chart(
            trend_rows,
            x="Date",
            y="Sales"
        )

        st.dataframe(trend_rows)

        if len(trend_rows) == 1:
            st.info(
                "Only one dated day is available. "
                "Add records on more days to see a trend."
            )
    else:
        st.info("No dated records available.")

    st.caption(
        "Undated records are excluded. "
        "Missing dates are not treated as zero-sales days."
    )

    st.divider()
    st.subheader("🍽️ Leftover Analysis")

    leftover_totals = {}

    for record in records:
        food_name = record["food"].strip()
        food_key = food_name.casefold()

        if food_key not in leftover_totals:
            leftover_totals[food_key] = {
                "Food": food_name,
                "Prepared": 0,
                "Leftover": 0
            }

        leftover_totals[food_key]["Prepared"] += record.get(
            "prepared", record["sold"] + record["leftover"]
        )

        leftover_totals[food_key]["Leftover"] += record["leftover"]

    if leftover_totals:
        leftover_rows = []

        for totals in leftover_totals.values():
            prepared_total = totals["Prepared"]
            leftover_total = totals["Leftover"]

            percentage = (
                leftover_total / prepared_total * 100
                if prepared_total > 0
                else None
            )

            leftover_rows.append({
                "Food": totals["Food"],
                "Prepared": prepared_total,
                "Leftover": leftover_total,
                "Leftover (%)": (
                    round(percentage, 2)
                    if percentage is not None else None
                )
            })

        st.dataframe(leftover_rows)

        total_prepared = sum(
            item["Prepared"] for item in leftover_totals.values()
        )

        total_leftover = sum(
            item["Leftover"] for item in leftover_totals.values()
        )

        if total_prepared > 0:
            overall_percentage = (
                total_leftover / total_prepared * 100
            )

            st.metric(
                "Overall leftover percentage",
                f"{overall_percentage:.1f}%"
            )
        else:
            st.info(
                "Percentage needs a prepared quantity greater than zero."
            )
    else:
        st.info("Add records to see leftover analysis.")

    st.caption(
        "Leftover means unsold food, not necessarily discarded food."
    )


# DEMAND TAB
with demand_tab:
    st.subheader("📊 Food Demand Estimation")

    st.caption(
        "Uses up to 7 recent recorded days before today. "
        "Today's sales are excluded."
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
                "Average sold per recorded day": round(average_sold, 2),
                "Suggested preparation": suggested_quantity
            })

        st.dataframe(estimates)

        st.info(
            "This is an average-based estimate, not AI prediction. "
            "Missing dates are not counted as zero-sales days. "
            "Sales may underestimate demand when food sells out."
        )

        st.caption(
            "One recorded day gives a weak estimate. "
            "Collect more daily records before relying on suggestions."
        )
    else:
        st.info("No dated records from before today are available.")


# BACKUP TAB
with backup_tab:
    st.subheader("💾 Download Data Backup")

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

    st.divider()
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

            validate_records(backup_records)

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

                restore_clicked = st.form_submit_button(
                    "Restore backup"
                )

            if restore_clicked:
                if not confirmed:
                    st.warning("Tick the confirmation checkbox first.")
                else:
                    try:
                        save_records(backup_records)
                    except (OSError, ValueError, OverflowError) as error:
                        st.error(f"Could not restore backup: {error}")
                    else:
                        reset_actions()
                        st.session_state.message = (
                            "Backup restored successfully!"
                        )
                        st.rerun()
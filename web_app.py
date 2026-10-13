import json
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


st.title("🍽️ Smart Canteen Tracker")
st.caption("Created by Sanket")

records = load_records()

if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

with st.form("food_entry", clear_on_submit=False):
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
    st.session_state.pending_delete = None

    if not food_name.strip():
        st.error("Enter a food name.")
    elif sold > prepared:
        st.error("Sold quantity cannot exceed prepared quantity.")
    else:
        record = {
            "date": date.today().isoformat(),
            "food": food_name.strip(),
            "price": price,
            "prepared": prepared,
            "sold": sold,
            "leftover": prepared - sold,
            "sales": price * sold
        }

        updated_records = records + [record]

        try:
            save_records(updated_records)
        except OSError as error:
            st.error(f"Could not save record: {error}")
        else:
            records = updated_records
            st.success("Record saved successfully!")

st.subheader("All saved records")

if records:
    widths = [2, 2, 1, 1, 1, 1, 1.5, 1.5]

    headings = [
        "Date", "Food", "Price", "Prepared",
        "Sold", "Leftover", "Sales", "Action"
    ]

    header_columns = st.columns(widths)

    for column, heading in zip(header_columns, headings):
        column.write(f"**{heading}**")

    st.divider()

    for index, record in enumerate(records):
        columns = st.columns(widths)

        columns[0].write(record.get("date", "Old record"))
        columns[1].write(record["food"])

        record_price = record.get("price")
        columns[2].write(
            f"{record_price:.2f}"
            if record_price is not None
            else "—"
        )

        columns[3].write(
            record.get(
                "prepared",
                record["sold"] + record["leftover"]
            )
        )
        columns[4].write(record["sold"])
        columns[5].write(record["leftover"])
        columns[6].write(f"Rs. {record['sales']:.2f}")

        with columns[7]:
            if st.button("🗑 Delete", key=f"delete_{index}"):
                st.session_state.pending_delete = index
                st.rerun()

        if st.session_state.pending_delete == index:
            st.warning(
                f"Delete {record['food']} | "
                f"Sold: {record['sold']} | "
                f"Sales: Rs. {record['sales']:.2f}?"
            )

            confirm_column, cancel_column = st.columns(2)

            with confirm_column:
                if st.button(
                    "Confirm delete",
                    key=f"confirm_{index}"
                ):
                    remaining_records = (
                        records[:index] + records[index + 1:]
                    )

                    try:
                        save_records(remaining_records)
                    except OSError as error:
                        st.error(f"Could not delete record: {error}")
                    else:
                        st.session_state.pending_delete = None
                        st.rerun()

            with cancel_column:
                if st.button(
                    "Cancel",
                    key=f"cancel_{index}"
                ):
                    st.session_state.pending_delete = None
                    st.rerun()

        st.divider()

    total_sales = sum(record["sales"] for record in records)
    st.metric("Total saved sales", f"Rs. {total_sales:.2f}")

else:
    st.info("No records yet. Add your first food item.")

st.caption("Records are saved locally on this laptop.")
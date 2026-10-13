import json
from pathlib import Path
from datetime import date

data_file = Path(__file__).parent / "records.json"
print("Smart Canteen Tracker")
print("Created by: Sanket")

if data_file.exists():
    try:
        with data_file.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError:
        print("Error: records.json contains invalid JSON.")
        raise SystemExit
else:
    records = []

while True:
    food_name = input("\nEnter food name (or q to finish): ").strip()

    if food_name.lower() == "q":
        break

    if not food_name:
        print("Error: Food name cannot be empty.")
        continue

    try:
        price = float(input("Enter price per item: Rs. "))
        prepared = int(input("Enter prepared quantity: "))
        sold = int(input("Enter sold quantity: "))

        if price < 0 or prepared < 0 or sold < 0:
            print("Error: Values cannot be negative.")
            continue

        if sold > prepared:
            print("Error: Sold quantity cannot exceed prepared quantity.")
            continue

        record = {

            "date": date.today().isoformat(),
            "food": food_name,
            "price": price,
            "prepared": prepared,
            "sold": sold,
            "leftover": prepared - sold,
            "sales": price * sold
        }

        records.append(record)

        with data_file.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)

        print("Item added successfully!")

    except ValueError:
        print("Error: Enter numbers for price and whole numbers for quantities.")

print("\n--- Final Canteen Summary ---")

grand_total = 0

for record in records:
    record_date = record.get("date", "Old record")
    prepared_quantity = record.get(
        "prepared", record["sold"] + record["leftover"]
    )

    print(
        f"{record_date} | "
        f"{record['food']} | "
        f"Prepared: {prepared_quantity} | "
        f"Sold: {record['sold']} | "
        f"Leftover: {record['leftover']} | "
        f"Sales: Rs. {record['sales']:.2f}"
    )

    grand_total += record["sales"]

print(f"\nTotal sales: Rs. {grand_total:.2f}")

report_date = input(
    "\nEnter report date (YYYY-MM-DD), or Enter to skip: "
).strip()

if report_date:
    try:
        date.fromisoformat(report_date)

        daily_sales = 0
        daily_leftover = 0
        matching_records = 0

        print(f"\n--- Report for {report_date} ---")

        for record in records:
            if record.get("date") == report_date:
                print(
                    f"{record['food']} | "
                    f"Sales: Rs. {record['sales']:.2f} | "
                    f"Leftover: {record['leftover']}"
                )

                daily_sales += record["sales"]
                daily_leftover += record["leftover"]
                matching_records += 1

        if matching_records == 0:
            print("No records found for this date.")
        else:
            print(f"Daily sales: Rs. {daily_sales:.2f}")
            print("Total leftover quantity:", daily_leftover)

    except ValueError:
        print("Invalid date. Use YYYY-MM-DD, for example 2026-10-13.")
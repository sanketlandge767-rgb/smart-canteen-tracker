print("Smart Canteen Tracker")
print("Created by: Sanket")

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
            "food": food_name,
            "sold": sold,
            "leftover": prepared - sold,
            "sales": price * sold
        }

        records.append(record)
        print("Item added successfully!")

    except ValueError:
        print("Error: Enter numbers for price and whole numbers for quantities.")

print("\n--- Final Canteen Summary ---")

grand_total = 0

for record in records:
    print(
        f"{record['food']} | "
        f"Sold: {record['sold']} | "
        f"Leftover: {record['leftover']} | "
        f"Sales: Rs. {record['sales']:.2f}"
    )
    grand_total += record["sales"]

print(f"\nTotal sales: Rs. {grand_total:.2f}")
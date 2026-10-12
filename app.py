print("Smart Canteen Tracker")
print("Created by: Sanket")

food_name = input("Enter food name: ").strip()

try:
    price = float(input("Enter price per item: Rs. "))
    prepared = int(input("Enter prepared quantity: "))
    sold = int(input("Enter sold quantity: "))

    if not food_name:
        print("Error: Food name cannot be empty.")
    elif price < 0 or prepared < 0 or sold < 0:
        print("Error: Values cannot be negative.")
    elif sold > prepared:
        print("Error: Sold quantity cannot exceed prepared quantity.")
    else:
        total_sales = price * sold
        leftover = prepared - sold

        print("\n--- Canteen Summary ---")
        print("Food:", food_name)
        print("Prepared:", prepared)
        print("Sold:", sold)
        print("Leftover:", leftover)
        print(f"Total sales: Rs. {total_sales:.2f}")

except ValueError:
    print("Error: Enter numbers for price and whole numbers for quantities.")
import csv
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vinith@0998",
    database="test"
)

cursor = conn.cursor()

with open("output.csv", newline='', encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        cursor.execute("""
            INSERT INTO voters
            (serial_no, epic_no, name, relative_type,
             relative_name, house_number, age, gender)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            row['serial_no'],
            row['epic_no'],
            row['name'],
            row['relative_type'],
            row['relative_name'],
            row['house_number'],
            row['age'],
            row['gender']
        ))

conn.commit()

print("Inserted Successfully")

cursor.close()
conn.close()
import pytesseract
from PIL import Image
import re
import csv
'''img = Image.open("voter_1.png")
#data = pytesseract.image_to_data(img,output_type=pytesseract.Output.DICT)
text = pytesseract.image_to_string(img)'''

def extract_voter_data(image_path):

    img = Image.open(image_path)

    text = pytesseract.image_to_string(img)

    serial_no = re.search(r'^\s*(\d+)', text, re.MULTILINE)

    epic_no = re.search(r'([A-Z]{3}\d{7})', text)

    name = re.search(r'Name\s*:\s*(.*?)\n',text,re.IGNORECASE)

    husband = re.search(r'Husbands?\s*Name\s*:\s*(.*?)\n',text,re.IGNORECASE)

    father = re.search( r'Fathers?\s*Name\s*:\s*(.*?)\n', text, re.IGNORECASE)
    house = re.search(r'House\s*Number\s*:\s*(.*?)\n',text,re.IGNORECASE    )

    age_gender = re.search(r'Age\s*:\s*(\d+)\s*Gender\s*:\s*(Male|Female)',text,re.IGNORECASE    )

    return {
        "serial_no": serial_no.group(1) if serial_no else None,
        "epic_no": epic_no.group(1) if epic_no else None,
        "name": name.group(1).strip() if name else None,
        "relative_type":
            "Husband" if husband
            else "Father" if father
            else None,
        "relative_name":
            husband.group(1).strip() if husband
            else father.group(1).strip() if father
            else None,
        "house_number":
            house.group(1).strip() if house else None,
        "age":
            int(age_gender.group(1))
            if age_gender else None,
        "gender":
            age_gender.group(2)
            if age_gender else None
    }

#record = extract_voter_data("voter_1.png")
records =[]
for i in range(1, 31):
    record = extract_voter_data(f"voter_{i}.png")
    records.append(record)
    print(i)
#print(records)
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
'''
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("VoterData") \
    .getOrCreate()

df = spark.createDataFrame(records)

df.show(truncate=False)'''
import fitz
import pytesseract
import re
from PIL import Image
from pyspark.sql import SparkSession

# Set path if Tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_file = "ecdata.pdf"

# -----------------------------
# STEP 1: Convert PDF to Images
# -----------------------------

pdf = fitz.open(pdf_file)

all_records = []

for page_no in range(len(pdf)):

    page = pdf[page_no]

    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))

    full_page_img = f"page_{page_no}.png"

    pix.save(full_page_img)

    img = Image.open(full_page_img)

    width, height = img.size

    #print(f"Page {page_no+1} Size: {width} x {height}")

    # ------------------------------------
    # STEP 2: Crop voter boxes
    # ------------------------------------

    boxes = [
        (0, 300, width//3, height//2),
        (width//3, 300, 2*width//3, height//2),
        (2*width//3, 300, width, height//2),

        (0, height//2, width//3, height),
        (width//3, height//2, 2*width//3, height),
        (2*width//3, height//2, width, height)
    ]

    # ------------------------------------
    # STEP 3: OCR each box
    # ------------------------------------

    for idx, box in enumerate(boxes):

        crop = img.crop(box)

        crop_file = f"page_{page_no+1}_voter_{idx+1}.png"

        #crop.save(crop_file)

        text = pytesseract.image_to_string(crop)

        # print for debugging

        # ------------------------------------
        # STEP 4: Parse fields
        # ------------------------------------

        epic = re.search(r'NBT\d+', text)

        name = re.search(
            r'Name\s*:\s*(.+)',
            text,
            re.IGNORECASE
        )

        relation = re.search(
            r'(?:Father|Fathers|Husband|Husbands)\s*Name\s*:\s*(.+)',
            text,
            re.IGNORECASE
        )

        house = re.search(
            r'House\s*Number\s*:\s*(.+)',
            text,
            re.IGNORECASE
        )

        age_gender = re.search(
            r'Age\s*:\s*(\d+).*?Gender\s*:\s*(Male|Female)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if epic:

            record = {
                "epic_no": epic.group(0),
                "name": name.group(1).strip() if name else None,
                "relative_name": relation.group(1).strip() if relation else None,
                "house_no": house.group(1).strip() if house else None,
                "age": int(age_gender.group(1)) if age_gender else None,
                "gender": age_gender.group(2) if age_gender else None
            }

            all_records.append(record)

# ------------------------------------
# STEP 5: Create Spark DataFrame
# ------------------------------------

spark = SparkSession.builder \
    .appName("VoterExtraction") \
    .getOrCreate()

df = spark.createDataFrame(all_records)

df.show(truncate=False)

# ------------------------------------
# STEP 6: Save Results
# ------------------------------------

df.write.csv("voters_csv")

df.write.parquet("voters_parquet")

print(f"Total Records Extracted: {len(all_records)}")
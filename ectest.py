from PIL import Image

img = Image.open("page11.png")

width, height = img.size

# Page layout
cols = 3
rows = 10

# Margins (adjust if needed)
left_margin = 20
right_margin = 20
top_margin = 50
bottom_margin = 50

usable_width = width - left_margin - right_margin
usable_height = height - top_margin - bottom_margin

box_width = usable_width // cols
box_height = usable_height // rows

count = 1

for row in range(rows):
    for col in range(cols):

        left = left_margin + col * box_width
        top = top_margin + row * box_height

        right = left_margin + (col + 1) * box_width
        bottom = top_margin + (row + 1) * box_height

        crop = img.crop((left, top, right, bottom))

        crop.save(f"voter_{count}.png")

        print(f"Saved voter_{count}.png")

        count += 1

print("Done")
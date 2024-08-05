from PIL import Image

im = Image.open("Raw.png")

col, row = int(input("Enter the number of columns: ")), int(input("Enter the number of rows: "))

for i in range(row):
    for j in range(col):
        im.crop((
            int(j * im.width / col),
            int(i * im.height / row),
            int((j + 1) * im.width / col),
            int((i + 1) * im.height / row),
        )).save(f"{i * col + j + 1}.png")
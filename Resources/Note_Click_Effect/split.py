from PIL import Image

im = Image.open("Raw.png")

for i in range(5):
    for j in range(6):
        im.crop((
            int(j * im.width / 6),
            int(i * im.height / 5),
            int((j + 1) * im.width / 6),
            int((i + 1) * im.height / 5),
        )).save(f"{i * 6 + j + 1}.png")
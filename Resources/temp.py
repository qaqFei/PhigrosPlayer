from PIL import Image

def p(n):
    im = Image.open(f"./{n}.png")
    nim = Image.new("RGBA", (max(im.width, im.height), max(im.width, im.height)), (0, 0, 0, 0))
    nim.paste(
        im,
        (int((nim.width - im.width) / 2), int((nim.height - im.height) / 2))
    )
    nim.save(f"./{n}.png")

p("PUIBack")
p("PUIResume")
p("PUIRetry")
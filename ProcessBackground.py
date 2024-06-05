from sys import argv

from PIL import Image,ImageFilter,ImageEnhance

im = Image.open(argv[1])
ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur((im.width + im.height) / 300))).enhance(0.4).save(argv[2])
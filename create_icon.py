from PIL import Image, ImageDraw

def create_favicon():
    img = Image.new('RGB', (256, 256), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((80,100), "DLNA", fill=(255,255,0))
    img.save('favicon.ico')
    print("Created favicon.ico")

if __name__ == "__main__":
    create_favicon()

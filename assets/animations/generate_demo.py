from pathlib import Path
import math

from PIL import Image, ImageDraw


OUT_DIR = Path(__file__).resolve().parent
SIZE = 160
SCALE = 3
FRAME_COUNT = 12


def make_frame(index):
    bob = round(2 * (1 - math.cos(index * 2 * math.pi / FRAME_COUNT)))
    image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE))
    draw = ImageDraw.Draw(image)

    def shape(points, fill, outline="#29233d", width=3):
        points = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
        draw.polygon(points, fill=fill, outline=outline, width=width * SCALE)

    def ellipse(box, fill, outline="#29233d", width=3):
        box = tuple(round(value * SCALE) for value in box)
        draw.ellipse(box, fill=fill, outline=outline, width=width * SCALE)

    def line(points, fill, width=2):
        points = [(round(x * SCALE), round(y * SCALE)) for x, y in points]
        draw.line(points, fill=fill, width=width * SCALE, joint="curve")

    # Small feet and pointed ears make the idle sprite readable at desktop size.
    ellipse((55, 115 + bob, 76, 130 + bob), "#7e62d6")
    ellipse((84, 115 + bob, 105, 130 + bob), "#7e62d6")
    shape([(48, 67 + bob), (51, 42 + bob), (72, 56 + bob), (88, 56 + bob), (109, 42 + bob), (112, 67 + bob)], "#a991ff")
    ellipse((43, 53 + bob, 117, 124 + bob), "#a991ff")
    ellipse((52, 62 + bob, 108, 117 + bob), "#b9a8ff", outline=None, width=0)
    ellipse((71, 78 + bob, 89, 104 + bob), "#fff1d6", outline="#4c3e72", width=2)

    blink = index in (5, 6)
    for x in (65, 95):
        if blink:
            line([(x - 4, 82 + bob), (x, 84 + bob), (x + 4, 82 + bob)], "#332a4a", 2)
        else:
            ellipse((x - 3, 78 + bob, x + 3, 86 + bob), "#332a4a", outline=None, width=0)
            ellipse((x - 1, 79 + bob, x + 1, 81 + bob), "#ffffff", outline=None, width=0)
    ellipse((52, 90 + bob, 63, 96 + bob), "#f29bb6", outline=None, width=0)
    ellipse((97, 90 + bob, 108, 96 + bob), "#f29bb6", outline=None, width=0)
    line([(77, 91 + bob), (80, 94 + bob), (83, 91 + bob)], "#6b4a72", 1)
    ellipse((77, 105 + bob, 83, 111 + bob), "#8b69df", outline=None, width=0)

    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    rgba_frames = [make_frame(index) for index in range(FRAME_COUNT)]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rgba_frames[0].save(OUT_DIR / "preview.png")

    atlas = Image.new("RGB", (SIZE * FRAME_COUNT, SIZE), "white")
    for index, frame in enumerate(rgba_frames):
        atlas.paste(frame.convert("RGB"), (index * SIZE, 0), frame.getchannel("A"))
    palette_source = atlas.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = palette_source.getpalette()
    palette.extend([0] * (768 - len(palette)))
    palette[255 * 3:255 * 3 + 3] = [0, 0, 0]
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette)

    frames = []
    for frame in rgba_frames:
        indexed = frame.convert("RGB").quantize(palette=palette_image)
        indexed.putpalette(palette)
        transparent = frame.getchannel("A").point(lambda alpha: 255 if alpha < 128 else 0)
        indexed.paste(255, mask=transparent)
        frames.append(indexed)

    frames[0].save(
        OUT_DIR / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=False,
    )


if __name__ == "__main__":
    main()

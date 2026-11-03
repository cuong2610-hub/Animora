import io

from PIL import Image
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap


def compose_layers(layers, opacity=100, rotation=0):
    visible = [frames for frames, enabled in layers if enabled and frames]
    if not visible:
        return []
    frame_count = max(len(frames) for frames in visible)
    # ponytail: composed editor frames stay in RAM; stream composition for long high-resolution projects.
    width = max(frame.width() for frames in visible for frame in frames)
    height = max(frame.height() for frames in visible for frame in frames)
    result = []
    for index in range(frame_count):
        canvas = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        for frames in visible:
            frame = frames[index % len(frames)]
            painter.save()
            painter.setOpacity(max(0, min(100, opacity)) / 100)
            painter.translate(width / 2, height / 2)
            painter.rotate(rotation)
            painter.translate(-width / 2, -height / 2)
            painter.drawPixmap((width - frame.width()) // 2, (height - frame.height()) // 2, frame)
            painter.restore()
        painter.end()
        result.append(QPixmap.fromImage(canvas))
    return result


def export_gif(frames, path, fps=24):
    if not frames:
        raise ValueError("Không có frame để export.")
    images = []
    for frame in frames:
        image = frame.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        buffer = QBuffer()
        data = QByteArray()
        buffer.setBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        buffer.close()
        images.append(Image.open(io.BytesIO(bytes(data))).convert("RGBA"))

    atlas_width = max(image.width for image in images)
    atlas_height = max(image.height for image in images)
    atlas = Image.new("RGB", (atlas_width * len(images), atlas_height), "white")
    for index, image in enumerate(images):
        atlas.paste(image.convert("RGB"), (index * atlas_width, 0), image.getchannel("A"))
    palette_source = atlas.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = palette_source.getpalette()
    palette.extend([0] * (768 - len(palette)))
    palette[255 * 3:255 * 3 + 3] = [0, 0, 0]
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(palette)

    indexed_frames = []
    for image in images:
        indexed = image.convert("RGB").quantize(palette=palette_image)
        indexed.putpalette(palette)
        alpha = image.getchannel("A").point(lambda value: 255 if value < 128 else 0)
        indexed.paste(255, mask=alpha)
        indexed_frames.append(indexed)
    indexed_frames[0].save(
        path,
        save_all=True,
        append_images=indexed_frames[1:],
        duration=max(1, round(1000 / max(1, fps))),
        loop=0,
        transparency=255,
        disposal=2,
        optimize=False,
    )

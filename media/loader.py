from PIL import Image, ImageSequence
from PySide6.QtGui import QImage, QPixmap


def _to_qimage(image):
    rgba = image.convert("RGBA")
    width, height = rgba.size
    return QImage(rgba.tobytes(), width, height, width * 4, QImage.Format.Format_RGBA8888).copy()


def _to_pixmap(image):
    return QPixmap.fromImage(image)


def load_animation(path):
    images, durations, fps = load_animation_images(path)
    return [_to_pixmap(image) for image in images], durations, fps


def load_animation_images(path):
    frames, durations = [], []
    with Image.open(path) as image:
        for frame in ImageSequence.Iterator(image):
            frames.append(_to_qimage(frame))
            durations.append(max(1, int(frame.info.get("duration", image.info.get("duration", 100)))))
    if not frames:
        return [], [], 24
    fps = max(1, round(1000 / (sum(durations) / len(durations))))
    return frames, durations, fps


def load_sprite_sheet(path, columns, rows, fps=12):
    if not isinstance(columns, int) or not isinstance(rows, int) or columns < 1 or rows < 1:
        raise ValueError("Số cột và hàng phải là số nguyên lớn hơn 0.")
    with Image.open(path) as image:
        if image.width % columns or image.height % rows:
            raise ValueError("Kích thước sprite sheet phải chia hết cho số cột và hàng.")
        cell_width, cell_height = image.width // columns, image.height // rows
        frames = [
            _to_pixmap(_to_qimage(image.crop((column * cell_width, row * cell_height, (column + 1) * cell_width, (row + 1) * cell_height))))
            for row in range(rows)
            for column in range(columns)
        ]
    duration = max(1, round(1000 / max(1, fps)))
    return frames, [duration] * len(frames), max(1, fps)

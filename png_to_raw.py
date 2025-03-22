from PIL import Image
import numpy as np
import os

def convert_png_to_raw(input_png_path: str, output_raw_path: str):
    """
    Преобразует PNG-изображение в RAW-формат и сохраняет его.
    :param input_png_path: Путь к PNG-изображению.
    :param output_raw_path: Путь для сохранения RAW-файла.
    """
    # Открываем изображение
    image = Image.open(input_png_path)
    width, height = image.size

    # Преобразуем изображение в массив NumPy
    image_data = np.array(image)

    # Проверяем режим изображения
    if image.mode == "1":  # Черно-белое изображение
        # Упаковываем биты в байты
        image_data = np.packbits(image_data)
    elif image.mode == "L":  # Серое изображение
        pass  # Данные уже в правильном формате
    elif image.mode == "RGB":  # Цветное изображение
        pass  # Данные уже в правильном формате
    else:
        raise ValueError(f"Неподдерживаемый режим изображения: {image.mode}")

    # Сохраняем данные в RAW-файл
    with open(output_raw_path, "wb") as f:
        # Сохраняем размеры изображения (4 байта на ширину и 4 байта на высоту)
        f.write(width.to_bytes(4, "big"))
        f.write(height.to_bytes(4, "big"))
        # Сохраняем пиксельные данные
        f.write(image_data.tobytes())

    print(f"Изображение {input_png_path} преобразовано в RAW: {output_raw_path}")


# Пример использования
if __name__ == "__main__":
    # Пути к PNG-изображениям
    bw_png_path = "C:/OPP/compression_project/tests/black_white_image.png"
    gray_png_path = "C:/OPP/compression_project/tests/gray_image.png"
    color_png_path = "C:/OPP/compression_project/tests/color_image.png"

    # Пути для сохранения RAW-файлов
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Преобразование PNG в RAW
    convert_png_to_raw(bw_png_path, bw_raw_path)
    convert_png_to_raw(gray_png_path, gray_raw_path)
    convert_png_to_raw(color_png_path, color_raw_path)
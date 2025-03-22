import heapq
from collections import defaultdict, Counter
import pickle
from PIL import Image
import numpy as np
import os
import math


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Рассчитывает коэффициент сжатия.
    :param original_size: Размер исходного файла в байтах.
    :param compressed_size: Размер сжатого файла в байтах.
    :return: Коэффициент сжатия.
    """
    return original_size / compressed_size


def calculate_entropy(data: bytes) -> float:
    """
    Рассчитывает энтропию файла.
    :param data: Данные файла в виде байтовой строки.
    :return: Энтропия файла.
    """
    if not data:
        return 0.0

    # Считаем частоту каждого символа
    frequency = Counter(data)
    total_symbols = len(data)

    # Рассчитываем энтропию
    entropy = 0.0
    for count in frequency.values():
        probability = count / total_symbols
        entropy -= probability * math.log2(probability)

    return entropy


def analyze_file(file_path: str):
    """
    Анализирует файл: рассчитывает его размер и энтропию.
    :param file_path: Путь к файлу.
    :return: Размер файла и его энтропия.
    """
    with open(file_path, "rb") as f:
        data = f.read()
    file_size = len(data)
    entropy = calculate_entropy(data)
    return file_size, entropy


def analyze_compression(input_file: str, compressed_file: str):
    """
    Анализирует сжатие файла: рассчитывает коэффициент сжатия и энтропию.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    """
    original_size, original_entropy = analyze_file(input_file)
    compressed_size, compressed_entropy = analyze_file(compressed_file)

    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)


def lz77_encode(data: bytes, buffer_size: int = 512) -> bytes:
    """
    Сжимает данные с использованием алгоритма LZ77.
    :param data: Данные для сжатия.
    :param buffer_size: Размер буфера для поиска совпадений.
    :return: Сжатые данные.
    """
    compressed_data = []
    i = 0
    while i < len(data):
        match_offset, match_length = 0, 0
        buffer_start = max(0, i - buffer_size)
        buffer = data[buffer_start:i]

        # Ищем совпадения в буфере
        for offset in range(1, len(buffer) + 1):
            current_length = 0
            while (i + current_length < len(data) and
                   len(buffer) - offset + current_length < len(buffer) and
                   data[i + current_length] == buffer[len(buffer) - offset + current_length]):
                current_length += 1
            if current_length > match_length:
                match_offset, match_length = offset, current_length

        # Ограничиваем match_offset и match_length значением 255
        match_offset = min(match_offset, 255)
        match_length = min(match_length, 255)

        # Получаем следующий символ
        next_char = data[i + match_length] if i + match_length < len(data) else 0

        # Проверяем, что match_offset не превышает длину буфера
        if match_offset > len(buffer):
            match_offset, match_length = 0, 0  # Сбрасываем, если offset некорректен

        # Добавляем тройку (offset, length, next_char) в сжатые данные
        compressed_data.append(match_offset)
        compressed_data.append(match_length)
        compressed_data.append(next_char)

        # Перемещаем указатель
        i += match_length + 1

    return bytes(compressed_data)


def lz77_decode(compressed_data: bytes) -> bytes:
    """
    Декодирование данных, сжатых с использованием алгоритма LZ77.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decompressed_data = []  # Здесь хранятся декодированные данные
    i = 0  # Индекс для прохода по сжатым данным

    # Проходим по сжатым данным блоками по 3 байта (offset, length, next_char)
    while i + 2 < len(compressed_data):
        match_offset = compressed_data[i]  # Смещение назад
        match_length = compressed_data[i + 1]  # Длина совпадения
        next_char = compressed_data[i + 2]  # Следующий символ

        # Если offset и length равны 0, это конец данных
        if match_offset == 0 and match_length == 0:
            break

        # Проверяем, что match_offset не превышает длину decompressed_data
        if match_offset > len(decompressed_data):
            # Если offset больше, чем текущая длина данных, это ошибка
            raise ValueError(
                f"Invalid match_offset: {match_offset} > {len(decompressed_data)}. "
                f"Data may be corrupted or compression algorithm is incorrect."
            )

        # Восстанавливаем данные
        for _ in range(match_length):
            # Копируем символ из уже декодированных данных
            decompressed_data.append(decompressed_data[-match_offset])

        # Добавляем следующий символ
        decompressed_data.append(next_char)

        # Перемещаем указатель на следующую тройку
        i += 3

    return bytes(decompressed_data)


def compress_file(input_file: str, output_file: str, buffer_size: int = 512):
    """
    Сжимает файл с использованием алгоритма LZ77.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    :param buffer_size: Размер буфера для LZ77.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()  # Читаем весь файл
        compressed_data = lz77_encode(data, buffer_size)  # Сжимаем целиком
        f_out.write(compressed_data)


def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом LZ77.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()  # Читаем весь сжатый файл
        decompressed_data = lz77_decode(compressed_data)  # Декодируем целиком
        f_out.write(decompressed_data)  # Записываем восстановленные данные


def convert_raw_to_image(input_raw_path: str, output_image_path: str, image_mode: str):
    """
    Преобразует RAW-файл обратно в изображение.
    :param input_raw_path: Путь к RAW-файлу.
    :param output_image_path: Путь для сохранения изображения.
    :param image_mode: Режим изображения ("1", "L", "RGB").
    """
    # Чтение RAW-файла
    with open(input_raw_path, "rb") as f:
        # Читаем размеры изображения (первые 8 байт)
        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
        raw_data = f.read()

    # Преобразование данных в массив NumPy
    image_data = np.frombuffer(raw_data, dtype=np.uint8)

    # Проверка соответствия данных и размеров
    if image_mode == "1":
        # Для режима "1" каждый байт содержит 8 пикселей
        expected_pixels = width * height
        expected_bytes = (expected_pixels + 7) // 8  # Округление вверх
        if len(image_data) < expected_bytes:
            raise ValueError(f"Недостаточно данных для режима '1'. Ожидалось {expected_bytes} байт, получено {len(image_data)}.")
        image_data = np.unpackbits(image_data)[:expected_pixels]  # Обрезаем лишние данные
        image_data = image_data.reshape((height, width))
    elif image_mode == "L":
        expected_pixels = width * height
        if len(image_data) < expected_pixels:
            raise ValueError(f"Недостаточно данных для режима 'L'. Ожидалось {expected_pixels} байт, получено {len(image_data)}.")
        image_data = image_data.reshape((height, width))
    elif image_mode == "RGB":
        expected_pixels = width * height * 3
        if len(image_data) < expected_pixels:
            raise ValueError(f"Недостаточно данных для режима 'RGB'. Ожидалось {expected_pixels} байт, получено {len(image_data)}.")
        image_data = image_data.reshape((height, width, 3))
    else:
        raise ValueError(f"Неподдерживаемый режим изображения: {image_mode}")

    # Создаем изображение
    image = Image.fromarray(image_data, mode=image_mode)

    # Сохраняем изображение
    image.save(output_image_path)

    print(f"RAW-файл {input_raw_path} преобразован в изображение: {output_image_path}")


# Основная функция
if __name__ == "__main__":
    # Пути к RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"

    # Сжатие RAW-файлов с использованием LZ77
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.raw"

    # Декомпрессия RAW-файлов с использованием LZ77
    decompress_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file(color_compressed_path, color_decompressed_raw_path)

    # Преобразование RAW обратно в изображения
    convert_raw_to_image(bw_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.png", "1")
    convert_raw_to_image(gray_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.png", "L")
    convert_raw_to_image(color_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.png", "RGB")
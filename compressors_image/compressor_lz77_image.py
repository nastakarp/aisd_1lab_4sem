import os
import math
from collections import Counter

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

    frequency = Counter(data)
    total_symbols = len(data)
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
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, "rb") as f:
        data = f.read()
    file_size = len(data)
    entropy = calculate_entropy(data)
    return file_size, entropy

def lz77_encode(data: bytes, buffer_size: int = 512) -> bytes:
    """
    Кодирует данные с использованием алгоритма LZ77.
    :param data: Исходные данные (байтовая строка).
    :param buffer_size: Размер буфера для поиска совпадений.
    :return: Сжатые данные (байтовая строка).
    """
    encoded_data = bytearray()
    i = 0
    n = len(data)

    while i < n:
        max_length = 0
        max_offset = 0
        search_start = max(0, i - buffer_size)
        search_end = i

        for length in range(min(255, n - i), 0, -1):
            substring = data[i:i + length]
            offset = data[search_start:search_end].rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = search_end - search_start - offset
                break

        if max_length > 0:
            encoded_data.extend([(max_offset >> 8) & 0xFF, max_offset & 0xFF, (max_length >> 8) & 0xFF, max_length & 0xFF])
            i += max_length
        else:
            encoded_data.extend([0, 0, 0, 0, data[i]])
            i += 1

    return bytes(encoded_data)

def lz77_decode(encoded_data: bytes) -> bytes:
    """
    Декодирует данные, сжатые с использованием алгоритма LZ77.
    :param encoded_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)

    while i < n:
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])

    return bytes(decoded_data)

def compress_file(input_file: str, output_file: str, buffer_size: int = 512):
    """
    Сжимает файл с использованием алгоритма LZ77.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    :param buffer_size: Размер буфера для LZ77.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Файл {input_file} не найден.")

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = lz77_encode(data, buffer_size)
        f_out.write(compressed_data)

def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом LZ77.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Файл {input_file} не найден.")

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()
        decompressed_data = lz77_decode(compressed_data)
        f_out.write(decompressed_data)

def analyze_compression(original_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие файла.
    :param original_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к восстановленному файлу.
    """
    # Анализ исходного файла
    original_size, original_entropy = analyze_file(original_file)
    print(f"Исходный файл: {original_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")

    # Анализ сжатого файла
    compressed_size, _ = analyze_file(compressed_file)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.3f}")

    # Анализ восстановленного файла
    decompressed_size, _ = analyze_file(decompressed_file)
    print(f"Размер восстановленного файла: {decompressed_size} байт")

    # Проверка совпадения размеров исходного и восстановленного файлов
    if original_size == decompressed_size:
        print("Размеры исходного и восстановленного файлов совпадают.")
    else:
        print("Ошибка: размеры исходного и восстановленного файлов не совпадают.")
    print("-" * 40)

def test_buffer_sizes(input_file: str, output_dir: str, buffer_sizes: list):
    """
    Тестирует сжатие с разными размерами буфера.
    :param input_file: Путь к исходному файлу.
    :param output_dir: Директория для сохранения сжатых файлов.
    :param buffer_sizes: Список размеров буфера для тестирования.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Файл {input_file} не найден.")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    original_size, original_entropy = analyze_file(input_file)
    print(f"Исходный файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print("-" * 40)

    results = []
    for buffer_size in buffer_sizes:
        print(f"Тестирование с buffer_size = {buffer_size}...")

        compressed_file = os.path.join(output_dir, f"compressed_{buffer_size}.bin")
        decompressed_file = os.path.join(output_dir, f"decompressed_{buffer_size}.bin")

        compress_file(input_file, compressed_file, buffer_size=buffer_size)
        decompress_file(compressed_file, decompressed_file)

        compressed_size, _ = analyze_file(compressed_file)
        compression_ratio = calculate_compression_ratio(original_size, compressed_size)

        with open(input_file, "rb") as f1, open(decompressed_file, "rb") as f2:
            assert f1.read() == f2.read(), "Ошибка: распакованные данные не совпадают с исходными"

        results.append((buffer_size, compressed_size, compression_ratio))
        print(f"Размер сжатого файла: {compressed_size} байт")
        print(f"Коэффициент сжатия: {compression_ratio:.3f}")
        print("-" * 40)

    print("\nИтоговые результаты:")
    print("Buffer Size | Compressed Size | Compression Ratio")
    print("-" * 40)
    for buffer_size, compressed_size, compression_ratio in results:
        print(f"{buffer_size:11} | {compressed_size:15} | {compression_ratio:.3f}")

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

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.raw"

    # Декомпрессия RAW-файлов с использованием LZ77
    decompress_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file(color_compressed_path, color_decompressed_raw_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path, bw_decompressed_raw_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path, gray_decompressed_raw_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path, color_decompressed_raw_path)
# compressor_ha
from algorithms.huffman import count_symb, build_huffman_tree, generate_codes
import pickle
from PIL import Image
import numpy as np
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


def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие файла: рассчитывает коэффициент сжатия, энтропию и размер декомпрессированного файла.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к декомпрессированному файлу.
    """
    # Анализируем исходный файл
    original_size, original_entropy = analyze_file(input_file)
    # Анализируем сжатый файл
    compressed_size, compressed_entropy = analyze_file(compressed_file)
    # Анализируем декомпрессированный файл
    decompressed_size, _ = analyze_file(decompressed_file)

    # Рассчитываем коэффициент сжатия
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    # Выводим результаты
    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Размер декомпрессированного файла: {decompressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.3f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)


def huffman_compress(data: bytes) -> bytes:
    """
    Кодирование Хаффмана с сохранением таблицы кодов.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    frequency = count_symb(data)
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = generate_codes(huffman_tree)

    encoded_bits = "".join([huffman_codes[byte] for byte in data])
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += "0" * padding
    encoded_bytes = bytes([int(encoded_bits[i:i + 8], 2) for i in range(0, len(encoded_bits), 8)])

    # Сохраняем таблицу кодов и padding в сжатых данных
    metadata = {
        "codes": huffman_codes,
        "padding": padding,
    }
    metadata_bytes = pickle.dumps(metadata)
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


def huffman_decompress(encoded_data: bytes) -> bytes:
    """
    Декодирование Хаффмана с использованием таблицы кодов.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Извлекаем длину метаданных
    metadata_length = int.from_bytes(encoded_data[:4], "big")
    metadata_bytes = encoded_data[4:4 + metadata_length]
    encoded_bytes = encoded_data[4 + metadata_length:]

    # Восстанавливаем таблицу кодов и padding
    metadata = pickle.loads(metadata_bytes)
    huffman_codes = metadata["codes"]
    padding = metadata["padding"]

    # Преобразуем байты в битовую строку
    encoded_bits = "".join([f"{byte:08b}" for byte in encoded_bytes])
    encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits

    # Создаем таблицу для обратного поиска (битовая строка -> символ)
    reverse_codes = {v: k for k, v in huffman_codes.items()}

    # Декодируем битовую строку
    current_bits = ""
    decoded_data = []
    for bit in encoded_bits:
        current_bits += bit
        if current_bits in reverse_codes:
            decoded_data.append(reverse_codes[current_bits])
            current_bits = ""

    return bytes(decoded_data)


def compress_file(input_file: str, output_file: str):
    """
    Сжимает файл с использованием алгоритма Хаффмана.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    with open(input_file, "rb") as f:
        data = f.read()

    compressed_data = huffman_compress(data)

    with open(output_file, "wb") as f:
        f.write(compressed_data)


def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом Хаффмана.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    with open(input_file, "rb") as f:
        compressed_data = f.read()

    decompressed_data = huffman_decompress(compressed_data)

    with open(output_file, "wb") as f:
        f.write(decompressed_data)


def compress_raw_file(input_raw_path: str, output_compressed_path: str):
    """
    Сжимает RAW-файл с использованием алгоритма Хаффмана.
    :param input_raw_path: Путь к RAW-файлу.
    :param output_compressed_path: Путь для сохранения сжатого файла.
    """
    # Чтение RAW-файла
    with open(input_raw_path, "rb") as f:
        raw_data = f.read()

    # Сжатие данных
    compressed_data = huffman_compress(raw_data)

    # Сохранение сжатых данных
    with open(output_compressed_path, "wb") as f:
        f.write(compressed_data)

    print(f"RAW-файл {input_raw_path} сжат и сохранен в {output_compressed_path}")


# Декомпрессия RAW-файла
def decompress_raw_file(input_compressed_path: str, output_raw_path: str):
    """
    Декомпрессия RAW-файла.
    :param input_compressed_path: Путь к сжатому файлу.
    :param output_raw_path: Путь для сохранения восстановленного RAW-файла.
    """
    # Чтение сжатого файла
    with open(input_compressed_path, "rb") as f:
        compressed_data = f.read()

    # Декомпрессия данных
    decompressed_data = huffman_decompress(compressed_data)

    # Сохранение восстановленного RAW-файла
    with open(output_raw_path, "wb") as f:
        f.write(decompressed_data)

    print(f"Сжатый файл {input_compressed_path} декомпрессирован в {output_raw_path}")

# Пример использования
if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_ha.txt"
    # Сжимаем файл enwik7
    compress_file(input_data, compress_data)
    # Распаковываем файл
    decompress_file(compress_data, decompress_data)
    # Анализируем сжатие
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_ha.bin"
    # Сжимаем файл test2
    compress_file(input_data_ru, compress_data_ru)
    # Распаковываем файл
    decompress_file(compress_data_ru, decompress_data_ru)
    # Анализируем сжатие
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_compressed.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_decompressed.bin"
    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    # Анализируем сжатие
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.")
    # Пути к исходным RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"

    # Сжатие RAW-файлов
    compress_raw_file(bw_raw_path, bw_compressed_path)
    compress_raw_file(gray_raw_path, gray_compressed_path)
    compress_raw_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.raw"

    # Декомпрессия RAW-файлов
    decompress_raw_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_raw_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_raw_file(color_compressed_path, color_decompressed_raw_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path, bw_decompressed_raw_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path, gray_decompressed_raw_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path, color_decompressed_raw_path)

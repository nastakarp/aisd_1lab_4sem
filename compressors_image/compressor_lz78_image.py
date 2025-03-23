import os
import math
from collections import defaultdict, Counter
from PIL import Image
import numpy as np
import struct


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


# Реализация LZ78
class LZ78Encoder:
    def __init__(self):
        self.dictionary = {}  # Словарь для хранения строк
        self.next_code = 1  # Следующий доступный код

    def encode(self, data: bytes) -> list:
        """
        Кодирует данные с использованием алгоритма LZ78.
        :param data: Входные данные (байтовая строка).
        :return: Закодированные данные (список кортежей (код, символ)).
        """
        encoded_data = []
        current_string = b""
        for byte in data:
            new_string = current_string + bytes([byte])
            if new_string not in self.dictionary:
                # Добавляем новую строку в словарь
                self.dictionary[new_string] = self.next_code
                self.next_code += 1
                if current_string:
                    encoded_data.append((self.dictionary[current_string], byte))
                else:
                    encoded_data.append((0, byte))
                current_string = b""
            else:
                current_string = new_string
        if current_string:
            encoded_data.append((self.dictionary[current_string], 0))
        return encoded_data


class LZ78Decoder:
    def __init__(self):
        self.dictionary = {0: b""}  # Инициализация словаря

    def decode(self, encoded_data: list) -> bytes:
        """
        Декодирует данные, сжатые с использованием алгоритма LZ78.
        :param encoded_data: Закодированные данные (список кортежей (код, символ)).
        :return: Восстановленные данные (байтовая строка).
        """
        decoded_data = []
        for code, byte in encoded_data:
            if code == 0:
                # Если код равен 0, добавляем новый символ в словарь
                new_string = bytes([byte])
                decoded_data.append(new_string)
                self.dictionary[len(self.dictionary)] = new_string
            else:
                # Если код не равен 0, ищем строку в словаре
                if code not in self.dictionary:
                    raise ValueError(f"Код {code} отсутствует в словаре. Данные повреждены.")
                string = self.dictionary[code]
                new_string = string + bytes([byte]) if byte != 0 else string
                decoded_data.append(new_string)
                # Добавляем новую строку в словарь
                self.dictionary[len(self.dictionary)] = new_string
        return b"".join(decoded_data)


def compress_lz78(data: bytes) -> bytes:
    """
    Сжимает данные с использованием алгоритма LZ78.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    encoder = LZ78Encoder()
    encoded_data = encoder.encode(data)

    # Преобразуем список кортежей в байты
    compressed_data = []
    for code, byte in encoded_data:
        compressed_data.append(code.to_bytes(2, byteorder="big"))  # Код (2 байта)
        compressed_data.append(bytes([byte]))  # Символ (1 байт)
    return b"".join(compressed_data)


def decompress_lz78(compressed_data: bytes) -> bytes:
    """
    Распаковывает данные, сжатые с использованием алгоритма LZ78.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    if len(compressed_data) % 3 != 0:
        raise ValueError("Некорректный размер сжатых данных. Размер должен быть кратен 3 байтам.")

    encoded_data = []
    for i in range(0, len(compressed_data), 3):
        try:
            code = int.from_bytes(compressed_data[i:i+2], byteorder="big")
            byte = compressed_data[i+2]
            encoded_data.append((code, byte))
        except struct.error as e:
            raise ValueError(f"Ошибка при распаковке данных: {e}")

    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)

def compress_file(input_file: str, output_file: str):
    """
    Сжимает файл с использованием алгоритма LZ78.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()  # Читаем весь файл
        compressed_data = compress_lz78(data)  # Сжимаем данные
        f_out.write(compressed_data)


def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом LZ78.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()  # Читаем весь сжатый файл
        decompressed_data = decompress_lz78(compressed_data)  # Распаковываем данные
        f_out.write(decompressed_data)


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

    # Сжатие RAW-файлов с использованием LZ78
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

    # Декомпрессия RAW-файлов с использованием LZ78
    decompress_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file(color_compressed_path, color_decompressed_raw_path)

    print("Все операции завершены.")

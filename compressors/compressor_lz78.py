import os
import math
import struct
from collections import Counter

# Функции для анализа сжатия (из предыдущего кода)
def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    return original_size / compressed_size

def calculate_entropy(data: bytes) -> float:
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
    with open(file_path, "rb") as f:
        data = f.read()
    file_size = len(data)
    entropy = calculate_entropy(data)
    return file_size, entropy

def analyze_compression(input_file: str, compressed_file: str):
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

# Реализация LZ78 (из вашего кода)
class LZ78Encoder:
    def __init__(self):
        self.dictionary = {}
        self.next_code = 1

    def encode(self, data: bytes) -> list:
        encoded_data = []
        current_string = b""
        for byte in data:
            new_string = current_string + bytes([byte])
            if new_string not in self.dictionary:
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
        self.dictionary = {0: b""}

    def decode(self, encoded_data: list) -> bytes:
        decoded_data = []
        for code, byte in encoded_data:
            if code == 0:
                decoded_data.append(bytes([byte]))
                self.dictionary[len(self.dictionary)] = bytes([byte])
            else:
                string = self.dictionary[code]
                if byte != 0:
                    new_string = string + bytes([byte])
                    decoded_data.append(new_string)
                    self.dictionary[len(self.dictionary)] = new_string
                else:
                    decoded_data.append(string)
        return b"".join(decoded_data)

def compress_lz78(data: bytes) -> bytes:
    """
    Компрессор: LZ78.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    encoder = LZ78Encoder()
    encoded_data = encoder.encode(data)

    # Преобразуем список кортежей в байты
    compressed_data = []
    for code, byte in encoded_data:
        # Упаковываем код (2 байта) и байт (1 байт)
        compressed_data.extend(struct.pack(">HB", code, byte))
    return b"".join(compressed_data)

def decompress_lz78(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: LZ78.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Преобразуем байты в список кортежей
    encoded_data = []
    for i in range(0, len(compressed_data), 3):
        # Распаковываем код (2 байта) и байт (1 байт)
        code, byte = struct.unpack_from(">HB", compressed_data, i)
        encoded_data.append((code, byte))

    # Декодируем LZ78
    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)

# Функции для работы с файлами
def compress_file_lz78(input_file: str, output_file: str):
    """
    Сжимает файл с использованием алгоритма LZ78.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = compress_lz78(data)
        f_out.write(compressed_data)

def decompress_file_lz78(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом LZ78.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()
        decompressed_data = decompress_lz78(compressed_data)
        f_out.write(decompressed_data)

# Основной блок
if __name__ == "__main__":
    # Обработка файла enwik7 (английский текст)
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz78.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz78.txt"

    # Сжимаем файл enwik7 с использованием LZ78
    compress_file_lz78(input_data, compress_data)
    print("Сжатие enwik7 с использованием LZ78 завершено.")

    # Распаковываем файл
    decompress_file_lz78(compress_data, decompress_data)
    print("Распаковка enwik7 завершена.")

    # Анализируем сжатие
    analyze_compression(input_data, compress_data)
    print("Анализ сжатия enwik7 завершен.")
    print("-" * 40)

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_lz78.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_lz78.txt"

    # Сжимаем файл test2 с использованием LZ78
    compress_file_lz78(input_data_ru, compress_data_ru)
    print("Сжатие русского текста с использованием LZ78 завершено.")

    # Распаковываем файл
    decompress_file_lz78(compress_data_ru, decompress_data_ru)
    print("Распаковка русского текста завершена.")

    # Анализируем сжатие
    analyze_compression(input_data_ru, compress_data_ru)
    print("Анализ сжатия русского текста завершен.")
    print("-" * 40)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_lz78.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_lz78_decompressed.bin"

    # Сжимаем бинарный файл с использованием LZ78
    compress_file_lz78(binary_input, binary_compressed)
    print("Сжатие бинарного файла с использованием LZ78 завершено.")

    # Распаковываем бинарный файл
    decompress_file_lz78(binary_compressed, binary_decompressed)
    print("Распаковка бинарного файла завершена.")

    # Анализируем сжатие
    analyze_compression(binary_input, binary_compressed)
    print("Анализ сжатия бинарного файла завершен.")
    print("-" * 40)

    print("Все операции завершены.")
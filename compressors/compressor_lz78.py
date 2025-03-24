import os
import math
import struct
from collections import Counter

# Функции для анализа сжатия
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

def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие файла.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к восстановленному файлу.
    """
    # Анализ исходного файла
    original_size, original_entropy = analyze_file(input_file)
    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")

    # Анализ сжатого файла
    compressed_size, compressed_entropy = analyze_file(compressed_file)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")

    # Анализ восстановленного файла
    decompressed_size, _ = analyze_file(decompressed_file)
    print(f"Размер восстановленного файла: {decompressed_size} байт")

    # Проверка совпадения размеров исходного и восстановленного файлов
    if original_size == decompressed_size:
        print("Размеры исходного и восстановленного файлов совпадают.")
    else:
        print("Ошибка: размеры исходного и восстановленного файлов не совпадают.")
    print("-" * 40)

# Реализация LZ78
class LZ78Encoder:
    def __init__(self):
        self.dictionary = {b'': 0}
        self.next_code = 1

    def encode(self, data: bytes) -> list:
        encoded_data = []
        current_string = b''

        for byte in data:
            new_string = current_string + bytes([byte])
            if new_string in self.dictionary:
                current_string = new_string
            else:
                encoded_data.append((self.dictionary[current_string], byte))
                self.dictionary[new_string] = self.next_code
                self.next_code += 1
                current_string = b''

        if current_string:
            # Для последней последовательности используем byte=256 как маркер конца
            encoded_data.append((self.dictionary[current_string], 256))

        return encoded_data


class LZ78Decoder:
    def __init__(self):
        self.dictionary = {0: b''}

    def decode(self, encoded_data: list) -> bytes:
        decoded_data = []

        for code, byte in encoded_data:
            if code not in self.dictionary:
                raise ValueError(f"Invalid code {code} in encoded data")

            if byte == 256:  # Маркер конца
                entry = self.dictionary[code]
            else:
                entry = self.dictionary[code] + bytes([byte])
                # Добавляем в словарь только если это не последняя запись
                if byte != 256:
                    self.dictionary[len(self.dictionary)] = entry

            decoded_data.append(entry)

        return b''.join(decoded_data)


def compress_lz78(data: bytes) -> bytes:
    encoder = LZ78Encoder()
    encoded_data = encoder.encode(data)

    # Определяем необходимый размер для хранения кодов
    max_code = max((code for code, _ in encoded_data), default=0)
    code_bytes = (max_code.bit_length() + 7) // 8
    code_bytes = max(1, code_bytes)  # Минимум 1 байт

    compressed_data = bytearray()
    for code, byte in encoded_data:
        compressed_data.extend(code.to_bytes(code_bytes, 'big'))
        # Для byte=256 используем 2 байта
        if byte == 256:
            compressed_data.extend((255, 255))
        else:
            compressed_data.append(byte)

    # Добавляем заголовок (размер кода и маркер версии)
    header = bytes([code_bytes, 1])  # Версия 1
    return header + compressed_data


def decompress_lz78(compressed_data: bytes) -> bytes:
    if len(compressed_data) < 2:
        return b''

    code_bytes, version = compressed_data[:2]
    if version != 1:
        raise ValueError("Unsupported compression version")

    encoded_data = []
    pos = 2
    while pos + code_bytes <= len(compressed_data):
        code = int.from_bytes(compressed_data[pos:pos + code_bytes], 'big')
        pos += code_bytes

        if pos >= len(compressed_data):
            break

        byte = compressed_data[pos]
        pos += 1

        # Обработка маркера 255,255
        if byte == 255 and pos < len(compressed_data) and compressed_data[pos] == 255:
            byte = 256
            pos += 1

        encoded_data.append((code, byte))

    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)

# Функции для работы с файлами
def compress_file_lz78(input_file: str, output_file: str):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = compress_lz78(data)
        f_out.write(compressed_data)

def decompress_file_lz78(input_file: str, output_file: str):
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

    compress_file_lz78(input_data, compress_data)
    print("Сжатие enwik7 с использованием LZ78 завершено.")

    decompress_file_lz78(compress_data, decompress_data)
    print("Распаковка enwik7 завершена.")

    analyze_compression(input_data, compress_data, decompress_data)
    print("Анализ сжатия enwik7 завершен.")
    print("-" * 40)

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_lz78.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_lz78.txt"

    compress_file_lz78(input_data_ru, compress_data_ru)
    print("Сжатие русского текста с использованием LZ78 завершено.")

    decompress_file_lz78(compress_data_ru, decompress_data_ru)
    print("Распаковка русского текста завершена.")

    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Анализ сжатия русского текста завершен.")
    print("-" * 40)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_lz78.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_lz78_decompressed.bin"

    compress_file_lz78(binary_input, binary_compressed)
    print("Сжатие бинарного файла с использованием LZ78 завершено.")

    decompress_file_lz78(binary_compressed, binary_decompressed)
    print("Распаковка бинарного файла завершена.")

    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Анализ сжатия бинарного файла завершен.")
    print("-" * 40)
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"

    # Сжатие RAW-файлов с использованием LZ78
    compress_file_lz78(bw_raw_path, bw_compressed_path)
    compress_file_lz78(gray_raw_path, gray_compressed_path)
    compress_file_lz78(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.raw"

    # Декомпрессия RAW-файлов с использованием LZ78
    decompress_file_lz78(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file_lz78(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file_lz78(color_compressed_path, color_decompressed_raw_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path, bw_decompressed_raw_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path, gray_decompressed_raw_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path, color_decompressed_raw_path)

    print("Все операции завершены.")
    print("Все операции завершены.")
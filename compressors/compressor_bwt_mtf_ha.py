import numpy as np
import time
import math
import os
import queue

# Размер блока (64 КБ)
BLOCK_SIZE = 64 * 1024


# Функции для BWT (остаются без изменений)
def build_suffix_array(data: bytes) -> list[int]:
    n = len(data)
    sa = list(range(n))
    rank = [0] * n
    for i in range(n):
        rank[i] = data[i]
    k = 1
    while k < n:
        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            prev = sa[i - 1]
            curr = sa[i]
            equal = (rank[prev] == rank[curr] and
                     (prev + k < n and curr + k < n and
                      rank[prev + k] == rank[curr + k]))
            new_rank[curr] = new_rank[prev] + (0 if equal else 1)
        rank = new_rank
        k *= 2
    return sa


def bwt_transform(data: bytes) -> tuple[bytes, int]:
    n = len(data)
    suffix_array = build_suffix_array(data)
    transformed_data = bytearray()
    for i in range(n):
        transformed_data.append(data[(suffix_array[i] + n - 1) % n])
    index = suffix_array.index(0)
    return bytes(transformed_data), index


def bwt_inverse(transformed_data: bytes, index: int) -> bytes:
    n = len(transformed_data)
    freq = [0] * 256
    for byte in transformed_data:
        freq[byte] += 1
    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]
    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = transformed_data[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1
    original_data = bytearray()
    i = index
    for _ in range(n):
        original_data.append(transformed_data[i])
        i = lf[i]
    return bytes(original_data[::-1])


# Функции для MTF (остаются без изменений)
def mtf_transform(data: bytes) -> bytes:
    alphabet = list(range(256))
    transformed_data = bytearray()
    for byte in data:
        index = alphabet.index(byte)
        transformed_data.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(transformed_data)


def mtf_inverse(transformed_data: bytes) -> bytes:
    alphabet = list(range(256))
    original_data = bytearray()
    for index in transformed_data:
        byte = alphabet[index]
        original_data.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(original_data)


# Функции для Хаффмана (остаются без изменений)
class Node():
    def __init__(self, symbol=None, counter=None, left=None, right=None, parent=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.counter < other.counter


def count_symb(data: bytes) -> np.ndarray:
    counter = np.zeros(256, dtype=int)
    for byte in data:
        counter[byte] += 1
    return counter


def huffman_compress(data: bytes) -> tuple[bytes, dict]:
    C = count_symb(data)
    list_of_leafs = []
    Q = queue.PriorityQueue()
    for i in range(256):
        if C[i] != 0:
            leaf = Node(symbol=i, counter=C[i])
            list_of_leafs.append(leaf)
            Q.put(leaf)
    while Q.qsize() >= 2:
        left_node = Q.get()
        right_node = Q.get()
        parent_node = Node(left=left_node, right=right_node)
        left_node.parent = parent_node
        right_node.parent = parent_node
        parent_node.counter = left_node.counter + right_node.counter
        Q.put(parent_node)
    codes = {}
    for leaf in list_of_leafs:
        node = leaf
        code = ""
        while node.parent is not None:
            if node.parent.left == node:
                code = "0" + code
            else:
                code = "1" + code
            node = node.parent
        codes[leaf.symbol] = code
    coded_message = ""
    for byte in data:
        coded_message += codes[byte]
    padding = 8 - len(coded_message) % 8
    coded_message += '0' * padding
    coded_message = f"{padding:08b}" + coded_message
    bytes_string = bytearray()
    for i in range(0, len(coded_message), 8):
        byte = coded_message[i:i + 8]
        bytes_string.append(int(byte, 2))
    return bytes(bytes_string), codes


def huffman_decompress(compressed_data: bytes, huffman_codes: dict) -> bytes:
    padding = compressed_data[0]
    coded_message = ""
    for byte in compressed_data[1:]:
        coded_message += f"{byte:08b}"
    if padding > 0:
        coded_message = coded_message[:-padding]
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ""
    decoded_data = bytearray()
    for bit in coded_message:
        current_code += bit
        if current_code in reverse_codes:
            decoded_data.append(reverse_codes[current_code])
            current_code = ""
    return bytes(decoded_data)


def read_huffman_codes(codes_file):
    huffman_codes = {}
    with open(codes_file, 'r') as f:
        for line in f:
            symbol, code = line.strip().split(':')
            huffman_codes[int(symbol)] = code
    return huffman_codes


def write_huffman_codes(huffman_codes, file_path):
    with open(file_path, 'w') as code_file:
        for symbol, code in huffman_codes.items():
            code_file.write(f"{symbol}:{code}\n")


# Новые функции для интеграции с вашим примером использования
def compress_file(input_path: str, output_path: str):
    """Сжимает файл с использованием BWT+MTF+HA"""
    with open(input_path, "rb") as f:
        data = f.read()

    # Применяем BWT
    transformed_data, index = bwt_transform(data)

    # Применяем MTF
    mtf_data = mtf_transform(transformed_data)

    # Применяем Хаффман
    compressed_bytes, huffman_codes = huffman_compress(mtf_data)

    # Сохраняем сжатые данные и дополнительную информацию
    with open(output_path, "wb") as f:
        # Записываем индекс BWT (4 байта)
        f.write(index.to_bytes(4, byteorder='big'))
        # Записываем коды Хаффмана
        codes_bytes = serialize_huffman_codes(huffman_codes)
        f.write(len(codes_bytes).to_bytes(4, byteorder='big'))
        f.write(codes_bytes)
        # Записываем сжатые данные
        f.write(compressed_bytes)


def decompress_file(input_path: str, output_path: str):
    """Распаковывает файл, сжатый с помощью BWT+MTF+HA"""
    with open(input_path, "rb") as f:
        # Читаем индекс BWT
        index = int.from_bytes(f.read(4), byteorder='big')
        # Читаем коды Хаффмана
        codes_length = int.from_bytes(f.read(4), byteorder='big')
        codes_bytes = f.read(codes_length)
        huffman_codes = deserialize_huffman_codes(codes_bytes)
        # Читаем сжатые данные
        compressed_data = f.read()

    # Декодируем Хаффман
    decoded_mtf_data = huffman_decompress(compressed_data, huffman_codes)

    # Декодируем MTF
    decoded_transformed_data = mtf_inverse(decoded_mtf_data)

    # Декодируем BWT
    decompressed_data = bwt_inverse(decoded_transformed_data, index)

    # Сохраняем распакованные данные
    with open(output_path, "wb") as f:
        f.write(decompressed_data)


def serialize_huffman_codes(huffman_codes: dict) -> bytes:
    """Сериализует коды Хаффмана в компактный бинарный формат"""
    codes_bytes = bytearray()
    for symbol, code in huffman_codes.items():
        codes_bytes.extend([symbol, len(code)])
        # Преобразуем строку кода в байты
        code_byte = int(code, 2)
        codes_bytes.append(code_byte)
    return bytes(codes_bytes)


def deserialize_huffman_codes(codes_bytes: bytes) -> dict:
    """Десериализует коды Хаффмана из бинарного формата"""
    huffman_codes = {}
    i = 0
    while i < len(codes_bytes):
        symbol = codes_bytes[i]
        code_length = codes_bytes[i + 1]
        code_byte = codes_bytes[i + 2]
        # Преобразуем байт обратно в строку битов
        code = bin(code_byte)[2:].zfill(code_length)
        huffman_codes[symbol] = code
        i += 3
    return huffman_codes


def analyze_compression(original_path: str, compressed_path: str, decompressed_path: str):
    """Анализирует эффективность сжатия"""
    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)
    decompressed_size = os.path.getsize(decompressed_path)

    print(f"\nАнализ сжатия для файла: {original_path}")
    print(f"Исходный размер: {original_size} байт")
    print(f"Размер после сжатия: {compressed_size} байт")
    print(f"Размер после распаковки: {decompressed_size} байт")

    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    # Проверка целостности данных
    with open(original_path, "rb") as f1, open(decompressed_path, "rb") as f2:
        original_data = f1.read()
        decompressed_data = f2.read()

    if original_data == decompressed_data:
        print("Проверка целостности: данные совпадают")
    else:
        print("Ошибка: данные после распаковки не совпадают с оригиналом")


# Пример использования (адаптированный под ваш пример)
if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_bwt_mtf_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_bwt_mtf_ha.txt"

    print("Сжатие файла enwik7...")
    compress_file(input_data, compress_data)
    print("Распаковка файла enwik7...")
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_bwt_mtf_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_bwt_mtf_ha.txt"

    print("Сжатие русского текста...")
    compress_file(input_data_ru, compress_data_ru)
    print("Распаковка русского текста...")
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_bwt_mtf_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_bwt_mtf_ha.exe"

    print("Сжатие бинарного файла...")
    compress_file(binary_input, binary_compressed)
    print("Распаковка бинарного файла...")
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Обработка изображений
    image_files = [
        ("C:/OPP/compression_project/tests/black_white_image.raw", "test4", "bw"),
        ("C:/OPP/compression_project/tests/gray_image.raw", "test5", "gray"),
        ("C:/OPP/compression_project/tests/color_image.raw", "test6", "color")
    ]

    for img_path, test_num, img_type in image_files:
        compressed_img = f"C:/OPP/compression_project/results/compressed/{test_num}/{img_type}_bwt_mtf_ha.bin"
        decompressed_img = f"C:/OPP/compression_project/results/decompressors/{test_num}/{img_type}_bwt_mtf_ha.raw"

        print(f"Сжатие {img_type} изображения...")
        compress_file(img_path, compressed_img)
        print(f"Распаковка {img_type} изображения...")
        decompress_file(compressed_img, decompressed_img)
        analyze_compression(img_path, compressed_img, decompressed_img)
        print(f"{img_type.capitalize()} изображение обработано.\n")
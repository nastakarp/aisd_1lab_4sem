import numpy as np
import time
import math
import os
import queue

# Размер блока (64 КБ)
BLOCK_SIZE = 64 * 1024

# Функции для BWT
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

# Функции для MTF
def mtf_transform(data: bytes) -> bytes:
    alphabet = list(range(256))
    transformed_data = bytearray()
    for byte in data:
        index = alphabet.index(byte)
        transformed_data.append(index)
        # Перемещаем символ в начало алфавита
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(transformed_data)

def mtf_inverse(transformed_data: bytes) -> bytes:
    alphabet = list(range(256))
    original_data = bytearray()
    for index in transformed_data:
        byte = alphabet[index]
        original_data.append(byte)
        # Перемещаем символ в начало алфавита
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(original_data)

# Функции для RLE
def rle_compress(data: bytes) -> bytes:
    compressed_data = bytearray()
    n = len(data)
    i = 0
    while i < n:
        current_byte = data[i]
        count = 1
        while i + count < n and count < 255 and data[i + count] == current_byte:
            count += 1
        compressed_data.append(count)
        compressed_data.append(current_byte)
        i += count
    return bytes(compressed_data)

def rle_decompress(compressed_data: bytes) -> bytes:
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0
    while i < n:
        count = compressed_data[i]
        byte = compressed_data[i + 1]
        decompressed_data.extend([byte] * count)
        i += 2
    return bytes(decompressed_data)

# Функции для Хаффмана
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

# Общие функции
def calculate_entropy(data: bytes) -> float:
    counter = count_symb(data)
    total_symbols = len(data)
    entropy = 0.0
    for count in counter:
        if count > 0:
            probability = count / total_symbols
            entropy -= probability * math.log2(probability)
    return entropy

def calculate_average_code_length(huffman_codes: dict, data: bytes) -> float:
    counter = count_symb(data)
    total_symbols = len(data)
    total_length = 0.0
    for symbol, code in huffman_codes.items():
        probability = counter[symbol] / total_symbols
        total_length += probability * len(code)
    return total_length

def process_file(file_path, output_compressed, output_decompressed):
    start_time = time.time()
    with open(file_path, "rb") as f:
        data = f.read()
    original_size = len(data)
    print(f"Исходный размер данных: {original_size} байт")

    # Применяем BWT
    transformed_data, index = bwt_transform(data)
    # Применяем MTF
    mtf_data = mtf_transform(transformed_data)
    # Применяем RLE
    rle_data = rle_compress(mtf_data)
    # Применяем Хаффман
    compressed_bytes, huffman_codes = huffman_compress(rle_data)

    # Записываем сжатые данные и коды Хаффмана
    compressed_size = len(compressed_bytes)
    print(f"Размер сжатых данных: {compressed_size} байт")
    with open(output_compressed, "wb") as file:
        file.write(compressed_bytes)
    with open(output_compressed + '_codes', 'w') as code_file:
        for symbol, code in huffman_codes.items():
            code_file.write(f"{symbol}:{code}\n")

    # Декомпрессия
    with open(output_compressed, "rb") as f:
        compressed_data = f.read()
    huffman_codes = read_huffman_codes(output_compressed + '_codes')
    # Декодируем Хаффман
    decoded_rle_data = huffman_decompress(compressed_data, huffman_codes)
    # Декодируем RLE
    decoded_mtf_data = rle_decompress(decoded_rle_data)
    # Декодируем MTF
    decoded_transformed_data = mtf_inverse(decoded_mtf_data)
    # Декодируем BWT
    decompressed_data = bwt_inverse(decoded_transformed_data, index)

    # Записываем декомпрессированные данные
    decompressed_size = len(decompressed_data)
    print(f"Размер после декомпрессии: {decompressed_size} байт")
    with open(output_decompressed, "wb") as file:
        file.write(decompressed_data)

    # Вычисляем коэффициент сжатия и энтропию
    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    entropy = calculate_entropy(data)
    print(f"Энтропия: {entropy:.2f} бит/символ")
    avg_code_length = calculate_average_code_length(huffman_codes, rle_data)
    print(f"Средняя длина кода: {avg_code_length:.2f} бит/символ")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения: {elapsed_time:.2f} секунд \n")

# Список файлов для обработки
file_paths = [
    "C:/OPP/compression_project/tests/test1_enwik7",
    "C:/OPP/compression_project/tests/test2_rus.txt",
    "C:/OPP/compression_project/tests/test3_bin.exe"
]

# Обработка каждого файла
for i, file_path in enumerate(file_paths):
    output_compressed = f"compressed_file_BWT+RLE+MTF+HA_{i+1}.bin"
    output_decompressed = f"decompressed_file_BWT+RLE+MTF+HA_{i+1}.txt"
    print(f"Обработка файла {file_path}...")
    process_file(file_path, output_compressed, output_decompressed)


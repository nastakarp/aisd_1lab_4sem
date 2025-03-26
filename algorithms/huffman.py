import heapq
from collections import Counter

import pickle

class Node:
    def __init__(self, symbol=None, counter=None, left=None, right=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.counter < other.counter


def count_symb(data: bytes) -> dict:
    """
    Подсчитывает частоту символов в данных.
    :param data: Входные данные (байтовая строка).
    :return: Словарь с частотами символов.
    """
    return Counter(data)


def build_huffman_tree(frequency: dict) -> Node:
    """
    Строит дерево Хаффмана на основе частот символов.
    :param frequency: Словарь с частотами символов.
    :return: Корень дерева Хаффмана.
    """
    heap = []
    for symbol, weight in frequency.items():
        heapq.heappush(heap, Node(symbol=symbol, counter=weight))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(counter=left.counter + right.counter, left=left, right=right)
        heapq.heappush(heap, parent)

    return heapq.heappop(heap)


def generate_codes(node: Node, code: str = "", codes: dict = None) -> dict:
    """
    Генерирует коды Хаффмана для каждого символа.
    :param node: Текущий узел дерева.
    :param code: Текущий код.
    :param codes: Словарь для хранения кодов.
    :return: Словарь с кодами Хаффмана.
    """
    if codes is None:
        codes = {}
    if node.symbol is not None:
        codes[node.symbol] = code
    else:
        generate_codes(node.left, code + "0", codes)
        generate_codes(node.right, code + "1", codes)
    return codes

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

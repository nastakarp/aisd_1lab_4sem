#huffman
import heapq
from collections import defaultdict, Counter
import pickle


def huffman_encode(data: bytes) -> bytes:
    """
    Кодирование Хаффмана с сохранением таблицы кодов.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    frequency = Counter(data)
    heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = "0" + pair[1]
        for pair in hi[1:]:
            pair[1] = "1" + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    huffman_codes = dict(heapq.heappop(heap)[1:])
    encoded_bits = "".join([huffman_codes[byte] for byte in data])
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += "0" * padding
    encoded_bytes = bytes([int(encoded_bits[i:i+8], 2) for i in range(0, len(encoded_bits), 8)])

    # Сохраняем таблицу кодов и padding в сжатых данных
    metadata = {
        "codes": huffman_codes,
        "padding": padding,
    }
    metadata_bytes = pickle.dumps(metadata)
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


def huffman_decode(encoded_data: bytes) -> bytes:
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
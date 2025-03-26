import os
import time
import heapq
import pickle
from collections import Counter
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Node:
    def __init__(self, symbol=None, counter=None, left=None, right=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.counter < other.counter


def build_suffix_array(data: bytes) -> list[int]:
    """Строит суффиксный массив с использованием алгоритма Manber-Myers."""
    n = len(data)
    sa = list(range(n))
    rank = [data[i] for i in range(n)]
    k = 1

    while k < n:
        # Сортируем суффиксы по текущему и следующему символу
        sa.sort(key=lambda i: (rank[i], rank[i + k]) if i + k < n else (rank[i],))

        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            # Сравниваем текущий и предыдущий суффиксы
            curr = sa[i]
            prev = sa[i - 1]
            same_as_prev = (rank[curr] == rank[prev] and
                            ((curr + k < n and prev + k < n and rank[curr + k] == rank[prev + k]) or
                             (curr + k >= n and prev + k >= n)))

            new_rank[curr] = new_rank[prev] + (0 if same_as_prev else 1)
        rank = new_rank

        if rank[sa[-1]] == n - 1:
            break
        k *= 2
    return sa


def bwt_transform(data: bytes) -> tuple[bytes, int]:
    """Применяет преобразование Барроуза-Уилера к данным."""
    if not data:
        return b'', 0

    n = len(data)
    sa = build_suffix_array(data)

    # Создаем преобразованные данные
    transformed = bytearray()
    for i in range(n):
        transformed.append(data[(sa[i] + n - 1) % n])

    index = sa.index(0)
    return bytes(transformed), index


def bwt_inverse(transformed: bytes, index: int) -> bytes:
    """Обратное преобразование Барроуза-Уилера."""
    if not transformed:
        return b''

    n = len(transformed)

    # Подсчет частот символов
    freq = [0] * 256
    for byte in transformed:
        freq[byte] += 1

    # Вычисление стартовых позиций
    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]

    # Построение LF-маппинга
    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = transformed[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1

    # Восстановление оригинальных данных
    original = bytearray()
    i = index
    for _ in range(n):
        original.append(transformed[i])
        i = lf[i]

    return bytes(original[::-1])


def rle_compress(data: bytes) -> bytes:
    """RLE сжатие с обработкой длинных последовательностей."""
    compressed = bytearray()
    n = len(data)
    i = 0

    while i < n:
        current = data[i]
        count = 1
        max_count = min(255, n - i)

        while count < max_count and data[i + count] == current:
            count += 1

        compressed.append(count)
        compressed.append(current)
        i += count

    return bytes(compressed)


def rle_decompress(compressed: bytes) -> bytes:
    """RLE распаковка."""
    decompressed = bytearray()
    n = len(compressed)

    for i in range(0, n, 2):
        if i + 1 >= n:
            break
        count = compressed[i]
        byte = compressed[i + 1]
        decompressed.extend([byte] * count)

    return bytes(decompressed)


def mtf_transform(data: bytes) -> bytes:
    """Move-To-Front преобразование."""
    alphabet = list(range(256))
    transformed = bytearray()

    for byte in data:
        index = alphabet.index(byte)
        transformed.append(index)
        # Перемещаем символ в начало
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(transformed)


def mtf_inverse(transformed: bytes) -> bytes:
    """Обратное Move-To-Front преобразование."""
    alphabet = list(range(256))
    original = bytearray()

    for index in transformed:
        byte = alphabet[index]
        original.append(byte)
        # Восстанавливаем алфавит
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(original)


def build_huffman_tree(freq: dict) -> Node:
    """Строит дерево Хаффмана."""
    heap = []
    for symbol, count in freq.items():
        heapq.heappush(heap, Node(symbol=symbol, counter=count))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(counter=left.counter + right.counter, left=left, right=right)
        heapq.heappush(heap, parent)

    return heapq.heappop(heap)


def generate_huffman_codes(node: Node, code: str = "", codes: dict = None) -> dict:
    """Генерирует коды Хаффмана."""
    if codes is None:
        codes = {}

    if node.symbol is not None:
        codes[node.symbol] = code
    else:
        generate_huffman_codes(node.left, code + "0", codes)
        generate_huffman_codes(node.right, code + "1", codes)

    return codes


def huffman_compress(data: bytes) -> bytes:
    """Huffman сжатие."""
    if not data:
        return b''

    # Подсчет частот
    freq = Counter(data)

    # Построение дерева
    tree = build_huffman_tree(freq)

    # Генерация кодов
    codes = generate_huffman_codes(tree)

    # Кодирование данных
    encoded_bits = ''.join([codes[byte] for byte in data])

    # Добавление padding
    padding = (8 - len(encoded_bits) % 8) % 8
    encoded_bits += '0' * padding

    # Преобразование в байты
    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte = encoded_bits[i:i + 8]
        encoded_bytes.append(int(byte, 2))

    # Подготовка метаданных
    metadata = {
        'codes': codes,
        'padding': padding,
        'freq': freq
    }
    metadata_bytes = pickle.dumps(metadata)

    # Формат: [4 байта - длина метаданных][метаданные][закодированные данные]
    return len(metadata_bytes).to_bytes(4, 'big') + metadata_bytes + encoded_bytes


def huffman_decompress(compressed: bytes) -> bytes:
    """Huffman распаковка."""
    if not compressed:
        return b''

    # Извлечение метаданных
    metadata_length = int.from_bytes(compressed[:4], 'big')
    metadata = pickle.loads(compressed[4:4 + metadata_length])
    encoded_data = compressed[4 + metadata_length:]

    # Восстановление дерева
    tree = build_huffman_tree(metadata['freq'])

    # Преобразование байтов в биты
    bits = []
    for byte in encoded_data:
        bits.append(f"{byte:08b}")
    bits = ''.join(bits)

    # Удаление padding
    if metadata['padding'] > 0:
        bits = bits[:-metadata['padding']]

    # Декодирование
    current_node = tree
    decoded = bytearray()

    for bit in bits:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.symbol is not None:
            decoded.append(current_node.symbol)
            current_node = tree

    return bytes(decoded)


class BWT_RLE_MTF_Huffman:
    @staticmethod
    def compress(data: bytes, chunk_size: int = 1024 * 1024) -> bytes:
        """Сжатие с чанкованием."""
        if not data:
            return b''

        compressed_chunks = []
        total_size = len(data)
        processed = 0

        print("Compressing...")
        while processed < total_size:
            chunk = data[processed:processed + chunk_size]
            processed += len(chunk)

            # BWT
            bwt_data, index = bwt_transform(chunk)

            # RLE
            rle_data = rle_compress(bwt_data)

            # MTF
            mtf_data = mtf_transform(rle_data)

            # Huffman
            huffman_data = huffman_compress(mtf_data)

            # Сохраняем индекс BWT и сжатые данные
            compressed_chunk = index.to_bytes(4, 'big') + huffman_data
            compressed_chunks.append(compressed_chunk)

            print(f"Processed {processed}/{total_size} bytes ({processed / total_size:.1%})")

        # Объединяем все чанки
        return len(compressed_chunks).to_bytes(4, 'big') + b''.join(compressed_chunks)

    @staticmethod
    def decompress(compressed: bytes) -> bytes:
        """Распаковка с чанкованием."""
        if not compressed:
            return b''

        # Извлекаем количество чанков
        num_chunks = int.from_bytes(compressed[:4], 'big')
        offset = 4
        decompressed_chunks = []

        print("Decompressing...")
        for chunk_num in range(num_chunks):
            # Извлекаем индекс BWT
            index = int.from_bytes(compressed[offset:offset + 4], 'big')
            offset += 4

            # Находим конец Huffman данных
            if chunk_num < num_chunks - 1:
                next_chunk_offset = offset + int.from_bytes(compressed[offset:offset + 4], 'big')
                huffman_data = compressed[offset:next_chunk_offset]
                offset = next_chunk_offset
            else:
                huffman_data = compressed[offset:]

            # Huffman
            mtf_data = huffman_decompress(huffman_data)

            # MTF
            rle_data = mtf_inverse(mtf_data)

            # RLE
            bwt_data = rle_decompress(rle_data)

            # BWT
            chunk_data = bwt_inverse(bwt_data, index)

            decompressed_chunks.append(chunk_data)
            print(f"Decompressed chunk {chunk_num + 1}/{num_chunks}")

        return b''.join(decompressed_chunks)


def process_file(input_path: str, compressed_path: str, decompressed_path: str):
    """Обрабатывает файл полностью."""
    try:
        # Чтение исходного файла
        logger.info(f"Reading file: {input_path}")
        with open(input_path, 'rb') as f:
            original_data = f.read()
        original_size = len(original_data)
        logger.info(f"Original size: {original_size} bytes")

        # Сжатие
        logger.info("Compressing...")
        start_time = time.time()
        compressed_data = BWT_RLE_MTF_Huffman.compress(original_data)
        compression_time = time.time() - start_time

        compressed_size = len(compressed_data)
        logger.info(f"Compressed size: {compressed_size} bytes")
        logger.info(f"Compression ratio: {compressed_size / original_size:.2f}")
        logger.info(f"Compression time: {compression_time:.2f} sec")

        # Сохранение сжатых данных
        with open(compressed_path, 'wb') as f:
            f.write(compressed_data)
        logger.info(f"Compressed data saved to: {compressed_path}")

        # Распаковка
        logger.info("Decompressing...")
        start_time = time.time()
        decompressed_data = BWT_RLE_MTF_Huffman.decompress(compressed_data)
        decompression_time = time.time() - start_time
        logger.info(f"Decompression time: {decompression_time:.2f} sec")

        # Проверка целостности
        if original_data == decompressed_data:
            logger.info("Data integrity check: SUCCESS")
        else:
            logger.error("Data integrity check: FAILED")
            # Находим первое несовпадение
            min_len = min(len(original_data), len(decompressed_data))
            for i in range(min_len):
                if original_data[i] != decompressed_data[i]:
                    logger.error(f"First mismatch at position {i}: "
                                 f"original={original_data[i]}, decompressed={decompressed_data[i]}")
                    break
            if len(original_data) != len(decompressed_data):
                logger.error(f"Length mismatch: original={len(original_data)}, "
                             f"decompressed={len(decompressed_data)}")
            return

        # Сохранение распакованных данных
        with open(decompressed_path, 'wb') as f:
            f.write(decompressed_data)
        logger.info(f"Decompressed data saved to: {decompressed_path}")

    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Пути к файлам
    input_file = "C:/OPP/compression_project/tests/test1_enwik7"
    compressed_file = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_BWT_RLE_MTF_Ha.bin"
    decompressed_file = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_BWT_RLE_MTF_Ha.txt"

    # Создаем директории, если их нет
    os.makedirs(os.path.dirname(compressed_file), exist_ok=True)
    os.makedirs(os.path.dirname(decompressed_file), exist_ok=True)

    # Обработка файла
    process_file(input_file, compressed_file, decompressed_file)
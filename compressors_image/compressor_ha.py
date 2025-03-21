import heapq
from collections import defaultdict, Counter
import pickle
from PIL import Image
import numpy as np
import os
import math


# Класс для узла дерева Хаффмана
class Node:
    def __init__(self, symbol=None, frequency=0, left=None, right=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


# Подсчет частот символов
def count_symb(data: bytes) -> dict:
    frequency = defaultdict(int)
    for byte in data:
        frequency[byte] += 1
    return frequency


# Построение дерева Хаффмана
def build_huffman_tree(frequency: dict) -> Node:
    heap = []
    for symbol, freq in frequency.items():
        heapq.heappush(heap, Node(symbol=symbol, frequency=freq))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(frequency=left.frequency + right.frequency, left=left, right=right)
        heapq.heappush(heap, parent)

    return heapq.heappop(heap)


# Генерация кодов Хаффмана
def generate_codes(node: Node, code: str = "", codes: dict = None) -> dict:
    if codes is None:
        codes = {}

    if node.symbol is not None:
        codes[node.symbol] = code
    else:
        generate_codes(node.left, code + "0", codes)
        generate_codes(node.right, code + "1", codes)

    return codes


# Кодирование данных с использованием алгоритма Хаффмана
def huffman_compress(data: bytes) -> bytes:
    frequency = count_symb(data)
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = generate_codes(huffman_tree)

    encoded_bits = "".join(huffman_codes[byte] for byte in data)
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += "0" * padding
    encoded_bytes = bytes(int(encoded_bits[i:i + 8], 2) for i in range(0, len(encoded_bits), 8))

    # Сохраняем таблицу кодов и padding
    metadata = {
        "codes": huffman_codes,
        "padding": padding,
    }
    metadata_bytes = pickle.dumps(metadata)
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


# Декодирование данных с использованием алгоритма Хаффмана
def huffman_decompress(encoded_data: bytes) -> bytes:
    metadata_length = int.from_bytes(encoded_data[:4], "big")
    metadata_bytes = encoded_data[4:4 + metadata_length]
    encoded_bytes = encoded_data[4 + metadata_length:]

    metadata = pickle.loads(metadata_bytes)
    huffman_codes = metadata["codes"]
    padding = metadata["padding"]

    encoded_bits = "".join(f"{byte:08b}" for byte in encoded_bytes)
    encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits

    reverse_codes = {v: k for k, v in huffman_codes.items()}

    current_bits = ""
    decoded_data = []
    for bit in encoded_bits:
        current_bits += bit
        if current_bits in reverse_codes:
            decoded_data.append(reverse_codes[current_bits])
            current_bits = ""

    return bytes(decoded_data)


# Расчет энтропии
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


# Расчет коэффициента сжатия
def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    return original_size / compressed_size if compressed_size != 0 else 0


# Анализ файла (размер и энтропия)
def analyze_file(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    file_size = len(data)
    entropy = calculate_entropy(data)
    return file_size, entropy


# Сжатие изображения
def compress_image(input_image_path: str, output_compressed_path: str):
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_compressed_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Открываем изображение
    image = Image.open(input_image_path)
    image_data = np.array(image)

    # Получаем размеры изображения
    height, width = image_data.shape[:2]

    # Преобразуем данные изображения в байты
    if image.mode == "1":  # Черно-белое изображение
        data = image_data.tobytes()
    elif image.mode == "L":  # Серое изображение
        data = image_data.tobytes()
    elif image.mode == "RGB":  # Цветное изображение
        # Разделяем на каналы R, G, B
        r, g, b = image_data[:, :, 0], image_data[:, :, 1], image_data[:, :, 2]
        data = {
            "r": r.tobytes(),
            "g": g.tobytes(),
            "b": b.tobytes(),
        }
    else:
        raise ValueError("Неподдерживаемый формат изображения")

    # Сжимаем данные
    if isinstance(data, dict):  # Цветное изображение
        compressed_data = {
            "r": huffman_compress(data["r"]),
            "g": huffman_compress(data["g"]),
            "b": huffman_compress(data["b"]),
            "height": height,
            "width": width,
        }
    else:  # Черно-белое или серое изображение
        compressed_data = {
            "data": huffman_compress(data),
            "height": height,
            "width": width,
        }

    # Сохраняем сжатые данные
    with open(output_compressed_path, "wb") as f:
        pickle.dump(compressed_data, f)


# Декомпрессия изображения
def decompress_image(input_compressed_path: str, output_image_path: str):
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_image_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Загружаем сжатые данные
    with open(input_compressed_path, "rb") as f:
        compressed_data = pickle.load(f)

    # Извлекаем высоту и ширину
    height = compressed_data["height"]
    width = compressed_data["width"]

    # Распаковываем данные
    if "r" in compressed_data:  # Цветное изображение
        r = huffman_decompress(compressed_data["r"])
        g = huffman_decompress(compressed_data["g"])
        b = huffman_decompress(compressed_data["b"])
        # Преобразуем байты обратно в массив numpy
        r = np.frombuffer(r, dtype=np.uint8).reshape((height, width))
        g = np.frombuffer(g, dtype=np.uint8).reshape((height, width))
        b = np.frombuffer(b, dtype=np.uint8).reshape((height, width))
        # Объединяем каналы
        image_data = np.stack((r, g, b), axis=-1)
    else:  # Черно-белое или серое изображение
        data = huffman_decompress(compressed_data["data"])
        image_data = np.frombuffer(data, dtype=np.uint8).reshape((height, width))

    # Создаем изображение из данных
    image = Image.fromarray(image_data)

    # Сохраняем изображение
    image.save(output_image_path)


# Пример использования
if __name__ == "__main__":
    # Обработка черно-белого изображения
    bw_input = "C:/OPP/compression_project/tests/black_white_image.png"
    bw_compressed = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    bw_decompressed = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.png"

    # Сжатие и декомпрессия
    compress_image(bw_input, bw_compressed)
    decompress_image(bw_compressed, bw_decompressed)

    # Анализ сжатия
    original_size, original_entropy = analyze_file(bw_input)
    compressed_size, compressed_entropy = analyze_file(bw_compressed)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print("Черно-белое изображение:")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)

    # Обработка серого изображения
    gray_input = "C:/OPP/compression_project/tests/gray_image.png"
    gray_compressed = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    gray_decompressed = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.png"

    # Сжатие и декомпрессия
    compress_image(gray_input, gray_compressed)
    decompress_image(gray_compressed, gray_decompressed)

    # Анализ сжатия
    original_size, original_entropy = analyze_file(gray_input)
    compressed_size, compressed_entropy = analyze_file(gray_compressed)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print("Серое изображение:")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)

    # Обработка цветного изображения
    color_input = "C:/OPP/compression_project/tests/color_image.png"
    color_compressed = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"
    color_decompressed = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.png"

    # Сжатие и декомпрессия
    compress_image(color_input, color_compressed)
    decompress_image(color_compressed, color_decompressed)

    # Анализ сжатия
    original_size, original_entropy = analyze_file(color_input)
    compressed_size, compressed_entropy = analyze_file(color_compressed)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print("Цветное изображение:")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)
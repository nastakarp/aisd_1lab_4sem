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


# Преобразование изображения в RAW
def convert_image_to_raw(input_image_path: str, output_raw_path: str):
    """
    Преобразует изображение в формат RAW и сохраняет его размеры.
    :param input_image_path: Путь к исходному изображению.
    :param output_raw_path: Путь для сохранения RAW-файла.
    """
    # Открываем изображение
    image = Image.open(input_image_path)
    width, height = image.size

    # Преобразуем изображение в массив NumPy
    image_data = np.array(image)

    # Сохраняем данные в RAW-файл
    with open(output_raw_path, "wb") as f:
        # Сохраняем размеры изображения (4 байта на ширину и 4 байта на высоту)
        f.write(width.to_bytes(4, "big"))
        f.write(height.to_bytes(4, "big"))
        f.write(image_data.tobytes())

    print(f"Изображение {input_image_path} преобразовано в RAW: {output_raw_path}")


# Сжатие RAW-файла
def convert_raw_to_image(input_raw_path: str, output_image_path: str, image_mode: str):
    """
    Преобразует RAW-файл обратно в изображение.
    :param input_raw_path: Путь к RAW-файлу.
    :param output_image_path: Путь для сохранения изображения.
    :param image_mode: Режим изображения ("1", "L", "RGB").
    """
    # Чтение RAW-файла
    with open(input_raw_path, "rb") as f:
        # Читаем размеры изображения (первые 8 байт)
        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
        raw_data = f.read()

    # Преобразование данных в массив NumPy
    image_data = np.frombuffer(raw_data, dtype=np.uint8)

    # Преобразование массива в изображение
    if image_mode == "RGB":
        image_data = image_data.reshape((height, width, 3))
    elif image_mode == "1":
        # Для режима "1" каждый байт содержит 8 пикселей
        image_data = np.unpackbits(image_data).reshape((height, width))
    else:
        image_data = image_data.reshape((height, width))

    image = Image.fromarray(image_data, mode=image_mode)
    image.save(output_image_path)

    print(f"RAW-файл {input_raw_path} преобразован в изображение: {output_image_path}")


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


# Преобразование RAW обратно в изображение
def convert_raw_to_image(input_raw_path: str, output_image_path: str, image_mode: str):
    """
    Преобразует RAW-файл обратно в изображение.
    :param input_raw_path: Путь к RAW-файлу.
    :param output_image_path: Путь для сохранения изображения.
    :param image_mode: Режим изображения ("1", "L", "RGB").
    """
    # Чтение RAW-файла
    with open(input_raw_path, "rb") as f:
        # Читаем размеры изображения (первые 8 байт)
        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
        raw_data = f.read()

    # Преобразование данных в массив NumPy
    image_data = np.frombuffer(raw_data, dtype=np.uint8)

    # Преобразование массива в изображение
    if image_mode == "RGB":
        image_data = image_data.reshape((height, width, 3))
    elif image_mode == "1":
        # Для режима "1" каждый байт содержит 8 пикселей
        # Распаковываем биты и изменяем форму массива
        image_data = np.unpackbits(image_data)
        # Убедимся, что количество пикселей соответствует width * height
        expected_pixels = width * height
        if len(image_data) > expected_pixels:
            image_data = image_data[:expected_pixels]  # Обрезаем лишние данные
        image_data = image_data.reshape((height, width))
    else:
        image_data = image_data.reshape((height, width))

    image = Image.fromarray(image_data, mode=image_mode)
    image.save(output_image_path)

    print(f"RAW-файл {input_raw_path} преобразован в изображение: {output_image_path}")


# Анализ сжатия
def analyze_compression(input_raw_path: str, compressed_path: str):
    """
    Анализирует сжатие: рассчитывает коэффициент сжатия и энтропию.
    :param input_raw_path: Путь к исходному RAW-файлу.
    :param compressed_path: Путь к сжатому файлу.
    """
    # Чтение исходного RAW-файла
    with open(input_raw_path, "rb") as f:
        raw_data = f.read()

    # Чтение сжатого файла
    with open(compressed_path, "rb") as f:
        compressed_data = f.read()

    # Расчет коэффициента сжатия
    original_size = len(raw_data)
    compressed_size = len(compressed_data)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    # Расчет энтропии
    original_entropy = calculate_entropy(raw_data)
    compressed_entropy = calculate_entropy(compressed_data)

    # Вывод результатов
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)

def calculate_image_size(raw_data_size: int, image_mode: str) -> tuple:
    """
    Рассчитывает размеры изображения на основе размера RAW-файла и режима изображения.
    :param raw_data_size: Размер RAW-файла в байтах.
    :param image_mode: Режим изображения ("1", "L", "RGB").
    :return: Кортеж (ширина, высота).
    """
    if image_mode == "1":  # Черно-белое изображение (1 бит на пиксель)
        total_pixels = raw_data_size * 8  # 1 байт = 8 пикселей
    elif image_mode == "L":  # Серое изображение (1 байт на пиксель)
        total_pixels = raw_data_size
    elif image_mode == "RGB":  # Цветное изображение (3 байта на пиксель)
        total_pixels = raw_data_size // 3
    else:
        raise ValueError("Неподдерживаемый режим изображения")

    # Предполагаем, что изображение квадратное
    side = int(math.sqrt(total_pixels))
    return (side, side)

# Определение функции compress_raw_file
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

# Основная функция
if __name__ == "__main__":
    # Пути к изображениям
    bw_image_path = "C:/OPP/compression_project/tests/black_white_image.png"
    gray_image_path = "C:/OPP/compression_project/tests/gray_image.png"
    color_image_path = "C:/OPP/compression_project/tests/color_image.png"

    # Пути для сохранения RAW-файлов
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Преобразование изображений в RAW
    convert_image_to_raw(bw_image_path, bw_raw_path)
    convert_image_to_raw(gray_image_path, gray_raw_path)
    convert_image_to_raw(color_image_path, color_raw_path)

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"

    # Сжатие RAW-файлов
    compress_raw_file(bw_raw_path, bw_compressed_path)
    compress_raw_file(gray_raw_path, gray_compressed_path)
    compress_raw_file(color_raw_path, color_compressed_path)

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

    # Декомпрессия RAW-файлов
    decompress_raw_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_raw_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_raw_file(color_compressed_path, color_decompressed_raw_path)

    # Преобразование RAW обратно в изображения
    convert_raw_to_image(bw_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.png", "1")
    convert_raw_to_image(gray_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.png", "L")
    convert_raw_to_image(color_decompressed_raw_path, "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.png", "RGB")

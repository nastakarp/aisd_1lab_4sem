import os
import math
from collections import Counter
from typing import Tuple

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Рассчитывает коэффициент сжатия."""
    return original_size / compressed_size if compressed_size > 0 else 0.0


def calculate_entropy(data: bytes) -> float:
    """Рассчитывает энтропию файла."""
    if not data:
        return 0.0

    frequency = Counter(data)
    total_symbols = len(data)
    entropy = 0.0

    for count in frequency.values():
        probability = count / total_symbols
        entropy -= probability * math.log2(probability)

    return entropy


def analyze_file(file_path: str) -> Tuple[int, float]:
    """Анализирует файл: размер и энтропию."""
    with open(file_path, "rb") as f:
        data = f.read()
    return len(data), calculate_entropy(data)


def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """Анализирует результаты сжатия."""
    original_size, original_entropy = analyze_file(input_file)
    compressed_size, compressed_entropy = analyze_file(compressed_file)
    decompressed_size, _ = analyze_file(decompressed_file)

    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Размер декомпрессированного файла: {decompressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.3f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)


def rle_compress(data: bytes) -> bytes:
    """Сжимает данные с использованием RLE."""
    compressed_data = bytearray()
    n = len(data)
    i = 0

    while i < n:
        current_byte = data[i]
        count = 1

        while i + count < n and count < 255 and data[i + count] == current_byte:
            count += 1

        if count > 1:
            compressed_data.append(count)
            compressed_data.append(current_byte)
            i += count
        else:
            non_repeating = bytearray()
            while i < n and (i + 1 >= n or data[i] != data[i + 1]):
                non_repeating.append(data[i])
                i += 1
                if len(non_repeating) == 255:
                    break
            compressed_data.append(0)
            compressed_data.append(len(non_repeating))
            compressed_data.extend(non_repeating)

    return bytes(compressed_data)


def rle_decompress(compressed_data: bytes) -> bytes:
    """Декомпрессия RLE."""
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0

    while i < n:
        flag = compressed_data[i]
        if flag == 0:
            length = compressed_data[i + 1]
            decompressed_data.extend(compressed_data[i + 2:i + 2 + length])
            i += 2 + length
        else:
            count = flag
            byte = compressed_data[i + 1]
            decompressed_data.extend([byte] * count)
            i += 2

    return bytes(decompressed_data)


def compress_file(input_file: str, output_file: str):
    """Сжимает файл с использованием RLE."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, "rb") as f:
        data = f.read()
    with open(output_file, "wb") as f:
        f.write(rle_compress(data))


def decompress_file(input_file: str, output_file: str):
    """Распаковывает RLE-сжатый файл."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, "rb") as f:
        compressed_data = f.read()
    with open(output_file, "wb") as f:
        f.write(rle_decompress(compressed_data))


if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_rle.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_rle.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)

    # Обработка русского текста
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_rle.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_rle.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_rle.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_rle_decompressed.bin"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)

    # Черно-белое изображение
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    bw_compressed = "C:/OPP/compression_project/results/compressed/test4/bw_image_rle.bin"
    bw_decompressed = "C:/OPP/compression_project/results/decompressors/test4/bw_image_rle_decompressed.raw"

    compress_file(bw_raw_path, bw_compressed)
    decompress_file(bw_compressed, bw_decompressed)
    analyze_compression(bw_raw_path, bw_compressed, bw_decompressed)

    # Серое изображение
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    gray_compressed = "C:/OPP/compression_project/results/compressed/test5/gray_image_rle.bin"
    gray_decompressed = "C:/OPP/compression_project/results/decompressors/test5/gray_image_rle_decompressed.raw"

    compress_file(gray_raw_path, gray_compressed)
    decompress_file(gray_compressed, gray_decompressed)
    analyze_compression(gray_raw_path, gray_compressed, gray_decompressed)

    # Цветное изображение
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"
    color_compressed = "C:/OPP/compression_project/results/compressed/test6/color_image_rle.bin"
    color_decompressed = "C:/OPP/compression_project/results/decompressors/test6/color_image_rle_decompressed.raw"

    compress_file(color_raw_path, color_compressed)
    decompress_file(color_compressed, color_decompressed)
    analyze_compression(color_raw_path, color_compressed, color_decompressed)


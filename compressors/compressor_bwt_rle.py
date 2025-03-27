import time
import math
import os

# Размер блока (64 КБ)
BLOCK_SIZE = 64 * 1024


def build_suffix_array(data: bytes) -> list[int]:
    """Строит суффиксный массив с использованием алгоритма Manber-Myers."""
    n = len(data)
    sa = list(range(n))
    rank = [data[i] for i in range(n)]
    k = 1
    while k < n:
        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            prev, curr = sa[i - 1], sa[i]
            equal = (rank[prev] == rank[curr] and
                     (prev + k < n and curr + k < n and
                      rank[prev + k] == rank[curr + k]))
            new_rank[curr] = new_rank[prev] + (0 if equal else 1)
        rank = new_rank
        k *= 2
    return sa


# Функции для BWT
def bwt_transform(data: bytes, chunk_size: int = 1024) -> tuple[bytes, list[int]]:
    transformed_data = bytearray()
    indices = []
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]
        index, encoded_chunk = transform_chunk(chunk)
        transformed_data.extend(encoded_chunk)
        indices.append(index)
    return bytes(transformed_data), indices


def transform_chunk(chunk: bytes) -> tuple[int, bytes]:
    rotations = [chunk[i:] + chunk[:i] for i in range(len(chunk))]
    rotations.sort()
    original_index = rotations.index(chunk)
    encoded_chunk = bytes(rotation[-1] for rotation in rotations)
    return original_index, encoded_chunk


def bwt_inverse(transformed_data: bytes, indices: list[int], chunk_size: int = 1024) -> bytes:
    restored_data = bytearray()
    position = 0
    index = 0
    while position < len(transformed_data):
        end = position + chunk_size if position + chunk_size <= len(transformed_data) else len(transformed_data)
        chunk = transformed_data[position:end]
        original_index = indices[index]
        restored_chunk = reverse_transform_chunk(original_index, chunk)
        restored_data.extend(restored_chunk)
        position = end
        index += 1
    return bytes(restored_data)


def reverse_transform_chunk(original_index: int, encoded_chunk: bytes) -> bytes:
    table = [(char, idx) for idx, char in enumerate(encoded_chunk)]
    table.sort()
    result = bytearray()
    current_row = original_index
    for _ in range(len(encoded_chunk)):
        char, current_row = table[current_row]
        result.append(char)
    return bytes(result)


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
        compressed_data.append(count)
        compressed_data.append(current_byte)
        i += count
    return bytes(compressed_data)


def rle_decompress(compressed_data: bytes) -> bytes:
    """Декомпрессия данных, сжатых с использованием RLE."""
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0
    while i < n:
        count = compressed_data[i]
        byte = compressed_data[i + 1]
        decompressed_data.extend([byte] * count)
        i += 2
    return bytes(decompressed_data)


def compress_file(input_path: str, output_path: str):
    """Сжимает файл с использованием BWT+RLE."""
    start_time = time.time()

    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        block_number = 0
        while True:
            block = f_in.read(BLOCK_SIZE)
            if not block:
                break
            transformed_data, indices = bwt_transform(block)
            # Store all indices for the block
            f_out.write(len(indices).to_bytes(4, 'big'))  # Write number of indices first
            for index in indices:
                f_out.write(index.to_bytes(4, 'big'))  # Write each index
            compressed_data = rle_compress(transformed_data)
            f_out.write(len(compressed_data).to_bytes(4, 'big'))
            f_out.write(compressed_data)
            block_number += 1

    print(f"Файл {input_path} успешно сжат в {output_path}")
    print(f"Время сжатия: {time.time() - start_time:.2f} секунд")


def decompress_file(input_path: str, output_path: str):
    """Декомпрессия файла, сжатого с использованием BWT+RLE."""
    start_time = time.time()

    blocks = {}
    with open(input_path, "rb") as f_in:
        block_number = 0
        while True:
            # Read number of indices
            num_indices_bytes = f_in.read(4)
            if not num_indices_bytes:
                break

            num_indices = int.from_bytes(num_indices_bytes, 'big')
            indices = []
            for _ in range(num_indices):
                index = int.from_bytes(f_in.read(4), 'big')
                indices.append(index)

            block_size = int.from_bytes(f_in.read(4), 'big')
            compressed_block = f_in.read(block_size)

            decompressed_transformed = rle_decompress(compressed_block)
            decompressed_data = bwt_inverse(decompressed_transformed, indices)
            blocks[block_number] = decompressed_data
            block_number += 1

    with open(output_path, "wb") as f_out:
        for block_number in sorted(blocks.keys()):
            f_out.write(blocks[block_number])

    print(f"Файл {input_path} успешно распакован в {output_path}")
    print(f"Время декомпрессии: {time.time() - start_time:.2f} секунд")


def analyze_compression(original_path: str, compressed_path: str, decompressed_path: str):
    """Анализирует эффективность сжатия."""
    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)
    decompressed_size = os.path.getsize(decompressed_path)

    print("\nАнализ сжатия:")
    print(f"Исходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Размер после распаковки: {decompressed_size} байт")

    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    if original_size == decompressed_size:
        print("Проверка целостности: данные совпадают")
    else:
        print("Проверка целостности: ОШИБКА - данные не совпадают")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_bwt_rle.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_bwt_rle.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)

    # Обработка русского текста
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_bwt_rle.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_bwt_rle.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_bwt_rle.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_bwt_rle_decompressed.bin"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)

    # Черно-белое изображение
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    bw_compressed = "C:/OPP/compression_project/results/compressed/test4/bw_image_bwt_rle.bin"
    bw_decompressed = "C:/OPP/compression_project/results/decompressors/test4/bw_image_bwt_rle_decompressed.raw"

    compress_file(bw_raw_path, bw_compressed)
    decompress_file(bw_compressed, bw_decompressed)
    analyze_compression(bw_raw_path, bw_compressed, bw_decompressed)

    # Серое изображение
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    gray_compressed = "C:/OPP/compression_project/results/compressed/test5/gray_image_bwt_rle.bin"
    gray_decompressed = "C:/OPP/compression_project/results/decompressors/test5/gray_image_bwt_rle_decompressed.raw"

    compress_file(gray_raw_path, gray_compressed)
    decompress_file(gray_compressed, gray_decompressed)
    analyze_compression(gray_raw_path, gray_compressed, gray_decompressed)

    # Цветное изображение
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"
    color_compressed = "C:/OPP/compression_project/results/compressed/test6/color_image_bwt_rle.bin"
    color_decompressed = "C:/OPP/compression_project/results/decompressors/test6/color_image_bwt_rle_decompressed.raw"

    compress_file(color_raw_path, color_compressed)
    decompress_file(color_compressed, color_decompressed)
    analyze_compression(color_raw_path, color_compressed, color_decompressed)
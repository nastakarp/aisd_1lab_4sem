from algorithms.bwt import bwt_transform, bwt_inverse
from algorithms.rle import rle_compress, rle_decompress
from file_analysis import analyze_compression

# Размер блока (64 КБ)
BLOCK_SIZE = 64 * 1024


def compress_file(input_path: str, output_path: str):
    """Сжимает файл с использованием BWT+RLE."""
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


def decompress_file(input_path: str, output_path: str):
    """Декомпрессия файла, сжатого с использованием BWT+RLE."""

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


if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_bwt_rle.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_bwt_rle.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/c_rus_bwt_rle.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/d_rus_bwt_rle.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/c_binary_bwt_rle.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/d_binary_bwt_rle.exe"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Пути к исходным RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_bwt_rle_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_bwt_rle_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_bwt_rle_compressed.bin"

    # Сжатие RAW-файлов
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_bwt_rle_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_bwt_rle_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_bwt_rle_decompressed.raw"

    # Декомпрессия RAW-файлов
    decompress_file(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file(color_compressed_path, color_decompressed_raw_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path, bw_decompressed_raw_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path, gray_decompressed_raw_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path, color_decompressed_raw_path)

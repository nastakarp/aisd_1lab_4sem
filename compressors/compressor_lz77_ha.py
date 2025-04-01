import os
from compressor_lz77 import lz77_encode, lz77_decode
from compressor_ha import huffman_compress, huffman_decompress
from file_analysis import analyze_compression


def lz77_huffman_compress(data: bytes, buffer_size: int = 8192) -> bytes:
    """
    Сжимает данные с использованием LZ77 и Хаффмана.
    :param data: Исходные данные (байтовая строка).
    :param buffer_size: Размер буфера для LZ77.
    :return: Сжатые данные (байтовая строка).
    """
    # Шаг 1: LZ77
    lz77_compressed = lz77_encode(data, buffer_size)

    # Шаг 2: Huffman
    huffman_compressed = huffman_compress(lz77_compressed)

    return huffman_compressed

def lz77_huffman_decompress(compressed_data: bytes) -> bytes:
    """
    Распаковывает данные, сжатые с использованием LZ77 и Хаффмана.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Huffman
    huffman_decompressed = huffman_decompress(compressed_data)

    # Шаг 2: LZ77
    lz77_decompressed = lz77_decode(huffman_decompressed)

    return lz77_decompressed

def compress_file(input_file: str, output_file: str, buffer_size: int = 512):
    """
    Сжимает файл с использованием LZ77 и Хаффмана.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к сжатому файлу.
    :param buffer_size: Размер буфера для LZ77.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = lz77_huffman_compress(data, buffer_size)
        f_out.write(compressed_data)

def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый с использованием LZ77 и Хаффмана.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к распакованному файлу.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()
        decompressed_data = lz77_huffman_decompress(compressed_data)
        f_out.write(decompressed_data)


# Пример использования
if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz77_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz77_ha.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/c_rus_lz77_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/d_rus_lz77_ha.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/c_binary_lz77_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/d_binary_lz77_ha.exe"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Пути к исходным RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_lz77_ha_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_lz77_ha_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_lz77_ha_compressed.bin"

    # Сжатие RAW-файлов
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_lz77_ha_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_lz77_ha_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_lz77_ha_decompressed.raw"

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
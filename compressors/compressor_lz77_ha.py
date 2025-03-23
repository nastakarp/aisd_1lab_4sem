import os
from compressor_lz77 import lz77_encode, lz77_decode
from compressor_ha import huffman_compress, huffman_decompress

def lz77_huffman_compress(data: bytes, buffer_size: int = 512) -> bytes:
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

def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие: размеры файлов и коэффициент сжатия.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к распакованному файлу.
    """
    # Размер исходного файла
    original_size = os.path.getsize(input_file)

    # Размер сжатого файла
    compressed_size = os.path.getsize(compressed_file)

    # Размер декомпрессированного файла
    decompressed_size = os.path.getsize(decompressed_file)

    # Коэффициент сжатия
    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

    # Вывод результатов
    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Размер декомпрессированного файла: {decompressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.3f}")
    print("-" * 40)

# Пример использования
if __name__ == "__main__":
    # Обработка файла enwik7 (английский текст)
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz77_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz77_ha.txt"

    compress_file(input_data, compress_data)
    print("Сжатие enwik7 с использованием LZ77 + Хаффмана завершено.")

    decompress_file(compress_data, decompress_data)
    print("Распаковка enwik7 завершена.")

    analyze_compression(input_data, compress_data, decompress_data)
    print("Анализ сжатия enwik7 завершен.")
    print("-" * 40)

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_lz77_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_lz77_ha.txt"

    compress_file(input_data_ru, compress_data_ru)
    print("Сжатие русского текста с использованием LZ77 + Хаффмана завершено.")

    decompress_file(compress_data_ru, decompress_data_ru)
    print("Распаковка русского текста завершена.")

    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Анализ сжатия русского текста завершен.")
    print("-" * 40)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_lz77_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_lz77_ha_decompressed.bin"

    compress_file(binary_input, binary_compressed)
    print("Сжатие бинарного файла с использованием LZ77 + Хаффмана завершено.")

    decompress_file(binary_compressed, binary_decompressed)
    print("Распаковка бинарного файла завершена.")

    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Анализ сжатия бинарного файла завершен.")
    print("-" * 40)

    # Обработка изображений
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_lz77_ha.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_lz77_ha.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_lz77_ha.bin"

    # Сжатие RAW-файлов с использованием LZ77 + Хаффмана
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_lz77_ha_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_lz77_ha_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_lz77_ha_decompressed.raw"

    # Декомпрессия RAW-файлов с использованием LZ77 + Хаффмана
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
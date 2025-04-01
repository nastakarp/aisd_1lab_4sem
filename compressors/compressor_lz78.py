import os
from file_analysis import analyze_compression
from algorithms.lz78 import compress_lz78, decompress_lz78

# Функции для работы с файлами
def compress_file(input_file: str, output_file: str):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = compress_lz78(data)
        f_out.write(compressed_data)

def decompress_file(input_file: str, output_file: str):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()
        decompressed_data = decompress_lz78(compressed_data)
        f_out.write(decompressed_data)

# Основной блок
if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz78.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz78.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/c_rus_lz78.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/d_rus_lz78.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/c_binary_lz78.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/d_binary_lz78.exe"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Пути к исходным RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_lz78_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_lz78_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_lz78_compressed.bin"

    # Сжатие RAW-файлов
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_lz78_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_lz78_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_lz78_decompressed.raw"

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

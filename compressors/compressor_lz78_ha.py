import os
from compressor_ha import huffman_compress, huffman_decompress
from compressor_lz78 import compress_lz78, decompress_lz78

# Функции для анализа сжатия
def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    return original_size / compressed_size

def analyze_file(file_path: str) -> int:
    """
    Возвращает размер файла в байтах.
    """
    return os.path.getsize(file_path)

def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие файла.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к восстановленному файлу.
    """
    # Размер исходного файла
    original_size = analyze_file(input_file)
    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")

    # Размер сжатого файла
    compressed_size = analyze_file(compressed_file)
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    # Размер восстановленного файла
    decompressed_size = analyze_file(decompressed_file)
    print(f"Размер восстановленного файла: {decompressed_size} байт")

    # Проверка совпадения размеров исходного и восстановленного файлов
    if original_size == decompressed_size:
        print("Размеры исходного и восстановленного файлов совпадают.")
    else:
        print("Ошибка: размеры исходного и восстановленного файлов не совпадают.")
    print("-" * 40)

# Комбинированный компрессор LZ78 + Хаффман
def lz78_huffman_compress(data: bytes) -> bytes:
    """
    Сжимает данные с использованием LZ78 и Хаффмана.
    :param data: Исходные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    # Шаг 1: LZ78
    lz78_compressed = compress_lz78(data)

    # Шаг 2: Хаффман
    huffman_compressed = huffman_compress(lz78_compressed)

    return huffman_compressed

def lz78_huffman_decompress(compressed_data: bytes) -> bytes:
    """
    Распаковывает данные, сжатые с использованием LZ78 и Хаффмана.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Хаффман
    huffman_decompressed = huffman_decompress(compressed_data)

    # Шаг 2: LZ78
    lz78_decompressed = decompress_lz78(huffman_decompressed)

    return lz78_decompressed

# Функции для работы с файлами
def compress_file_lz78_huffman(input_file: str, output_file: str):
    """
    Сжимает файл с использованием LZ78 и Хаффмана.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к сжатому файлу.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()
        compressed_data = lz78_huffman_compress(data)
        f_out.write(compressed_data)

def decompress_file_lz78_huffman(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый с использованием LZ78 и Хаффмана.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к распакованному файлу.
    """
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()
        decompressed_data = lz78_huffman_decompress(compressed_data)
        f_out.write(decompressed_data)

# Пример использования
if __name__ == "__main__":
    # Обработка файла enwik7 (английский текст)
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz78_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz78_ha.txt"

    compress_file_lz78_huffman(input_data, compress_data)
    print("Сжатие enwik7 с использованием LZ78 + Хаффмана завершено.")

    decompress_file_lz78_huffman(compress_data, decompress_data)
    print("Распаковка enwik7 завершена.")

    analyze_compression(input_data, compress_data, decompress_data)
    print("Анализ сжатия enwik7 завершен.")
    print("-" * 40)

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_lz78_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_lz78_ha.txt"

    compress_file_lz78_huffman(input_data_ru, compress_data_ru)
    print("Сжатие русского текста с использованием LZ78 + Хаффмана завершено.")

    decompress_file_lz78_huffman(compress_data_ru, decompress_data_ru)
    print("Распаковка русского текста завершена.")

    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Анализ сжатия русского текста завершен.")
    print("-" * 40)

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_lz78_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_lz78_ha_decompressed.bin"

    compress_file_lz78_huffman(binary_input, binary_compressed)
    print("Сжатие бинарного файла с использованием LZ78 + Хаффмана завершено.")

    decompress_file_lz78_huffman(binary_compressed, binary_decompressed)
    print("Распаковка бинарного файла завершена.")

    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Анализ сжатия бинарного файла завершен.")
    print("-" * 40)

    # Обработка изображений
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_lz78_ha.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_lz78_ha.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_lz78_ha.bin"

    # Сжатие RAW-файлов с использованием LZ78 + Хаффмана
    compress_file_lz78_huffman(bw_raw_path, bw_compressed_path)
    compress_file_lz78_huffman(gray_raw_path, gray_compressed_path)
    compress_file_lz78_huffman(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_lz78_ha_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_lz78_ha_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_lz78_ha_decompressed.raw"

    # Декомпрессия RAW-файлов с использованием LZ78 + Хаффмана
    decompress_file_lz78_huffman(bw_compressed_path, bw_decompressed_raw_path)
    decompress_file_lz78_huffman(gray_compressed_path, gray_decompressed_raw_path)
    decompress_file_lz78_huffman(color_compressed_path, color_decompressed_raw_path)

    # Анализ сжатия
    print("Черно-белое изображение:")
    analyze_compression(bw_raw_path, bw_compressed_path, bw_decompressed_raw_path)

    print("Серое изображение:")
    analyze_compression(gray_raw_path, gray_compressed_path, gray_decompressed_raw_path)

    print("Цветное изображение:")
    analyze_compression(color_raw_path, color_compressed_path, color_decompressed_raw_path)
from algorithms.huffman import huffman_compress, huffman_decompress
from algorithms.bwt import bwt_inverse, bwt_transform
from algorithms.mtf import mtf_inverse, mtf_transform
from file_analysis import analyze_compression


def compress_file(input_path: str, output_path: str):
    """Сжимает файл с использованием BWT+MTF+HA"""
    with open(input_path, "rb") as f:
        data = f.read()

    # Применяем BWT (новая версия с чанками)
    transformed_data, indices = bwt_transform(data)

    # Применяем MTF
    mtf_data = mtf_transform(transformed_data)

    # Применяем Хаффман
    compressed_bytes = huffman_compress(mtf_data)

    # Сохраняем сжатые данные и дополнительную информацию
    with open(output_path, "wb") as f:
        # Записываем количество индексов (4 байта)
        f.write(len(indices).to_bytes(4, byteorder='big'))
        # Записываем все индексы
        for index in indices:
            f.write(index.to_bytes(4, byteorder='big'))
        # Записываем сжатые данные
        f.write(compressed_bytes)


def decompress_file(input_path: str, output_path: str):
    """Распаковывает файл, сжатый с помощью BWT+MTF+HA"""
    with open(input_path, "rb") as f:
        # Читаем количество индексов
        num_indices = int.from_bytes(f.read(4), byteorder='big')
        # Читаем все индексы
        indices = [int.from_bytes(f.read(4), byteorder='big') for _ in range(num_indices)]
        # Читаем сжатые данные
        compressed_data = f.read()

    # Декодируем Хаффман
    decoded_mtf_data = huffman_decompress(compressed_data)

    # Декодируем MTF
    decoded_transformed_data = mtf_inverse(decoded_mtf_data)

    # Декодируем BWT (новая версия с чанками)
    decompressed_data = bwt_inverse(decoded_transformed_data, indices)

    # Сохраняем распакованные данные
    with open(output_path, "wb") as f:
        f.write(decompressed_data)


if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_bwt_mtf_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_bwt_mtf_ha.txt"

    compress_file(input_data, compress_data)
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/c_rus_bwt_mtf_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/d_rus_bwt_mtf_ha.txt"

    compress_file(input_data_ru, compress_data_ru)
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/c_binary_bwt_mtf_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/d_binary_bwt_mtf_ha.exe"

    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Пути к исходным RAW-файлам
    bw_raw_path = "C:/OPP/compression_project/tests/black_white_image.raw"
    gray_raw_path = "C:/OPP/compression_project/tests/gray_image.raw"
    color_raw_path = "C:/OPP/compression_project/tests/color_image.raw"

    # Пути для сохранения сжатых файлов
    bw_compressed_path = "C:/OPP/compression_project/results/compressed/test4/bw_image_bwt_mtf_ha_compressed.bin"
    gray_compressed_path = "C:/OPP/compression_project/results/compressed/test5/gray_image_bwt_mtf_ha_compressed.bin"
    color_compressed_path = "C:/OPP/compression_project/results/compressed/test6/color_image_bwt_mtf_ha_compressed.bin"

    # Сжатие RAW-файлов
    compress_file(bw_raw_path, bw_compressed_path)
    compress_file(gray_raw_path, gray_compressed_path)
    compress_file(color_raw_path, color_compressed_path)

    # Пути для восстановленных RAW-файлов
    bw_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test4/bw_image_bwt_mtf_ha_decompressed.raw"
    gray_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test5/gray_image_bwt_mtf_ha_decompressed.raw"
    color_decompressed_raw_path = "C:/OPP/compression_project/results/decompressors/test6/color_image_bwt_mtf_ha_decompressed.raw"

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
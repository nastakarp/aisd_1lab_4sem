# compressor_rle
import os
from algorithms.rle import rle_encode, rle_decode
from utils.entropy_calculator import calculate_entropy
from utils.plotter import plot_compression_ratios


def compress_rle(data: bytes) -> bytes:
    """
    Компрессор: RLE.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    # Вычисляем энтропию исходных данных
    original_entropy = calculate_entropy(data)
    print(f"Энтропия исходных данных: {original_entropy:.4f} бит")

    # Применяем RLE для сжатия данных
    compressed_data = rle_encode(data)

    # Вычисляем энтропию сжатых данных
    compressed_entropy = calculate_entropy(compressed_data)
    print(f"Энтропия сжатых данных: {compressed_entropy:.4f} бит")

    return compressed_data


def decompress_rle(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: RLE.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    return rle_decode(compressed_data)


def analyze_compression(input_data: bytes, output_file: str = None):
    """
    Анализ сжатия: сжатие, декомпрессия и построение графиков.
    :param input_data: Входные данные (байтовая строка).
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    # Сжатие данных
    compressed = compress_rle(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия данных
    decompressed = decompress_rle(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"

    # Вычисление коэффициента сжатия
    original_size = len(input_data)
    compressed_size = len(compressed)
    compression_ratio = compressed_size / original_size
    print(f"Коэффициент сжатия: {compression_ratio:.4f}")

    # Построение графика коэффициента сжатия
    compressors = ["RLE"]
    compression_ratios = [compression_ratio]

    # Создание директории для сохранения графиков, если она не существует
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    plot_compression_ratios(compressors, compression_ratios, output_file=output_file)


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"aaabbbddd"

    # Анализ сжатия
    analyze_compression(input_data, output_file="C:/OPP/compression_project/results/graphs/rle_compression_ratio.png")
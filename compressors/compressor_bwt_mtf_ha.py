# compressor_bwt_mtf_ha
import os
from algorithms.bwt import bwt_transform, bwt_inverse
from algorithms.mtf import mtf_encode, mtf_decode
from algorithms.huffman import huffman_encode, huffman_decode
from utils.entropy_calculator import calculate_entropy
from utils.plotter import plot_compression_ratios


def compress_bwt_mtf_ha(data: bytes) -> bytes:
    """
    Компрессор: BWT + MTF + HA.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    # Вычисляем энтропию исходных данных
    original_entropy = calculate_entropy(data)
    print(f"Энтропия исходных данных: {original_entropy:.4f} бит")

    # Шаг 1: Применяем BWT
    transformed_data = bwt_transform(data.decode("utf-8"))  # BWT работает с строками
    transformed_data = transformed_data.encode("utf-8")  # Преобразуем обратно в байты

    # Шаг 2: Применяем MTF
    mtf_encoded_data = mtf_encode(transformed_data)

    # Шаг 3: Применяем Huffman Coding
    compressed_data = huffman_encode(mtf_encoded_data)

    # Вычисляем энтропию сжатых данных
    compressed_entropy = calculate_entropy(compressed_data)
    print(f"Энтропия сжатых данных: {compressed_entropy:.4f} бит")

    return compressed_data


def decompress_bwt_mtf_ha(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: BWT + MTF + HA.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Декодируем Huffman
    mtf_encoded_data = huffman_decode(compressed_data)

    # Шаг 2: Декодируем MTF
    transformed_data = mtf_decode(mtf_encoded_data)

    # Шаг 3: Обратное преобразование BWT
    original_data = bwt_inverse(transformed_data.decode("utf-8"))  # BWT работает с строками
    original_data = original_data.encode("utf-8")  # Преобразуем обратно в байты

    return original_data


def analyze_compression(input_data: bytes, output_file: str = None):
    """
    Анализ сжатия: сжатие, декомпрессия и построение графиков.
    :param input_data: Входные данные (байтовая строка).
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    # Сжатие данных
    compressed = compress_bwt_mtf_ha(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия данных
    decompressed = decompress_bwt_mtf_ha(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"

    # Вычисление коэффициента сжатия
    original_size = len(input_data)
    compressed_size = len(compressed)
    compression_ratio = compressed_size / original_size
    print(f"Коэффициент сжатия: {compression_ratio:.4f}")

    # Построение графика коэффициента сжатия
    compressors = ["BWT + MTF + HA"]
    compression_ratios = [compression_ratio]

    # Создание директории для сохранения графиков, если она не существует
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    plot_compression_ratios(compressors, compression_ratios, output_file=output_file)


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"banana"*10

    # Анализ сжатия
    analyze_compression(input_data, output_file="C:/OPP/compression_project/results/graphs/bwt_mtf_ha_compression_ratio.png")
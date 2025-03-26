import os
from algorithms.bwt import bwt_transform, bwt_inverse
from algorithms.mtf import mtf_encode, mtf_decode
from algorithms.huffman import huffman_encode, huffman_decode
from algorithms.rle import rle_encode, rle_decode
from algorithms.lz77 import lz77_encode, lz77_decode
from algorithms.lz78 import LZ78Encoder, LZ78Decoder
from utils.entropy_calculator import calculate_entropy
from utils.plotter_lz77 import plot_compression_ratios, plot_entropy_vs_block_size, plot_compression_ratio_vs_buffer_size, plot_compression_ratios_comparison
from tabulate import tabulate
# Таблица для хранения данных о компрессии
compression_data = []


def add_compression_data(table: list, compressor_name: str, test_data: str, original_size: int, compressed_size: int, decompressed_size: int, original_entropy: float, compressed_entropy: float, buffer_size: int = None, block_size: int = None):
    """
    Добавление данных о компрессии в таблицу.
    :param table: Таблица с данными.
    :param compressor_name: Название компрессора.
    :param test_data: Тестовые данные.
    :param original_size: Размер до компрессии (байты).
    :param compressed_size: Размер после компрессии (байты).
    :param decompressed_size: Размер после декомпрессии (байты).
    :param original_entropy: Энтропия исходных данных (бит/символ).
    :param compressed_entropy: Энтропия сжатых данных (бит/символ).
    :param buffer_size: Размер буфера (для LZ77).
    :param block_size: Размер блока (для BWT + MTF).
    """
    compression_ratio = compressed_size / original_size
    table.append({
        "Название компрессора": compressor_name,
        "Тестовые данные": test_data,
        "Размер до компрессии (байты)": original_size,
        "Размер после компрессии (байты)": compressed_size,
        "Размер после декомпрессии (байты)": decompressed_size,
        "Коэффициент сжатия": compression_ratio,
        "Энтропия исходных данных (бит/символ)": original_entropy,
        "Энтропия сжатых данных (бит/символ)": compressed_entropy,
        "Размер буфера (байты)": buffer_size,
        "Размер блока (байты)": block_size
    })

def plot_compression_ratios_from_table(table: list, output_file: str = None):
    """
    Построение графика сравнения коэффициентов сжатия для разных компрессоров на основе таблицы.
    :param table: Таблица с данными.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    compressors = [row["Название компрессора"] for row in table]
    compression_ratios = [row["Коэффициент сжатия"] for row in table]

    plot_compression_ratios(compressors, compression_ratios, output_file=output_file)

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

def compress_ha(data: bytes) -> bytes:
    """
    Компрессор: HA (Huffman Coding).
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    return huffman_encode(data)

def decompress_ha(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: HA (Huffman Coding).
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    return huffman_decode(compressed_data)

def compress_rle(data: bytes) -> bytes:
    """
    Компрессор: RLE (Run-Length Encoding).
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    return rle_encode(data)


def decompress_rle(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: RLE (Run-Length Encoding).
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    return rle_decode(compressed_data)

def compress_bwt_rle(data: bytes) -> bytes:
    """
    Компрессор: BWT + RLE.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    transformed_data = bwt_transform(data.decode("utf-8"))
    transformed_data = transformed_data.encode("utf-8")
    return rle_encode(transformed_data)

def decompress_bwt_rle(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: BWT + RLE.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    transformed_data = rle_decode(compressed_data)
    original_data = bwt_inverse(transformed_data.decode("utf-8"))
    return original_data.encode("utf-8")


def compress_lz77(data: bytes, buffer_size: int) -> bytes:
    """
    Компрессор: LZ77.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера.
    :return: Сжатые данные (байтовая строка).
    """
    return lz77_encode(data, buffer_size)

def decompress_lz77(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: LZ77.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    return lz77_decode(compressed_data)

def compress_lz78(data: bytes) -> bytes:
    """
    Компрессор: LZ78.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    encoder = LZ78Encoder()  # Создаем экземпляр класса
    encoded_data = encoder.encode(data)  # Вызываем метод encode через экземпляр

    # Преобразуем список кортежей в байты
    compressed_data = []
    for code, byte in encoded_data:
        compressed_data.extend([code >> 8, code & 0xFF, byte])
    return bytes(compressed_data)

def decompress_lz78(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: LZ78.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Преобразуем байты в список кортежей
    encoded_data = []
    for i in range(0, len(compressed_data), 3):
        code = (compressed_data[i] << 8) + compressed_data[i + 1]
        byte = compressed_data[i + 2]
        encoded_data.append((code, byte))

    # Декодируем LZ78
    decoder = LZ78Decoder()  # Создаем экземпляр класса
    return decoder.decode(encoded_data)  # Вызываем метод decode через экземпляр

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

def analyze_entropy_vs_block_size(data: bytes, block_sizes: list, output_file: str = None):
    """
    Исследование зависимости энтропии от размера блоков.
    :param data: Входные данные (байтовая строка).
    :param block_sizes: Список размеров блоков.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    entropies = []
    for block_size in block_sizes:
        # Разбиваем данные на блоки
        blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]

        # Вычисляем среднюю энтропию для всех блоков
        total_entropy = 0.0
        for block in blocks:
            total_entropy += calculate_entropy(block)
        average_entropy = total_entropy / len(blocks)
        entropies.append(average_entropy)

    # Построение графика
    plot_entropy_vs_block_size(block_sizes, entropies, output_file=output_file)

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Расчет коэффициента сжатия.
    :param original_size: Размер исходных данных (в байтах).
    :param compressed_size: Размер сжатых данных (в байтах).
    :return: Коэффициент сжатия.
    """
    if original_size == 0:
        return 0.0
    return compressed_size / original_size

def analyze_compression_ratio_vs_buffer_size(data: bytes, buffer_sizes: list, output_file: str = None):
    """
    Исследование зависимости коэффициента сжатия от размера буфера.
    :param data: Входные данные (байтовая строка).
    :param buffer_sizes: Список размеров буферов.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    compression_ratios = []
    for buffer_size in buffer_sizes:
        # Сжатие данных
        compressed_data = compress_lz77(data, buffer_size)

        # Расчет коэффициента сжатия
        original_size = len(data)
        compressed_size = len(compressed_data)
        compression_ratio = calculate_compression_ratio(original_size, compressed_size)
        compression_ratios.append(compression_ratio)

    # Построение графика
    plot_compression_ratio_vs_buffer_size(buffer_sizes, compression_ratios, output_file=output_file)

def compare_compressors(data: bytes, buffer_size: int = 1024, output_file: str = None):
    """
    Сравнение эффективности всех компрессоров.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера для LZ77.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    compressors = [
        ("HA", compress_ha, decompress_ha),
        ("RLE", compress_rle, decompress_rle),
        ("BWT + RLE", compress_bwt_rle, decompress_bwt_rle),
        ("BWT + MTF + HA", compress_bwt_mtf_ha, decompress_bwt_mtf_ha),
        ("LZ77", lambda d: compress_lz77(d, buffer_size), decompress_lz77),  # Передаем buffer_size
        ("LZ77 + HA", lambda d: compress_ha(compress_lz77(d, buffer_size)), lambda d: decompress_lz77(decompress_ha(d))),
        ("LZ78", compress_lz78, decompress_lz78),
        ("LZ78 + HA", lambda d: compress_ha(compress_lz78(d)), lambda d: decompress_lz78(decompress_ha(d))),
    ]

    for name, compress, decompress in compressors:
        compressed_data = compress(data)
        decompressed_data = decompress(compressed_data)
        assert data == decompressed_data, f"Декомпрессия не удалась для {name}!"

        # Добавляем данные в таблицу
        add_compression_data(
            compression_data,
            compressor_name=name,
            test_data="enwik7",  # Пример тестовых данных
            original_size=len(data),
            compressed_size=len(compressed_data),
            decompressed_size=len(decompressed_data)
        )

    # Построение графика на основе таблицы
    plot_compression_ratios_from_table(compression_data, output_file=output_file)

def save_table_to_file(table: list, filename: str = "compression_results.txt"):
    """
    Сохранение таблицы с данными о компрессии в текстовый файл.
    :param table: Таблица с данными.
    :param filename: Имя файла для сохранения.
    """
    # Форматируем таблицу
    formatted_table = tabulate(
        table,
        headers="keys",  # Используем ключи словаря как заголовки
        tablefmt="grid",  # Формат таблицы (grid, plain, simple, etc.)
        floatfmt=".4f"   # Формат чисел с плавающей точкой
    )

    # Записываем таблицу в файл
    with open(filename, "w", encoding="utf-8") as file:
        file.write(formatted_table)

    print(f"Таблица сохранена в файл: {filename}")

# Пример использования
# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    test_data_name = "banana_x1000"  # Название тестовых данных

    # Размеры буферов для LZ77
    buffer_sizes = [64, 128, 256, 512, 1024]

    # Вычисляем энтропию исходных данных
    original_entropy = calculate_entropy(input_data)

    # Сравнение коэффициентов сжатия для всех компрессоров
    compressors = [
        ("HA", compress_ha, decompress_ha),
        ("RLE", compress_rle, decompress_rle),
        ("BWT + RLE", compress_bwt_rle, decompress_bwt_rle),
        ("BWT + MTF + HA", compress_bwt_mtf_ha, decompress_bwt_mtf_ha),
        ("LZ78", compress_lz78, decompress_lz78),
    ]

    # Добавляем данные для компрессоров без буфера
    for name, compress, decompress in compressors:
        compressed_data = compress(input_data)
        decompressed_data = decompress(compressed_data)

        # Вычисляем энтропию сжатых данных
        compressed_entropy = calculate_entropy(compressed_data)

        # Добавляем данные в таблицу
        add_compression_data(
            compression_data,
            compressor_name=name,
            test_data=test_data_name,
            original_size=len(input_data),
            compressed_size=len(compressed_data),
            decompressed_size=len(decompressed_data),
            original_entropy=original_entropy,
            compressed_entropy=compressed_entropy
        )

    # Добавляем данные для LZ77 с разными размерами буфера
    for buffer_size in buffer_sizes:
        compressed_data = compress_lz77(input_data, buffer_size)
        decompressed_data = decompress_lz77(compressed_data)

        # Вычисляем энтропию сжатых данных
        compressed_entropy = calculate_entropy(compressed_data)

        # Добавляем данные в таблицу
        add_compression_data(
            compression_data,
            compressor_name="LZ77",
            test_data=test_data_name,
            original_size=len(input_data),
            compressed_size=len(compressed_data),
            decompressed_size=len(decompressed_data),
            original_entropy=original_entropy,
            compressed_entropy=compressed_entropy,
            buffer_size=buffer_size
        )

    # Сохранение таблицы в файл
    save_table_to_file(compression_data, filename="C:/OPP/compression_project/results/compression_results.txt")

    # Построение графиков
    plot_compression_ratios_comparison(compression_data, output_file="C:/OPP/compression_project/results/compression_ratios_comparison.png")
    plot_compression_ratio_vs_buffer_size(compression_data, output_file="C:/OPP/compression_project/results/compression_ratio_vs_buffer_size.png")
    plot_entropy_vs_block_size(compression_data, output_file="C:/OPP/compression_project/results/entropy_vs_block_size.png")




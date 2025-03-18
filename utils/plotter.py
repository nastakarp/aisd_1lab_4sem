import matplotlib.pyplot as plt
from algorithms.rle import rle_encode, rle_decode
from algorithms.huffman import huffman_encode, huffman_decode
from algorithms.lz77 import lz77_encode, lz77_decode
from utils.entropy_calculator import calculate_entropy

def plot_entropy_vs_block_size(block_sizes: list, entropy_values: list, output_file: str = None):
    """
    Построение графика зависимости энтропии от размера блоков.
    :param block_sizes: Список размеров блоков (в символах).
    :param entropy_values: Список значений энтропии для каждого размера блока (в битах на символ).
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(block_sizes, entropy_values, marker='o', linestyle='-', color='b')
    plt.title("Зависимость энтропии от размера блоков")
    plt.xlabel("Размер блока (символы)")
    plt.ylabel("Энтропия (бит/символ)")
    plt.grid(True)

    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def plot_compression_ratio_vs_buffer_size(buffer_sizes: list, compression_ratios: list, output_file: str = None):
    """
    Построение графика зависимости коэффициента сжатия от размера буфера.
    :param buffer_sizes: Список размеров буферов.
    :param compression_ratios: Список коэффициентов сжатия.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(buffer_sizes, compression_ratios, marker='o', linestyle='-', color='b')
    plt.title("Зависимость коэффициента сжатия от размера буфера")
    plt.xlabel("Размер буфера (байты)")
    plt.ylabel("Коэффициент сжатия")
    plt.grid(True)

    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def plot_compression_ratios(compressors: list, compression_ratios: list, output_file: str = None):
    """
    Построение графика сравнения коэффициентов сжатия для разных компрессоров.
    :param compressors: Список названий компрессоров.
    :param compression_ratios: Список коэффициентов сжатия для каждого компрессора.
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    """
    plt.figure(figsize=(10, 6))

    # Построение ломаной линии с точками
    plt.plot(compressors, compression_ratios, marker='o', linestyle='-', color='b', label="Коэффициент сжатия")

    # Настройка графика
    plt.title("Сравнение коэффициентов сжатия для разных компрессоров")
    plt.xlabel("Компрессор")
    plt.ylabel("Коэффициент сжатия")
    plt.grid(True)
    plt.legend()  # Добавляем легенду

    # Сохранение или отображение графика
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def analyze_compression(input_data: bytes, output_file: str = None, buffer_size: int = 1024):
    """
    Анализ сжатия: сжатие, декомпрессия и построение графиков.
    :param input_data: Входные данные (байтовая строка).
    :param output_file: Путь для сохранения графика (если None, график отображается на экране).
    :param buffer_size: Размер буфера для LZ77.
    """
    # Список компрессоров и соответствующих функций сжатия
    compressors = ["RLE", "Huffman",  "LZ77"]
    compression_functions = [
        rle_encode,
        huffman_encode,
        lambda data: lz77_encode(data, buffer_size)  # Передаем buffer_size в LZ77
    ]
    compression_ratios = []

    for compressor, compress_func in zip(compressors, compression_functions):
        try:
            # Сжатие данных
            compressed = compress_func(input_data)

            # Вычисление коэффициента сжатия
            original_size = len(input_data)
            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size
            compression_ratios.append(compression_ratio)

            print(f"{compressor}: Коэффициент сжатия = {compression_ratio:.4f}")
        except Exception as e:
            print(f"Ошибка при сжатии с использованием {compressor}: {e}")
            compression_ratios.append(None)  # Пропустить этот компрессор

    # Удаляем компрессоры, для которых произошла ошибка
    valid_compressors = []
    valid_ratios = []
    for compressor, ratio in zip(compressors, compression_ratios):
        if ratio is not None:
            valid_compressors.append(compressor)
            valid_ratios.append(ratio)

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(valid_compressors, valid_ratios, marker='o', linestyle='-', color='b', label="Коэффициент сжатия")
    plt.title("Сравнение коэффициентов сжатия для разных компрессоров")
    plt.xlabel("Компрессор")
    plt.ylabel("Коэффициент сжатия")
    plt.grid(True)
    plt.legend()

    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"banana" * 10  # Расширяем строку

    # Анализ сжатия
    analyze_compression(input_data, output_file="compression_ratios.png", buffer_size=1024)

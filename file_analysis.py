
import math
from collections import Counter
def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Рассчитывает коэффициент сжатия.
    :param original_size: Размер исходного файла в байтах.
    :param compressed_size: Размер сжатого файла в байтах.
    :return: Коэффициент сжатия.
    """
    return original_size / compressed_size


def calculate_entropy(data: bytes) -> float:
    """
    Рассчитывает энтропию файла.
    :param data: Данные файла в виде байтовой строки.
    :return: Энтропия файла.
    """
    if not data:
        return 0.0

    # Считаем частоту каждого символа
    frequency = Counter(data)
    total_symbols = len(data)

    # Рассчитываем энтропию
    entropy = 0.0
    for count in frequency.values():
        probability = count / total_symbols
        entropy -= probability * math.log2(probability)

    return entropy


def analyze_file(file_path: str):
    """
    Анализирует файл: рассчитывает его размер и энтропию.
    :param file_path: Путь к файлу.
    :return: Размер файла и его энтропия.
    """
    with open(file_path, "rb") as f:
        data = f.read()
    file_size = len(data)
    entropy = calculate_entropy(data)
    return file_size, entropy


def compare_files(file1: str, file2: str) -> bool:
    """
    Сравнивает два файла побайтово.
    :param file1: Путь к первому файлу.
    :param file2: Путь ко второму файлу.
    :return: True, если файлы идентичны, иначе False.
    """
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        content1 = f1.read()
        content2 = f2.read()

    if len(content1) != len(content2):
        return False

    return content1 == content2


def analyze_compression(input_file: str, compressed_file: str, decompressed_file: str):
    """
    Анализирует сжатие файла: рассчитывает коэффициент сжатия, энтропию и размер декомпрессированного файла.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    :param decompressed_file: Путь к декомпрессированному файлу.
    """
    # Анализируем исходный файл
    original_size, original_entropy = analyze_file(input_file)
    # Анализируем сжатый файл
    compressed_size, compressed_entropy = analyze_file(compressed_file)
    # Анализируем декомпрессированный файл
    decompressed_size, _ = analyze_file(decompressed_file)

    # Рассчитываем коэффициент сжатия
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    # Проверяем идентичность файлов
    files_identical = compare_files(input_file, decompressed_file)

    # Выводим результаты
    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Размер декомпрессированного файла: {decompressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.3f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print(f"Файлы до и после сжатия идентичны: {'Да' if files_identical else 'Нет'}")
    print("-" * 40)
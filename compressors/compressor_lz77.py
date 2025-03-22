import os
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

def analyze_compression(input_file: str, compressed_file: str):
    """
    Анализирует сжатие файла: рассчитывает коэффициент сжатия и энтропию.
    :param input_file: Путь к исходному файлу.
    :param compressed_file: Путь к сжатому файлу.
    """
    original_size, original_entropy = analyze_file(input_file)
    compressed_size, compressed_entropy = analyze_file(compressed_file)

    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    print(f"Файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print(f"Энтропия сжатого файла: {compressed_entropy:.2f} бит/символ")
    print("-" * 40)

import os
from collections import deque
def lz77_encode(data: bytes, buffer_size: int = 512) -> bytes:
    compressed_data = []
    i = 0
    while i < len(data):
        match_offset, match_length = 0, 0
        buffer_start = max(0, i - buffer_size)
        buffer = data[buffer_start:i]

        # Ищем совпадения в буфере
        for offset in range(1, len(buffer) + 1):
            current_length = 0
            while (i + current_length < len(data) and
                   len(buffer) - offset + current_length < len(buffer) and
                   data[i + current_length] == buffer[len(buffer) - offset + current_length]):
                current_length += 1
            if current_length > match_length:
                match_offset, match_length = offset, current_length

        # Ограничиваем match_offset и match_length значением 255
        match_offset = min(match_offset, 255)
        match_length = min(match_length, 255)

        # Получаем следующий символ
        next_char = data[i + match_length] if i + match_length < len(data) else 0

        # Проверяем, что match_offset не превышает длину буфера
        if match_offset > len(buffer):
            match_offset, match_length = 0, 0  # Сбрасываем, если offset некорректен

        # Добавляем тройку (offset, length, next_char) в сжатые данные
        compressed_data.append(match_offset)
        compressed_data.append(match_length)
        compressed_data.append(next_char)

        # Перемещаем указатель
        i += match_length + 1

    return bytes(compressed_data)

def lz77_decode(compressed_data: bytes) -> bytes:
    """
    Декодирование данных, сжатых с использованием алгоритма LZ77.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decompressed_data = []  # Здесь хранятся декодированные данные
    i = 0  # Индекс для прохода по сжатым данным

    # Проходим по сжатым данным блоками по 3 байта (offset, length, next_char)
    while i + 2 < len(compressed_data):
        match_offset = compressed_data[i]  # Смещение назад
        match_length = compressed_data[i + 1]  # Длина совпадения
        next_char = compressed_data[i + 2]  # Следующий символ

        # Если offset и length равны 0, это конец данных
        if match_offset == 0 and match_length == 0:
            break

        # Проверяем, что match_offset не превышает длину decompressed_data
        if match_offset > len(decompressed_data):
            # Если offset больше, чем текущая длина данных, это ошибка
            raise ValueError(
                f"Invalid match_offset: {match_offset} > {len(decompressed_data)}. "
                f"Data may be corrupted or compression algorithm is incorrect."
            )

        # Восстанавливаем данные
        for _ in range(match_length):
            # Копируем символ из уже декодированных данных
            decompressed_data.append(decompressed_data[-match_offset])

        # Добавляем следующий символ
        decompressed_data.append(next_char)

        # Перемещаем указатель на следующую тройку
        i += 3

    return bytes(decompressed_data)

def compress_file(input_file: str, output_file: str, buffer_size: int = 512):
    """
    Сжимает файл с использованием алгоритма LZ77.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    :param buffer_size: Размер буфера для LZ77.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        data = f_in.read()  # Читаем весь файл
        compressed_data = lz77_encode(data, buffer_size)  # Сжимаем целиком
        f_out.write(compressed_data)

def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом LZ77.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
        compressed_data = f_in.read()  # Читаем весь сжатый файл
        decompressed_data = lz77_decode(compressed_data)  # Декодируем целиком
        f_out.write(decompressed_data)  # Записываем восстановленные данные

# Пример использования
if __name__ == "__main__":
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_lz77.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_lz77.txt"

    # Сжимаем файл
    compress_file(input_data, compress_data)
    print("Сжатие завершено.")

    # Распаковываем файл
    decompress_file(compress_data, decompress_data)
    print("Распаковка завершена.")

    # Анализируем сжатие
    analyze_compression(input_data, compress_data)
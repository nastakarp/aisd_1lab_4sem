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

def lz77_encode(data: bytes, buffer_size: int = 512) -> bytes:
    """
    Кодирует данные с использованием алгоритма LZ77.
    :param data: Исходные данные (байтовая строка).
    :param buffer_size: Размер буфера для поиска совпадений.
    :return: Сжатые данные (байтовая строка).
    """
    encoded_data = bytearray()
    i = 0
    n = len(data)

    while i < n:
        max_length = 0
        max_offset = 0

        # Определяем границы поиска
        search_start = max(0, i - buffer_size)
        search_end = i

        # Ищем максимальное совпадение
        for length in range(min(255, n - i), 0, -1):
            substring = data[i:i + length]
            offset = data[search_start:search_end].rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = search_end - search_start - offset
                break

        if max_length > 0:
            # Кодируем offset и length в два байта каждый
            encoded_data.append((max_offset >> 8) & 0xFF)  # Старший байт offset
            encoded_data.append(max_offset & 0xFF)  # Младший байт offset
            encoded_data.append((max_length >> 8) & 0xFF)  # Старший байт length
            encoded_data.append(max_length & 0xFF)  # Младший байт length
            i += max_length
        else:
            # Если совпадений нет, кодируем как символ
            encoded_data.append(0)  # offset = 0 (старший байт)
            encoded_data.append(0)  # offset = 0 (младший байт)
            encoded_data.append(0)  # length = 0 (старший байт)
            encoded_data.append(0)  # length = 0 (младший байт)
            encoded_data.append(data[i])  # символ (1 байт)
            i += 1

    return bytes(encoded_data)

def lz77_decode(encoded_data: bytes) -> bytes:
    """
    Декодирует данные, сжатые с использованием алгоритма LZ77.
    :param encoded_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)

    while i < n:
        # Читаем offset и length (по два байта каждый)
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            # Это символ
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            # Это ссылка
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])

    return bytes(decoded_data)

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
    try:
        # Проверяем, существует ли директория для выходного файла
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_file, "rb") as f_in, open(output_file, "wb") as f_out:
            compressed_data = f_in.read()  # Читаем весь сжатый файл
            decompressed_data = lz77_decode(compressed_data)  # Декодируем
            f_out.write(decompressed_data)  # Записываем восстановленные данные
    except Exception as e:
        print(f"Ошибка при распаковке файла: {e}")

def test_buffer_sizes(input_file: str, output_dir: str, buffer_sizes: list):
    """
    Тестирует сжатие с разными размерами буфера.
    :param input_file: Путь к исходному файлу.
    :param output_dir: Директория для сохранения сжатых файлов.
    :param buffer_sizes: Список размеров буфера для тестирования.
    """
    # Создаем директорию для результатов, если она не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Анализируем исходный файл
    original_size, original_entropy = analyze_file(input_file)
    print(f"Исходный файл: {input_file}")
    print(f"Размер исходного файла: {original_size} байт")
    print(f"Энтропия исходного файла: {original_entropy:.2f} бит/символ")
    print("-" * 40)

    # Тестируем для каждого размера буфера
    results = []
    for buffer_size in buffer_sizes:
        print(f"Тестирование с buffer_size = {buffer_size}...")

        # Генерируем пути для сжатого и распакованного файлов
        compressed_file = os.path.join(output_dir, f"compressed_{buffer_size}.bin")
        decompressed_file = os.path.join(output_dir, f"decompressed_{buffer_size}.bin")

        # Сжимаем файл
        compress_file(input_file, compressed_file, buffer_size=buffer_size)

        # Распаковываем файл
        decompress_file(compressed_file, decompressed_file)

        # Анализируем сжатие
        compressed_size, _ = analyze_file(compressed_file)
        compression_ratio = calculate_compression_ratio(original_size, compressed_size)

        # Проверяем, что распакованный файл совпадает с исходным
        with open(input_file, "rb") as f1, open(decompressed_file, "rb") as f2:
            assert f1.read() == f2.read(), "Ошибка: распакованные данные не совпадают с исходными"

        # Сохраняем результаты
        results.append((buffer_size, compressed_size, compression_ratio))

        # Выводим результаты
        print(f"Размер сжатого файла: {compressed_size} байт")
        print(f"Коэффициент сжатия: {compression_ratio:.3f}")
        print("-" * 40)

    # Выводим итоговую таблицу
    print("\nИтоговые результаты:")
    print("Buffer Size | Compressed Size | Compression Ratio")
    print("-" * 40)
    for buffer_size, compressed_size, compression_ratio in results:
        print(f"{buffer_size:11} | {compressed_size:15} | {compression_ratio:.3f}")

if __name__ == "__main__":
    # Параметры тестирования
    buffer_sizes = [16384]  # Размеры буфера для тестирования
    '''
    # Обработка файла enwik7 (английский текст)
    input_enwik7 = "C:/OPP/compression_project/tests/test1_enwik7"
    output_enwik7 = "C:/OPP/compression_project/results/buffer_size_test/enwik7"
    print("Тестирование файла enwik7 (английский текст):")
    test_buffer_sizes(input_enwik7, output_enwik7, buffer_sizes)
    print("=" * 60)

    # Обработка файла test2 (русский текст)
    input_rus = "C:/OPP/compression_project/tests/test2_rus.txt"
    output_rus = "C:/OPP/compression_project/results/buffer_size_test/rus"
    print("Тестирование файла test2 (русский текст):")
    test_buffer_sizes(input_rus, output_rus, buffer_sizes)
    print("=" * 60)
    '''
    # Обработка бинарного файла
    input_bin = "C:/OPP/compression_project/tests/test3_bin.exe"
    output_bin = "C:/OPP/compression_project/results/buffer_size_test/bin"
    print("Тестирование бинарного файла:")
    test_buffer_sizes(input_bin, output_bin, buffer_sizes)
    print("=" * 60)

    print("Все тесты завершены.")
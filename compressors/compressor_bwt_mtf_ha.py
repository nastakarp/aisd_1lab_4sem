from algorithms.huffman import count_symb, build_huffman_tree, generate_codes
import pickle
import numpy as np
import os

# Размер блока (64 КБ)
BLOCK_SIZE = 64 * 1024


# Новые функции для BWT с обработкой по чанкам
def bwt_transform(data: bytes, chunk_size: int = 1024) -> tuple[bytes, list[int]]:
    """Применяет преобразование Барроуза-Уилера к данным по чанкам."""
    transformed_data = bytearray()
    indices = []
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]
        index, encoded_chunk = transform_chunk(chunk)
        transformed_data.extend(encoded_chunk)
        indices.append(index)
    return bytes(transformed_data), indices


def transform_chunk(chunk: bytes) -> tuple[int, bytes]:
    """Преобразует один чанк данных с помощью BWT."""
    rotations = [chunk[i:] + chunk[:i] for i in range(len(chunk))]
    rotations.sort()
    original_index = rotations.index(chunk)
    encoded_chunk = bytes(rotation[-1] for rotation in rotations)
    return original_index, encoded_chunk


def bwt_inverse(transformed_data: bytes, indices: list[int], chunk_size: int = 1024) -> bytes:
    """Обратное преобразование Барроуза-Уилера для чанков."""
    restored_data = bytearray()
    position = 0
    index = 0
    while position < len(transformed_data):
        end = position + chunk_size if position + chunk_size <= len(transformed_data) else len(transformed_data)
        chunk = transformed_data[position:end]
        original_index = indices[index]
        restored_chunk = reverse_transform_chunk(original_index, chunk)
        restored_data.extend(restored_chunk)
        position = end
        index += 1
    return bytes(restored_data)


def reverse_transform_chunk(original_index: int, encoded_chunk: bytes) -> bytes:
    """Обратное преобразование для одного чанка."""
    table = [(char, idx) for idx, char in enumerate(encoded_chunk)]
    table.sort()
    result = bytearray()
    current_row = original_index
    for _ in range(len(encoded_chunk)):
        char, current_row = table[current_row]
        result.append(char)
    return bytes(result)


# Функции для MTF (остаются без изменений)
def mtf_transform(data: bytes) -> bytes:
    alphabet = list(range(256))
    transformed_data = bytearray()
    for byte in data:
        index = alphabet.index(byte)
        transformed_data.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(transformed_data)


def mtf_inverse(transformed_data: bytes) -> bytes:
    alphabet = list(range(256))
    original_data = bytearray()
    for index in transformed_data:
        byte = alphabet[index]
        original_data.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(original_data)


def huffman_compress(data: bytes) -> bytes:
    """
    Кодирование Хаффмана с сохранением таблицы кодов.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    frequency = count_symb(data)
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = generate_codes(huffman_tree)

    encoded_bits = "".join([huffman_codes[byte] for byte in data])
    padding = 8 - len(encoded_bits) % 8
    if padding != 8:  # Добавляем padding только если он нужен
        encoded_bits += "0" * padding
    encoded_bytes = bytes([int(encoded_bits[i:i + 8], 2) for i in range(0, len(encoded_bits), 8)])

    # Сохраняем таблицу кодов и padding в сжатых данных
    metadata = {
        "codes": huffman_codes,
        "padding": padding,
    }
    metadata_bytes = pickle.dumps(metadata)
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


def huffman_decompress(encoded_data: bytes) -> bytes:
    """
    Декодирование Хаффмана с использованием таблицы кодов.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Извлекаем длину метаданных
    metadata_length = int.from_bytes(encoded_data[:4], "big")
    metadata_bytes = encoded_data[4:4 + metadata_length]
    encoded_bytes = encoded_data[4 + metadata_length:]

    # Восстанавливаем таблицу кодов и padding
    metadata = pickle.loads(metadata_bytes)
    huffman_codes = metadata["codes"]
    padding = metadata["padding"]

    # Преобразуем байты в битовую строку
    encoded_bits = "".join([f"{byte:08b}" for byte in encoded_bytes])
    if padding != 8:  # Удаляем padding только если он был добавлен
        encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits

    # Создаем таблицу для обратного поиска (битовая строка -> символ)
    reverse_codes = {v: k for k, v in huffman_codes.items()}

    # Декодируем битовую строку
    current_bits = ""
    decoded_data = []
    for bit in encoded_bits:
        current_bits += bit
        if current_bits in reverse_codes:
            decoded_data.append(reverse_codes[current_bits])
            current_bits = ""

    return bytes(decoded_data)


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


def analyze_compression(original_path: str, compressed_path: str, decompressed_path: str):
    """Анализирует эффективность сжатия"""
    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)
    decompressed_size = os.path.getsize(decompressed_path)

    print(f"\nАнализ сжатия для файла: {original_path}")
    print(f"Исходный размер: {original_size} байт")
    print(f"Размер после сжатия: {compressed_size} байт")
    print(f"Размер после распаковки: {decompressed_size} байт")

    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    # Проверка целостности данных
    with open(original_path, "rb") as f1, open(decompressed_path, "rb") as f2:
        original_data = f1.read()
        decompressed_data = f2.read()

    if original_data == decompressed_data:
        print("Проверка целостности: данные совпадают")
    else:
        print("Ошибка: данные после распаковки не совпадают с оригиналом")


if __name__ == "__main__":
    # Обработка файла enwik7
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_bwt_mtf_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_bwt_mtf_ha.txt"

    print("Сжатие файла enwik7...")
    compress_file(input_data, compress_data)
    print("Распаковка файла enwik7...")
    decompress_file(compress_data, decompress_data)
    analyze_compression(input_data, compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.\n")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_bwt_mtf_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_bwt_mtf_ha.txt"

    print("Сжатие русского текста...")
    compress_file(input_data_ru, compress_data_ru)
    print("Распаковка русского текста...")
    decompress_file(compress_data_ru, decompress_data_ru)
    analyze_compression(input_data_ru, compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.\n")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_bwt_mtf_ha.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_bwt_mtf_ha.exe"

    print("Сжатие бинарного файла...")
    compress_file(binary_input, binary_compressed)
    print("Распаковка бинарного файла...")
    decompress_file(binary_compressed, binary_decompressed)
    analyze_compression(binary_input, binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.\n")

    # Обработка изображений
    image_files = [
        ("C:/OPP/compression_project/tests/black_white_image.raw", "test4", "bw"),
        ("C:/OPP/compression_project/tests/gray_image.raw", "test5", "gray"),
        ("C:/OPP/compression_project/tests/color_image.raw", "test6", "color")
    ]

    for img_path, test_num, img_type in image_files:
        compressed_img = f"C:/OPP/compression_project/results/compressed/{test_num}/{img_type}_bwt_mtf_ha.bin"
        decompressed_img = f"C:/OPP/compression_project/results/decompressors/{test_num}/{img_type}_bwt_mtf_ha.raw"

        print(f"Сжатие {img_type} изображения...")
        compress_file(img_path, compressed_img)
        print(f"Распаковка {img_type} изображения...")
        decompress_file(compressed_img, decompressed_img)
        analyze_compression(img_path, compressed_img, decompressed_img)
        print(f"{img_type.capitalize()} изображение обработано.\n")
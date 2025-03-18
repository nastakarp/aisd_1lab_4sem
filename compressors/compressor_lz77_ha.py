# compressor_lz77_ha
from algorithms.lz77 import lz77_encode, lz77_decode
from algorithms.huffman import huffman_encode, huffman_decode
from utils.file_utils import read_file, write_file, process_file
from utils.entropy_calculator import calculate_entropy


def compress_lz77_ha(data: bytes, buffer_size: int = 1024) -> bytes:
    """
    Компрессор: LZ77 + HA.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера (по умолчанию 1024 байта).
    :return: Сжатые данные (байтовая строка).
    """
    # Шаг 1: Применяем LZ77
    lz77_encoded = lz77_encode(data, buffer_size)

    # Шаг 2: Применяем Huffman Coding
    compressed_data = huffman_encode(lz77_encoded)

    # Вычисляем энтропию исходных данных
    original_entropy = calculate_entropy(data)
    print(f"Энтропия исходных данных: {original_entropy:.4f} бит")

    # Вычисляем энтропию сжатых данных
    compressed_entropy = calculate_entropy(compressed_data)
    print(f"Энтропия сжатых данных: {compressed_entropy:.4f} бит")

    return compressed_data


def decompress_lz77_ha(compressed_data: bytes, buffer_size: int = 1024) -> bytes:
    """
    Декомпрессор: LZ77 + HA.
    :param compressed_data: Сжатые данные (байтовая строка).
    :param buffer_size: Размер буфера (по умолчанию 1024 байта).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Декодируем Huffman
    lz77_encoded = huffman_decode(compressed_data)

    # Шаг 2: Декодируем LZ77
    original_data = lz77_decode(lz77_encoded, buffer_size)

    return original_data


# Пример использования
if __name__ == "__main__":
    # Пути к файлам
    input_file = "tests/test1_enwik7.txt"  # Входной файл
    output_compressed = "results/compressed/enwik7_compressed.bin"  # Сжатый файл
    output_decompressed = "results/decompressed/enwik7_decompressed.txt"  # Восстановленный файл

    # Обработка файла
    process_file(
        input_file,
        output_compressed,
        output_decompressed,
        compress_lz77_ha,
        decompress_lz77_ha,
        buffer_size=1024
    )

#compressor_lz77
from algorithms.lz77 import lz77_encode, lz77_decode

def compress_lz77(data: bytes, buffer_size: int = 1024) -> bytes:
    """
    Компрессор: LZ77.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера (по умолчанию 1024 байта).
    :return: Сжатые данные (байтовая строка).
    """
    return lz77_encode(data, buffer_size)


def decompress_lz77(compressed_data: bytes, buffer_size: int = 1024) -> bytes:
    """
    Декомпрессор: LZ77.
    :param compressed_data: Сжатые данные (байтовая строка).
    :param buffer_size: Размер буфера (по умолчанию 1024 байта).
    :return: Восстановленные данные (байтовая строка).
    """
    return lz77_decode(compressed_data, buffer_size)


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"abracadabra"

    # Сжатие
    compressed = compress_lz77(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия
    decompressed = decompress_lz77(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"
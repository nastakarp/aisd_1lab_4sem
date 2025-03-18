# compressor_ha
from algorithms.huffman import huffman_encode, huffman_decode


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


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"banana"
    print(f"Исходные данные: {input_data}")
    # Сжатие
    compressed = compress_ha(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия
    decompressed = decompress_ha(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"
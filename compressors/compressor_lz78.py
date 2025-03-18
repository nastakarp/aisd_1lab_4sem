#compressor_lz78
from algorithms.lz78 import LZ78Encoder, LZ78Decoder
def compress_lz78(data: bytes) -> bytes:
    """
    Компрессор: LZ78.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    encoder = LZ78Encoder()
    encoded_data = encoder.encode(data)

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
    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"abracadabra"

    # Сжатие
    compressed = compress_lz78(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия
    decompressed = decompress_lz78(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"
#compressor_lz78_ha
from algorithms.lz78 import LZ78Decoder, LZ78Encoder
from algorithms.huffman import huffman_encode, huffman_decode



def compress_lz78_ha(data: bytes) -> bytes:
    """
    Компрессор: LZ78 + HA.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    # Шаг 1: Применяем LZ78
    lz78_encoder = LZ78Encoder()
    lz78_encoded = lz78_encoder.encode(data)

    # Преобразуем список кортежей в байты
    lz78_bytes = []
    for code, byte in lz78_encoded:
        lz78_bytes.extend([code >> 8, code & 0xFF, byte])
    lz78_bytes = bytes(lz78_bytes)

    # Шаг 2: Применяем Huffman Coding
    compressed_data = huffman_encode(lz78_bytes)

    return compressed_data


def decompress_lz78_ha(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: LZ78 + HA.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Декодируем Huffman
    lz78_bytes = huffman_decode(compressed_data)

    # Преобразуем байты в список кортежей
    lz78_encoded = []
    for i in range(0, len(lz78_bytes), 3):
        code = (lz78_bytes[i] << 8) + lz78_bytes[i + 1]
        byte = lz78_bytes[i + 2]
        lz78_encoded.append((code, byte))

    # Шаг 2: Декодируем LZ78
    lz78_decoder = LZ78Decoder()
    original_data = lz78_decoder.decode(lz78_encoded)

    return original_data


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"abracadabra"

    # Сжатие
    compressed = compress_lz78_ha(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия
    decompressed = decompress_lz78_ha(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"
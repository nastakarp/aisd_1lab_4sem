#compressor_bwt_rle
from algorithms.bwt import bwt_transform, bwt_inverse
from algorithms.rle import rle_encode, rle_decode


def compress_bwt_rle(data: bytes) -> bytes:
    """
    Компрессор: BWT + RLE.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    # Шаг 1: Применяем BWT
    transformed_data = bwt_transform(data.decode("utf-8"))  # BWT работает с строками
    transformed_data = transformed_data.encode("utf-8")  # Преобразуем обратно в байты

    # Шаг 2: Применяем RLE
    compressed_data = rle_encode(transformed_data)

    return compressed_data


def decompress_bwt_rle(compressed_data: bytes) -> bytes:
    """
    Декомпрессор: BWT + RLE.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Декодируем RLE
    transformed_data = rle_decode(compressed_data)

    # Шаг 2: Обратное преобразование BWT
    original_data = bwt_inverse(transformed_data.decode("utf-8"))  # BWT работает с строками
    original_data = original_data.encode("utf-8")  # Преобразуем обратно в байты

    return original_data


# Пример использования
if __name__ == "__main__":
    # Входные данные
    input_data = b"banana"
    print(f"Сжатые данные: {input_data}")
    # Сжатие
    compressed = compress_bwt_rle(input_data)
    print(f"Сжатые данные: {compressed}")

    # Декомпрессия
    decompressed = decompress_bwt_rle(compressed)
    print(f"Восстановленные данные: {decompressed.decode('utf-8')}")

    # Проверка корректности
    assert input_data == decompressed, "Декомпрессия не удалась!"
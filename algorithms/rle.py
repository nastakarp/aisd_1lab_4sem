#rle
def rle_encode(data: bytes) -> bytes:
    """
    Кодирование данных с использованием алгоритма RLE.
    :param data: Входные данные (байтовая строка).
    :return: Сжатые данные (байтовая строка).
    """
    encoded_data = []
    i = 0
    while i < len(data):
        current_byte = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == current_byte and count < 255:
            count += 1
        encoded_data.append(count)
        encoded_data.append(current_byte)
        i += count
    return bytes(encoded_data)

def rle_decode(compressed_data: bytes) -> bytes:
    """
    Декодирование данных, сжатых с использованием алгоритма RLE.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = []
    i = 0
    while i < len(compressed_data):
        count = compressed_data[i]
        current_byte = compressed_data[i + 1]
        decoded_data.extend([current_byte] * count)
        i += 2
    return bytes(decoded_data)
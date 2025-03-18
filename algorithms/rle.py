#rle
def rle_encode(data: bytes) -> bytes:
    """
    Кодирование Run-Length Encoding.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    encoded_data = []
    i = 0
    while i < len(data):
        current_char = data[i]
        count = 1
        while i + count < len(data) and data[i + count] == current_char:
            count += 1
        encoded_data.extend([current_char, count])
        i += count
    return bytes(encoded_data)


def rle_decode(encoded_data: bytes) -> bytes:
    """
    Декодирование Run-Length Encoding.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = []
    for i in range(0, len(encoded_data), 2):
        char = encoded_data[i]
        count = encoded_data[i + 1]
        decoded_data.extend([char] * count)
    return bytes(decoded_data)
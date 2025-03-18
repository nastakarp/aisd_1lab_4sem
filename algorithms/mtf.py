#mtf
def mtf_encode(data: bytes) -> bytes:
    """
    Кодирование Move-to-Front.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    dictionary = list(range(256))  # Инициализация словаря (0-255)
    encoded_data = []

    for byte in data:
        index = dictionary.index(byte)
        encoded_data.append(index)
        # Перемещаем символ в начало словаря
        dictionary.pop(index)
        dictionary.insert(0, byte)

    return bytes(encoded_data)


def mtf_decode(encoded_data: bytes) -> bytes:
    """
    Декодирование Move-to-Front.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    dictionary = list(range(256))  # Инициализация словаря (0-255)
    decoded_data = []

    for index in encoded_data:
        byte = dictionary[index]
        decoded_data.append(byte)
        # Перемещаем символ в начало словаря
        dictionary.pop(index)
        dictionary.insert(0, byte)

    return bytes(decoded_data)
#lz77

def lz77_encode(data: bytes, buffer_size: int) -> bytes:
    """
    Кодирование LZ77.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера (скользящего окна).
    :return: Закодированные данные (байтовая строка).
    """
    encoded_data = []
    i = 0
    while i < len(data):
        # Определяем границы поиска
        search_start = max(0, i - buffer_size)
        search_window = data[search_start:i]

        # Ищем максимальное совпадение
        max_length = 0
        max_offset = 0
        next_char = data[i] if i < len(data) else b""

        # Перебираем возможные смещения
        for offset in range(1, len(search_window) + 1):
            length = 0
            while (i + length < len(data)) and (data[i + length] == search_window[-offset + length % offset]):
                length += 1
            if length > max_length:
                max_length = length
                max_offset = offset

        # Если найдено совпадение, добавляем (смещение, длина, следующий символ)
        if max_length > 0:
            next_char = data[i + max_length] if i + max_length < len(data) else 0
            encoded_data.append((max_offset, max_length, next_char))
            i += max_length + 1
        else:
            # Если совпадений нет, добавляем (0, 0, следующий символ)
            encoded_data.append((0, 0, data[i]))
            i += 1

    # Преобразуем тройки в байты
    compressed_data = []
    for offset, length, char in encoded_data:
        compressed_data.extend([offset >> 8, offset & 0xFF, length, char])
    return bytes(compressed_data)


def lz77_decode(encoded_data: bytes, buffer_size: int) -> bytes:
    """
    Декодирование LZ77.
    :param encoded_data: Закодированные данные (байтовая строка).
    :param buffer_size: Размер буфера (скользящего окна).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = []
    i = 0
    while i < len(encoded_data):
        # Читаем тройку (смещение, длина, следующий символ)
        offset = (encoded_data[i] << 8) + encoded_data[i + 1]
        length = encoded_data[i + 2]
        char = encoded_data[i + 3]
        i += 4

        # Восстанавливаем данные
        if offset > 0:
            start = len(decoded_data) - offset
            for _ in range(length):
                decoded_data.append(decoded_data[start])
                start += 1
        if char != 0:  # Игнорируем нулевой символ
            decoded_data.append(char)

    return bytes(decoded_data)

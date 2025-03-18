#lz77
def lz77_encode(data: bytes, buffer_size: int) -> bytes:
    """
    Кодирование данных с использованием алгоритма LZ77.
    :param data: Входные данные (байтовая строка).
    :param buffer_size: Размер буфера.
    :return: Сжатые данные (байтовая строка).
    """
    compressed_data = []
    i = 0
    while i < len(data):
        # Ищем максимальное совпадение в буфере
        match_offset, match_length = 0, 0
        for offset in range(1, min(buffer_size, i) + 1):
            current_length = 0
            while (i + current_length < len(data) and
                   data[i + current_length] == data[i - offset + current_length]):
                current_length += 1
            if current_length > match_length:
                match_offset, match_length = offset, current_length

        # Ограничиваем длину совпадения 255
        match_length = min(match_length, 255)

        # Получаем следующий символ
        next_char = data[i + match_length] if i + match_length < len(data) else b''

        # Добавляем тройку (offset, length, next_char) в сжатые данные
        compressed_data.append(match_offset)
        compressed_data.append(match_length)
        if next_char:
            compressed_data.append(next_char)

        # Перемещаем указатель
        i += match_length + 1

    # Преобразуем список в байты
    return bytes(compressed_data)

def lz77_decode(compressed_data: bytes) -> bytes:
    """
    Декодирование данных, сжатых с использованием алгоритма LZ77.
    :param compressed_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decompressed_data = []
    i = 0
    while i < len(compressed_data):
        # Читаем тройку (offset, length, next_char)
        match_offset = compressed_data[i]
        match_length = compressed_data[i + 1]
        next_char = compressed_data[i + 2] if i + 2 < len(compressed_data) else None

        # Восстанавливаем данные
        for _ in range(match_length):
            decompressed_data.append(decompressed_data[-match_offset])
        if next_char is not None:
            decompressed_data.append(next_char)

        # Перемещаем указатель
        i += 3 if next_char is not None else 2

    return bytes(decompressed_data)
def lz77_encode(data: bytes, buffer_size: int = 8192) -> bytes:
    """
    Кодирует данные с использованием алгоритма LZ77.
    :param data: Исходные данные (байтовая строка).
    :param buffer_size: Размер буфера для поиска совпадений.
    :return: Сжатые данные (байтовая строка).
    """
    encoded_data = bytearray()
    i = 0
    n = len(data)

    while i < n:
        max_length = 0
        max_offset = 0

        # Определяем границы поиска
        search_start = max(0, i - buffer_size)
        search_end = i

        # Ищем максимальное совпадение
        for length in range(min(255, n - i), 0, -1):
            substring = data[i:i + length]
            offset = data[search_start:search_end].rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = search_end - search_start - offset
                break

        if max_length > 0:
            # Кодируем offset и length в два байта каждый
            encoded_data.append((max_offset >> 8) & 0xFF)  # Старший байт offset
            encoded_data.append(max_offset & 0xFF)  # Младший байт offset
            encoded_data.append((max_length >> 8) & 0xFF)  # Старший байт length
            encoded_data.append(max_length & 0xFF)  # Младший байт length
            i += max_length
        else:
            # Если совпадений нет, кодируем как символ
            encoded_data.append(0)  # offset = 0 (старший байт)
            encoded_data.append(0)  # offset = 0 (младший байт)
            encoded_data.append(0)  # length = 0 (старший байт)
            encoded_data.append(0)  # length = 0 (младший байт)
            encoded_data.append(data[i])  # символ (1 байт)
            i += 1

    return bytes(encoded_data)

def lz77_decode(encoded_data: bytes) -> bytes:
    """
    Декодирует данные, сжатые с использованием алгоритма LZ77.
    :param encoded_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)

    while i < n:
        # Читаем offset и length (по два байта каждый)
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            # Это символ
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            # Это ссылка
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])

    return bytes(decoded_data)
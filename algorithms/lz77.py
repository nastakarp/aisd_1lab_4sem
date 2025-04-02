def lz77_encode(data: bytes, buffer_size: int = 8192) -> bytes:
    """
    Кодирует данные с использованием алгоритма LZ77.
    :param data: Исходные данные (байтовая строка).
    :param buffer_size: Размер буфера для поиска совпадений.
    :return: Сжатые данные (байтовая строка).
    """
    encoded_data = bytearray()  # Создаем пустой массив для сжатых данных
    i = 0  # Текущая позиция в исходных данных
    n = len(data)  # Общая длина данных

    while i < n:  # Пока не обработали все данные
        max_length = 0  # Длина наилучшего найденного совпадения
        max_offset = 0  # Смещение наилучшего совпадения

        # Определяем границы поиска в скользящем окне:
        search_start = max(0, i - buffer_size)  # Начало окна (не может быть < 0)
        search_end = i  # Конец окна - текущая позиция

        # Ищем максимальное совпадение (начиная с самой длинной возможной последовательности)
        for length in range(min(255, n - i), 0, -1):  # От 255 или до конца данных
            substring = data[i:i + length]  # Подстрока для поиска
            # Ищем последнее вхождение подстроки в окне поиска
            offset = data[search_start:search_end].rfind(substring)

            if offset != -1:  # Если нашли совпадение
                max_length = length  # Запоминаем длину
                # Вычисляем смещение от текущей позиции
                max_offset = search_end - search_start - offset
                break  # Прерываем поиск, т.к. нашли максимальную длину

        if max_length > 0:  # Если нашли совпадение
            # Кодируем offset (2 байта) и length (2 байта):
            encoded_data.append((max_offset >> 8) & 0xFF)  # Старший байт offset
            encoded_data.append(max_offset & 0xFF)  # Младший байт offset
            encoded_data.append((max_length >> 8) & 0xFF)  # Старший байт length
            encoded_data.append(max_length & 0xFF)  # Младший байт length
            i += max_length  # Перемещаем указатель на длину совпадения
        else:
            # Если совпадений нет, кодируем как новый символ
            encoded_data.append(0)  # offset = 0 (старший байт)
            encoded_data.append(0)  # offset = 0 (младший байт)
            encoded_data.append(0)  # length = 0 (старший байт)
            encoded_data.append(0)  # length = 0 (младший байт)
            encoded_data.append(data[i])  # Сам символ (1 байт)
            i += 1  # Перемещаем указатель на 1 символ

    return bytes(encoded_data)  # Возвращаем сжатые данные


def lz77_decode(encoded_data: bytes) -> bytes:
    """
    Декодирует данные, сжатые с использованием алгоритма LZ77.
    :param encoded_data: Сжатые данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    decoded_data = bytearray()  # Буфер для распакованных данных
    i = 0  # Текущая позиция в сжатых данных
    n = len(encoded_data)  # Общая длина сжатых данных

    while i < n:  # Пока не обработали все сжатые данные
        # Читаем offset и length (по два байта каждый):
        # Собираем 2 байта в 16-битное число для offset
        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        # Собираем 2 байта в 16-битное число для length
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4  # Перемещаем указатель на 4 байта вперед

        if offset == 0 and length == 0:  # Если это одиночный символ
            decoded_data.append(encoded_data[i])  # Добавляем символ в выходные данные
            i += 1  # Перемещаем указатель на 1 байт
        else:  # Если это ссылка на предыдущие данные
            start = len(decoded_data) - offset  # Начало совпадения в распакованных данных
            end = start + length  # Конец совпадения
            # Копируем найденный участок в конец буфера
            decoded_data.extend(decoded_data[start:end])

    return bytes(decoded_data)  # Возвращаем распакованные данные
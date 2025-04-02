def rle_compress(data: bytes) -> bytes:
    """Сжимает данные с использованием RLE."""
    compressed_data = bytearray()  # Создаем пустой массив для сжатых данных
    n = len(data)  # Получаем длину исходных данных
    i = 0  # Указатель на текущую позицию в исходных данных

    while i < n:  # Пока не обработали все данные
        current_byte = data[i]  # Берем текущий байт
        count = 1  # Счетчик повторений (минимум 1)

        # Ищем количество повторений текущего байта (максимум 255)
        while i + count < n and count < 255 and data[i + count] == current_byte:
            count += 1

        if count > 1:  # Если нашли повторения (2 и более)
            compressed_data.append(count)  # Добавляем счетчик
            compressed_data.append(current_byte)  # Добавляем сам байт
            i += count  # Перемещаем указатель вперед на count позиций
        else:  # Если повторений нет
            non_repeating = bytearray()  # Буфер для неповторяющихся байтов
            # Собираем последовательность неповторяющихся байтов
            while i < n and (i + 1 >= n or data[i] != data[i + 1]):
                non_repeating.append(data[i])
                i += 1
                if len(non_repeating) == 255:  # Максимальная длина блока - 255
                    break
            # Добавляем маркер неповторяющейся последовательности (0)
            compressed_data.append(0)
            # Добавляем длину последовательности
            compressed_data.append(len(non_repeating))
            # Добавляем саму последовательность
            compressed_data.extend(non_repeating)

def rle_decompress(compressed_data: bytes) -> bytes:
    """Декомпрессия RLE."""
    decompressed_data = bytearray()  # Буфер для распакованных данных
    n = len(compressed_data)  # Длина сжатых данных
    i = 0  # Указатель на текущую позицию в сжатых данных

    while i < n:  # Пока не обработали все сжатые данные
        flag = compressed_data[i]  # Читаем флаг/счетчик
        if flag == 0:  # Если это маркер неповторяющейся последовательности
            length = compressed_data[i + 1]  # Читаем длину последовательности
            # Копируем последовательность в выходной буфер
            decompressed_data.extend(compressed_data[i + 2:i + 2 + length])
            i += 2 + length  # Перемещаем указатель
        else:  # Если это счетчик повторений
            count = flag  # Количество повторений
            byte = compressed_data[i + 1]  # Байт для повторения
            decompressed_data.extend([byte] * count)  # Добавляем count раз byte
            i += 2  # Перемещаем указатель на следующую пару
def bwt_transform(data: bytes, chunk_size: int = 1024) -> tuple[bytes, list[int]]:
    transformed_data = bytearray()  # Буфер для преобразованных данных
    indices = []  # Список индексов для каждого чанка

    # Обрабатываем данные по чанкам
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]  # Берем текущий чанк
        index, encoded_chunk = transform_chunk(chunk)  # Применяем BWT к чанку
        transformed_data.extend(encoded_chunk)  # Добавляем результат
        indices.append(index)  # Сохраняем индекс

    return bytes(transformed_data), indices


def transform_chunk(chunk: bytes) -> tuple[int, bytes]:
    # Генерируем все возможные вращения строки
    rotations = [chunk[i:] + chunk[:i] for i in range(len(chunk))]

    # Сортируем вращения лексикографически
    rotations.sort()

    # Находим индекс исходной строки в отсортированном списке
    original_index = rotations.index(chunk)

    # Берем последние символы всех вращений
    encoded_chunk = bytes(rotation[-1] for rotation in rotations)

    return original_index, encoded_chunk


def bwt_inverse(transformed_data: bytes, indices: list[int], chunk_size: int = 1024) -> bytes:
    restored_data = bytearray()  # Буфер для восстановленных данных
    position = 0  # Текущая позиция в данных
    index = 0  # Индекс текущего чанка

    while position < len(transformed_data):
        # Определяем границы текущего чанка
        end = position + chunk_size if position + chunk_size <= len(transformed_data) else len(transformed_data)
        chunk = transformed_data[position:end]  # Берем текущий чанк
        original_index = indices[index]  # Получаем индекс для этого чанка

        # Восстанавливаем чанк
        restored_chunk = reverse_transform_chunk(original_index, chunk)
        restored_data.extend(restored_chunk)

        # Переходим к следующему чанку
        position = end
        index += 1

    return bytes(restored_data)


def reverse_transform_chunk(original_index: int, encoded_chunk: bytes) -> bytes:
    # Создаем таблицу пар (символ, исходный индекс)
    table = [(char, idx) for idx, char in enumerate(encoded_chunk)]

    # Сортируем таблицу лексикографически
    table.sort()

    result = bytearray()  # Буфер для результата
    current_row = original_index  # Начинаем с оригинального индекса

    for _ in range(len(encoded_chunk)):
        # Получаем символ и следующий индекс
        char, current_row = table[current_row]
        result.append(char)  # Добавляем символ

    return bytes(result)
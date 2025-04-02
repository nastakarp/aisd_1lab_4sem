def mtf_transform(data: bytes) -> bytes:
    # Инициализируем алфавит - список чисел от 0 до 255 (все возможные байты)
    alphabet = list(range(256))
    transformed_data = bytearray()  # Буфер для преобразованных данных

    for byte in data:  # Обрабатываем каждый байт входных данных
        # Находим индекс текущего байта в алфавите
        index = alphabet.index(byte)
        # Добавляем индекс в выходные данные
        transformed_data.append(index)
        # Удаляем этот байт из текущей позиции в алфавите
        alphabet.pop(index)
        # Вставляем этот байт в начало алфавита
        alphabet.insert(0, byte)

    return bytes(transformed_data)


def mtf_inverse(transformed_data: bytes) -> bytes:
    # Инициализируем такой же алфавит
    alphabet = list(range(256))
    original_data = bytearray()  # Буфер для восстановленных данных

    for index in transformed_data:  # Обрабатываем каждый индекс
        # Получаем байт по индексу из алфавита
        byte = alphabet[index]
        # Добавляем байт в выход
        original_data.append(byte)
        # Удаляем этот байт из текущей позиции
        alphabet.pop(index)
        # Вставляем его в начало алфавита
        alphabet.insert(0, byte)

    return bytes(original_data)
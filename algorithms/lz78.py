# Класс для кодирования данных по алгоритму LZ78
class LZ78Encoder:
    def __init__(self):
        # Инициализация словаря с пустой строкой (код 0)
        self.dictionary = {b'': 0}
        # Следующий доступный код для добавления в словарь
        self.next_code = 1

    def encode(self, data: bytes) -> list:
        # Результат кодирования - список кортежей (код, байт)
        encoded_data = []
        # Текущая накапливаемая строка для поиска в словаре
        current_string = b''

        # Обрабатываем каждый байт входных данных
        for byte in data:
            # Формируем новую строку путем добавления текущего байта
            new_string = current_string + bytes([byte])

            # Если новая строка есть в словаре, продолжаем накапливать
            if new_string in self.dictionary:
                current_string = new_string
            else:
                # Добавляем в выходные данные пару (код, байт)
                encoded_data.append((self.dictionary[current_string], byte))
                # Добавляем новую строку в словарь
                self.dictionary[new_string] = self.next_code
                self.next_code += 1
                # Сбрасываем текущую строку
                current_string = b''

        # Обработка оставшейся строки (если есть)
        if current_string:
            # Используем специальный маркер 256 для конца данных
            encoded_data.append((self.dictionary[current_string], 256))

        return encoded_data


# Класс для декодирования данных по алгоритму LZ78
class LZ78Decoder:
    def __init__(self):
        # Инициализация словаря с пустой строкой (код 0)
        self.dictionary = {0: b''}

    def decode(self, encoded_data: list) -> bytes:
        # Результат декодирования
        decoded_data = []

        # Обрабатываем каждый элемент закодированных данных
        for code, byte in encoded_data:
            # Проверка на валидность кода
            if code not in self.dictionary:
                raise ValueError(f"Invalid code {code} in encoded data")

            # Если встретили маркер конца данных
            if byte == 256:
                entry = self.dictionary[code]
            else:
                # Формируем новую строку из словаря + новый байт
                entry = self.dictionary[code] + bytes([byte])
                # Добавляем в словарь только если это не последняя запись
                if byte != 256:
                    self.dictionary[len(self.dictionary)] = entry

            # Добавляем декодированную строку в результат
            decoded_data.append(entry)

        # Объединяем все части в единый bytes объект
        return b''.join(decoded_data)


# Функция для сжатия данных с использованием LZ78
def compress_lz78(data: bytes) -> bytes:
    # Создаем кодировщик
    encoder = LZ78Encoder()
    # Получаем закодированные данные в виде списка пар (код, байт)
    encoded_data = encoder.encode(data)

    # Определяем необходимый размер в байтах для хранения кодов
    max_code = max((code for code, _ in encoded_data), default=0)
    # Вычисляем минимальное количество байт для хранения максимального кода
    code_bytes = (max_code.bit_length() + 7) // 8
    # Гарантируем минимум 1 байт
    code_bytes = max(1, code_bytes)

    # Подготавливаем выходные сжатые данные
    compressed_data = bytearray()
    for code, byte in encoded_data:
        # Добавляем код в нужном количестве байт
        compressed_data.extend(code.to_bytes(code_bytes, 'big'))
        # Обработка специального маркера конца (256)
        if byte == 256:
            compressed_data.extend((255, 255))  # Используем 255,255 для представления 256
        else:
            compressed_data.append(byte)

    # Добавляем заголовок (размер кода и версию формата)
    header = bytes([code_bytes, 1])  # Версия 1
    return header + compressed_data


# Функция для распаковки данных, сжатых LZ78
def decompress_lz78(compressed_data: bytes) -> bytes:
    # Проверка на пустые входные данные
    if len(compressed_data) < 2:
        return b''

    # Чтение заголовка (первый байт - размер кода, второй - версия)
    code_bytes, version = compressed_data[:2]
    # Проверка версии формата
    if version != 1:
        raise ValueError("Unsupported compression version")

    # Подготовка списка закодированных данных для декодера
    encoded_data = []
    pos = 2  # Позиция после заголовка

    # Обработка сжатых данных
    while pos + code_bytes <= len(compressed_data):
        # Чтение кода
        code = int.from_bytes(compressed_data[pos:pos + code_bytes], 'big')
        pos += code_bytes

        # Проверка на конец данных
        if pos >= len(compressed_data):
            break

        # Чтение байта
        byte = compressed_data[pos]
        pos += 1

        # Обработка специальной последовательности 255,255 (представляющей 256)
        if byte == 255 and pos < len(compressed_data) and compressed_data[pos] == 255:
            byte = 256
            pos += 1

        # Добавление пары (код, байт) в список
        encoded_data.append((code, byte))

    # Создаем декодер и выполняем декодирование
    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)
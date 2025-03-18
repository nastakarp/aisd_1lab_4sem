import os


def read_file(file_path: str) -> bytes:
    """
    Чтение данных из файла.
    :param file_path: Путь к файлу.
    :return: Данные в виде байтовой строки.
    """
    with open(file_path, "rb") as file:
        return file.read()


def write_file(file_path: str, data: bytes):
    """
    Запись данных в файл.
    :param file_path: Путь к файлу.
    :param data: Данные для записи (байтовая строка).
    """
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(data)


def process_file(input_file: str, output_compressed: str, output_decompressed: str, compress_func, decompress_func, buffer_size: int = 1024):
    """
    Обработка файла: сжатие и декомпрессия.
    :param input_file: Путь к входному файлу.
    :param output_compressed: Путь к файлу для сохранения сжатых данных.
    :param output_decompressed: Путь к файлу для сохранения восстановленных данных.
    :param compress_func: Функция для сжатия данных.
    :param decompress_func: Функция для декомпрессии данных.
    :param buffer_size: Размер буфера для LZ77.
    """
    # Чтение данных из файла
    data = read_file(input_file)

    # Сжатие данных
    compressed = compress_func(data, buffer_size)
    write_file(output_compressed, compressed)

    # Декомпрессия данных
    decompressed = decompress_func(compressed, buffer_size)
    write_file(output_decompressed, decompressed)

    # Проверка корректности
    assert data == decompressed, "Декомпрессия не удалась!"
    print("Обработка файла завершена успешно!")
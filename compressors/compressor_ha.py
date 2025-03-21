# compressor_ha
from algorithms.huffman import count_symb, build_huffman_tree, generate_codes
import pickle
from PIL import Image
import numpy as np
import os  # Убедитесь, что модуль os импортирован


def huffman_compress(data: bytes) -> bytes:
    """
    Кодирование Хаффмана с сохранением таблицы кодов.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    frequency = count_symb(data)
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = generate_codes(huffman_tree)

    encoded_bits = "".join([huffman_codes[byte] for byte in data])
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += "0" * padding
    encoded_bytes = bytes([int(encoded_bits[i:i + 8], 2) for i in range(0, len(encoded_bits), 8)])

    # Сохраняем таблицу кодов и padding в сжатых данных
    metadata = {
        "codes": huffman_codes,
        "padding": padding,
    }
    metadata_bytes = pickle.dumps(metadata)
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


def huffman_decompress(encoded_data: bytes) -> bytes:
    """
    Декодирование Хаффмана с использованием таблицы кодов.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Извлекаем длину метаданных
    metadata_length = int.from_bytes(encoded_data[:4], "big")
    metadata_bytes = encoded_data[4:4 + metadata_length]
    encoded_bytes = encoded_data[4 + metadata_length:]

    # Восстанавливаем таблицу кодов и padding
    metadata = pickle.loads(metadata_bytes)
    huffman_codes = metadata["codes"]
    padding = metadata["padding"]

    # Преобразуем байты в битовую строку
    encoded_bits = "".join([f"{byte:08b}" for byte in encoded_bytes])
    encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits

    # Создаем таблицу для обратного поиска (битовая строка -> символ)
    reverse_codes = {v: k for k, v in huffman_codes.items()}

    # Декодируем битовую строку
    current_bits = ""
    decoded_data = []
    for bit in encoded_bits:
        current_bits += bit
        if current_bits in reverse_codes:
            decoded_data.append(reverse_codes[current_bits])
            current_bits = ""

    return bytes(decoded_data)


def compress_file(input_file: str, output_file: str):
    """
    Сжимает файл с использованием алгоритма Хаффмана.
    :param input_file: Путь к исходному файлу.
    :param output_file: Путь к файлу для сохранения сжатых данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    with open(input_file, "rb") as f:
        data = f.read()

    compressed_data = huffman_compress(data)

    with open(output_file, "wb") as f:
        f.write(compressed_data)


def decompress_file(input_file: str, output_file: str):
    """
    Распаковывает файл, сжатый алгоритмом Хаффмана.
    :param input_file: Путь к сжатому файлу.
    :param output_file: Путь к файлу для сохранения восстановленных данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    with open(input_file, "rb") as f:
        compressed_data = f.read()

    decompressed_data = huffman_decompress(compressed_data)

    with open(output_file, "wb") as f:
        f.write(decompressed_data)


def compress_image(input_image_path: str, output_compressed_path: str):
    """
    Сжимает изображение с использованием алгоритма Хаффмана.
    :param input_image_path: Путь к исходному изображению.
    :param output_compressed_path: Путь для сохранения сжатых данных.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_compressed_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    # Открываем изображение
    image = Image.open(input_image_path)
    image_data = np.array(image)  # Преобразуем изображение в массив numpy

    # Получаем размеры изображения
    height, width = image_data.shape[:2]

    # Преобразуем данные изображения в байты
    if image.mode == "1":  # Черно-белое изображение
        data = image_data.tobytes()
    elif image.mode == "L":  # Серое изображение
        data = image_data.tobytes()
    elif image.mode == "RGB":  # Цветное изображение
        # Разделяем на каналы R, G, B
        r, g, b = image_data[:, :, 0], image_data[:, :, 1], image_data[:, :, 2]
        data = {
            "r": r.tobytes(),
            "g": g.tobytes(),
            "b": b.tobytes(),
        }
    else:
        raise ValueError("Неподдерживаемый формат изображения")

    # Сжимаем данные
    if isinstance(data, dict):  # Цветное изображение
        compressed_data = {
            "r": huffman_compress(data["r"]),
            "g": huffman_compress(data["g"]),
            "b": huffman_compress(data["b"]),
            "height": height,
            "width": width,
        }
    else:  # Черно-белое или серое изображение
        compressed_data = {
            "data": huffman_compress(data),
            "height": height,
            "width": width,
        }

    # Сохраняем сжатые данные
    with open(output_compressed_path, "wb") as f:
        pickle.dump(compressed_data, f)


def decompress_image(input_compressed_path: str, output_image_path: str):
    """
    Распаковывает изображение, сжатое алгоритмом Хаффмана.
    :param input_compressed_path: Путь к сжатому файлу.
    :param output_image_path: Путь для сохранения восстановленного изображения.
    """
    # Проверяем, существует ли директория для выходного файла
    output_dir = os.path.dirname(output_image_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Создаем директорию, если её нет

    # Загружаем сжатые данные
    with open(input_compressed_path, "rb") as f:
        compressed_data = pickle.load(f)

    # Извлекаем высоту и ширину
    height = compressed_data["height"]
    width = compressed_data["width"]

    # Распаковываем данные
    if "r" in compressed_data:  # Цветное изображение
        r = huffman_decompress(compressed_data["r"])
        g = huffman_decompress(compressed_data["g"])
        b = huffman_decompress(compressed_data["b"])
        # Преобразуем байты обратно в массив numpy
        r = np.frombuffer(r, dtype=np.uint8).reshape((height, width))
        g = np.frombuffer(g, dtype=np.uint8).reshape((height, width))
        b = np.frombuffer(b, dtype=np.uint8).reshape((height, width))
        # Объединяем каналы
        image_data = np.stack((r, g, b), axis=-1)
    else:  # Черно-белое или серое изображение
        data = huffman_decompress(compressed_data["data"])
        image_data = np.frombuffer(data, dtype=np.uint8).reshape((height, width))

    # Создаем изображение из данных
    image = Image.fromarray(image_data)

    # Сохраняем изображение
    image.save(output_image_path)


# Пример использования
if __name__ == "__main__":
    input_data = "C:/OPP/compression_project/tests/test1_enwik7"
    compress_data = "C:/OPP/compression_project/results/compressed/test1/c_enwik7_ha.bin"
    decompress_data = "C:/OPP/compression_project/results/decompressors/test1/d_enwik7_ha.txt"
    # Сжимаем файл enwik7
    compress_file(input_data, compress_data)
    # Распаковываем файл
    decompress_file(compress_data, decompress_data)
    print("Сжатие и распаковка enwik7 завершены.")

    # Обработка файла test2 (русский текст)
    input_data_ru = "C:/OPP/compression_project/tests/test2_rus.txt"
    compress_data_ru = "C:/OPP/compression_project/results/compressed/test2/rus_ha.bin"
    decompress_data_ru = "C:/OPP/compression_project/results/decompressors/test2/rus_ha.bin"
    # Сжимаем файл test2
    compress_file(input_data_ru, compress_data_ru)
    # Распаковываем файл
    decompress_file(compress_data_ru, decompress_data_ru)
    print("Сжатие и распаковка русского текста завершены.")

    # Обработка бинарного файла
    binary_input = "C:/OPP/compression_project/tests/test3_bin.exe"
    binary_compressed = "C:/OPP/compression_project/results/compressed/test3/binary_file_compressed.bin"
    binary_decompressed = "C:/OPP/compression_project/results/decompressors/test3/binary_file_decompressed.bin"
    compress_file(binary_input, binary_compressed)
    decompress_file(binary_compressed, binary_decompressed)
    print("Бинарный файл сжат и распакован.")

    # Обработка черно-белого изображения
    bw_input = "C:/OPP/compression_project/tests/black_white_image.png"
    bw_compressed = "C:/OPP/compression_project/results/compressed/test4/bw_image_compressed.bin"
    bw_decompressed = "C:/OPP/compression_project/results/decompressors/test4/bw_image_decompressed.png"
    compress_image(bw_input, bw_compressed)
    decompress_image(bw_compressed, bw_decompressed)
    print("Черно-белое изображение сжато и распаковано.")

    # Обработка серого изображения
    gray_input = "C:/OPP/compression_project/tests/gray_image.png"
    gray_compressed = "C:/OPP/compression_project/results/compressed/test5/gray_image_compressed.bin"
    gray_decompressed = "C:/OPP/compression_project/results/decompressors/test5/gray_image_decompressed.png"
    compress_image(gray_input, gray_compressed)
    decompress_image(gray_compressed, gray_decompressed)
    print("Серое изображение сжато и распаковано.")

    # Обработка цветного изображения
    color_input = "C:/OPP/compression_project/tests/color_image.png"
    color_compressed = "C:/OPP/compression_project/results/compressed/test6/color_image_compressed.bin"
    color_decompressed = "C:/OPP/compression_project/results/decompressors/test6/color_image_decompressed.png"
    compress_image(color_input, color_compressed)
    decompress_image(color_compressed, color_decompressed)
    print("Цветное изображение сжато и распаковано.")

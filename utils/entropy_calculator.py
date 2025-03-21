from collections import Counter
import math


def calculate_entropy(data: bytes) -> float:
    """
    Вычисление энтропии данных.
    :param data: Входные данные (байтовая строка).
    :return: Энтропия (бит/символ).
    """
    if not data:
        return 0.0

    # Вычисляем частоту каждого символа
    counter = Counter(data)
    total_length = len(data)

    # Вычисляем энтропию
    entropy = 0.0
    for count in counter.values():
        probability = count / total_length
        entropy -= probability * math.log2(probability)



def calculate_entropy_from_file(file_path: str) -> float:
    """
    Вычисление энтропии данных из файла.
    :param file_path: Путь к файлу.
    :return: Значение энтропии в битах.
    """
    with open(file_path, "rb") as file:
        data = file.read()
    return calculate_entropy(data)
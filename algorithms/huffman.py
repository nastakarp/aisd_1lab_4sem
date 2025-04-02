import heapq  # Импорт модуля для работы с кучей (приоритетной очередью)
from collections import Counter  # Импорт Counter для подсчета частот символов
import pickle  # Импорт модуля для сериализации/десериализации объектов Python


class Node:
    """
    Класс, представляющий узел в дереве Хаффмана.
    Каждый узел может быть либо листом (с символом), либо внутренним узлом (с потомками).
    """

    def __init__(self, symbol=None, counter=None, left=None, right=None):
        """
        Инициализация узла.
        :param symbol: Символ, если узел является листом
        :param counter: Частота символа или сумма частот потомков
        :param left: Левый потомок
        :param right: Правый потомок
        """
        self.symbol = symbol  # Символ (только для листовых узлов)
        self.counter = counter  # Частота символа или сумма частот потомков
        self.left = left  # Левый потомок
        self.right = right  # Правый потомок

    def __lt__(self, other):
        """
        Метод для сравнения узлов по частоте (необходим для работы heapq).
        Позволяет сравнивать узлы при помещении в кучу.
        :param other: Другой узел для сравнения
        :return: True, если текущий узел имеет меньшую частоту
        """
        return self.counter < other.counter


def count_symb(data: bytes) -> dict:
    """
    Подсчитывает частоту символов в данных.
    :param data: Входные данные (байтовая строка).
    :return: Словарь с частотами символов (ключ - символ, значение - частота).
    """
    return Counter(data)  # Используем Counter для автоматического подсчета частот


def build_huffman_tree(frequency: dict) -> Node:
    """
    Строит дерево Хаффмана на основе частот символов.
    :param frequency: Словарь с частотами символов.
    :return: Корень дерева Хаффмана.
    """
    heap = []
    # Создаем начальную кучу из узлов для каждого символа
    for symbol, weight in frequency.items():
        heapq.heappush(heap, Node(symbol=symbol, counter=weight))

    # Пока в куче больше одного элемента
    while len(heap) > 1:
        # Извлекаем два узла с наименьшими частотами
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        # Создаем новый родительский узел с суммой частот потомков
        parent = Node(counter=left.counter + right.counter, left=left, right=right)
        # Добавляем новый узел обратно в кучу
        heapq.heappush(heap, parent)

    # Возвращаем корень дерева (последний оставшийся узел в куче)
    return heapq.heappop(heap)


def generate_codes(node: Node, code: str = "", codes: dict = None) -> dict:
    """
    Рекурсивно генерирует коды Хаффмана для каждого символа.
    :param node: Текущий узел дерева.
    :param code: Текущий код (накопленные биты пути от корня).
    :param codes: Словарь для хранения кодов (создается при первом вызове).
    :return: Словарь с кодами Хаффмана (ключ - символ, значение - битовая строка).
    """
    if codes is None:
        codes = {}  # Инициализация словаря при первом вызове

    # Если узел - лист (содержит символ)
    if node.symbol is not None:
        codes[node.symbol] = code  # Сохраняем код для символа
    else:
        # Рекурсивно обходим левое поддерево, добавляя '0' к коду
        generate_codes(node.left, code + "0", codes)
        # Рекурсивно обходим правое поддерево, добавляя '1' к коду
        generate_codes(node.right, code + "1", codes)
    return codes


def huffman_compress(data: bytes) -> bytes:
    """
    Кодирование данных с использованием алгоритма Хаффмана.
    Сохраняет таблицу кодов в сжатых данных.
    :param data: Входные данные (байтовая строка).
    :return: Закодированные данные (байтовая строка).
    """
    # Шаг 1: Подсчет частот символов
    frequency = count_symb(data)
    # Шаг 2: Построение дерева Хаффмана
    huffman_tree = build_huffman_tree(frequency)
    # Шаг 3: Генерация кодов Хаффмана для каждого символа
    huffman_codes = generate_codes(huffman_tree)

    # Шаг 4: Кодирование данных с использованием полученных кодов
    encoded_bits = "".join([huffman_codes[byte] for byte in data])

    # Шаг 5: Добавление padding (выравнивание до целого числа байт)
    padding = 8 - len(encoded_bits) % 8
    if padding == 8:  # Если бит уже кратно 8, padding не нужен
        padding = 0
    encoded_bits += "0" * padding  # Добавляем нулевые биты для выравнивания

    # Преобразуем битовую строку в байты
    encoded_bytes = bytes([int(encoded_bits[i:i + 8], 2) for i in range(0, len(encoded_bits), 8)])

    # Шаг 6: Упаковка метаданных (таблица кодов и padding)
    metadata = {
        "codes": huffman_codes,  # Таблица кодов Хаффмана
        "padding": padding,  # Количество добавленных бит для выравнивания
    }
    # Сериализуем метаданные в байты
    metadata_bytes = pickle.dumps(metadata)

    # Возвращаем результат:
    # 1. 4 байта - длина метаданных
    # 2. Сериализованные метаданные
    # 3. Закодированные данные
    return len(metadata_bytes).to_bytes(4, "big") + metadata_bytes + encoded_bytes


def huffman_decompress(encoded_data: bytes) -> bytes:
    """
    Декодирование данных, сжатых алгоритмом Хаффмана.
    :param encoded_data: Закодированные данные (байтовая строка).
    :return: Восстановленные данные (байтовая строка).
    """
    # Шаг 1: Извлечение длины метаданных (первые 4 байта)
    metadata_length = int.from_bytes(encoded_data[:4], "big")
    # Шаг 2: Извлечение самих метаданных
    metadata_bytes = encoded_data[4:4 + metadata_length]
    # Шаг 3: Оставшаяся часть - закодированные данные
    encoded_bytes = encoded_data[4 + metadata_length:]

    # Шаг 4: Десериализация метаданных
    metadata = pickle.loads(metadata_bytes)
    huffman_codes = metadata["codes"]  # Таблица кодов Хаффмана
    padding = metadata["padding"]  # Количество бит padding

    # Шаг 5: Преобразование байтов в битовую строку
    encoded_bits = "".join([f"{byte:08b}" for byte in encoded_bytes])
    # Удаление добавленных бит padding
    encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits

    # Шаг 6: Создание обратного словаря (код -> символ)
    reverse_codes = {v: k for k, v in huffman_codes.items()}

    # Шаг 7: Декодирование битовой строки
    current_bits = ""  # Текущая накопленная битовая последовательность
    decoded_data = []  # Список для хранения декодированных символов
    for bit in encoded_bits:
        current_bits += bit  # Добавляем очередной бит
        # Если текущая последовательность соответствует какому-то коду
        if current_bits in reverse_codes:
            decoded_data.append(reverse_codes[current_bits])  # Добавляем символ
            current_bits = ""  # Сбрасываем текущую последовательность

    # Возвращаем декодированные данные как байтовую строку
    return bytes(decoded_data)
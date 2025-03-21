import heapq
from collections import Counter



class Node:
    def __init__(self, symbol=None, counter=None, left=None, right=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.counter < other.counter


def count_symb(data: bytes) -> dict:
    """
    Подсчитывает частоту символов в данных.
    :param data: Входные данные (байтовая строка).
    :return: Словарь с частотами символов.
    """
    return Counter(data)


def build_huffman_tree(frequency: dict) -> Node:
    """
    Строит дерево Хаффмана на основе частот символов.
    :param frequency: Словарь с частотами символов.
    :return: Корень дерева Хаффмана.
    """
    heap = []
    for symbol, weight in frequency.items():
        heapq.heappush(heap, Node(symbol=symbol, counter=weight))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(counter=left.counter + right.counter, left=left, right=right)
        heapq.heappush(heap, parent)

    return heapq.heappop(heap)


def generate_codes(node: Node, code: str = "", codes: dict = None) -> dict:
    """
    Генерирует коды Хаффмана для каждого символа.
    :param node: Текущий узел дерева.
    :param code: Текущий код.
    :param codes: Словарь для хранения кодов.
    :return: Словарь с кодами Хаффмана.
    """
    if codes is None:
        codes = {}
    if node.symbol is not None:
        codes[node.symbol] = code
    else:
        generate_codes(node.left, code + "0", codes)
        generate_codes(node.right, code + "1", codes)
    return codes



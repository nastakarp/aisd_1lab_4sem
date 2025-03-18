def bwt_transform(data: str) -> str:
    """
    Прямое преобразование Барроуза-Уиллера.
    :param data: Входная строка.
    :return: Преобразованная строка.
    """
    data = data + "$"
    rotations = [data[i:] + data[:i] for i in range(len(data))]
    rotations.sort()
    last_column = "".join([rotation[-1] for rotation in rotations])
    return last_column


def bwt_inverse(transformed_data: str) -> str:
    """
    Обратное преобразование Барроуза-Уиллера.
    :param transformed_data: Преобразованная строка.
    :return: Исходная строка.
    """
    table = [""] * len(transformed_data)
    for _ in range(len(transformed_data)):
        table = [transformed_data[i] + table[i] for i in range(len(transformed_data))]
        table.sort()
    for row in table:
        if row.endswith("$"):
            return row.rstrip("$")
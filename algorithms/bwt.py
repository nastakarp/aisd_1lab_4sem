def build_suffix_array(data: bytes) -> list[int]:
    """Строит суффиксный массив с использованием алгоритма Manber-Myers."""
    n = len(data)
    sa = list(range(n))
    rank = [data[i] for i in range(n)]
    k = 1
    while k < n:
        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            prev, curr = sa[i - 1], sa[i]
            equal = (rank[prev] == rank[curr] and
                     (prev + k < n and curr + k < n and
                      rank[prev + k] == rank[curr + k]))
            new_rank[curr] = new_rank[prev] + (0 if equal else 1)
        rank = new_rank
        k *= 2
    return sa


def bwt_transform(data: bytes) -> tuple[bytes, int]:
    """Применяет преобразование Барроуза-Уилера к данным."""
    n = len(data)
    sa = build_suffix_array(data)
    transformed_data = bytearray(data[(sa[i] + n - 1) % n] for i in range(n))
    index = sa.index(0)
    return bytes(transformed_data), index


def bwt_inverse(transformed_data: bytes, index: int) -> bytes:
    """Обратное преобразование Барроуза-Уилера."""
    n = len(transformed_data)
    freq = [0] * 256
    for byte in transformed_data:
        freq[byte] += 1
    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]
    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = transformed_data[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1
    original_data = bytearray()
    i = index
    for _ in range(n):
        original_data.append(transformed_data[i])
        i = lf[i]
    return bytes(original_data[::-1])
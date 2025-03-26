def rle_compress(data: bytes) -> bytes:
    """Сжимает данные с использованием RLE."""
    compressed_data = bytearray()
    n = len(data)
    i = 0
    while i < n:
        current_byte = data[i]
        count = 1
        while i + count < n and count < 255 and data[i + count] == current_byte:
            count += 1
        compressed_data.append(count)
        compressed_data.append(current_byte)
        i += count
    return bytes(compressed_data)


def rle_decompress(compressed_data: bytes) -> bytes:
    """Декомпрессия данных, сжатых с использованием RLE."""
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0
    while i < n:
        count = compressed_data[i]
        byte = compressed_data[i + 1]
        decompressed_data.extend([byte] * count)
        i += 2
    return bytes(decompressed_data)
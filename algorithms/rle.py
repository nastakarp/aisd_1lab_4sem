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

        if count > 1:
            compressed_data.append(count)
            compressed_data.append(current_byte)
            i += count
        else:
            non_repeating = bytearray()
            while i < n and (i + 1 >= n or data[i] != data[i + 1]):
                non_repeating.append(data[i])
                i += 1
                if len(non_repeating) == 255:
                    break
            compressed_data.append(0)
            compressed_data.append(len(non_repeating))
            compressed_data.extend(non_repeating)

    return bytes(compressed_data)


def rle_decompress(compressed_data: bytes) -> bytes:
    """Декомпрессия RLE."""
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0

    while i < n:
        flag = compressed_data[i]
        if flag == 0:
            length = compressed_data[i + 1]
            decompressed_data.extend(compressed_data[i + 2:i + 2 + length])
            i += 2 + length
        else:
            count = flag
            byte = compressed_data[i + 1]
            decompressed_data.extend([byte] * count)
            i += 2

    return bytes(decompressed_data)
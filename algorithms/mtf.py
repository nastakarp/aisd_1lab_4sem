# Функции для MTF
def mtf_transform(data: bytes) -> bytes:
    alphabet = list(range(256))
    transformed_data = bytearray()
    for byte in data:
        index = alphabet.index(byte)
        transformed_data.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(transformed_data)


def mtf_inverse(transformed_data: bytes) -> bytes:
    alphabet = list(range(256))
    original_data = bytearray()
    for index in transformed_data:
        byte = alphabet[index]
        original_data.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)
    return bytes(original_data)
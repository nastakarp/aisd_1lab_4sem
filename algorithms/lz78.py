class LZ78Encoder:
    def __init__(self):
        self.dictionary = {b'': 0}
        self.next_code = 1

    def encode(self, data: bytes) -> list:
        encoded_data = []
        current_string = b''

        for byte in data:
            new_string = current_string + bytes([byte])
            if new_string in self.dictionary:
                current_string = new_string
            else:
                encoded_data.append((self.dictionary[current_string], byte))
                self.dictionary[new_string] = self.next_code
                self.next_code += 1
                current_string = b''

        if current_string:
            # Для последней последовательности используем byte=256 как маркер конца
            encoded_data.append((self.dictionary[current_string], 256))

        return encoded_data


class LZ78Decoder:
    def __init__(self):
        self.dictionary = {0: b''}

    def decode(self, encoded_data: list) -> bytes:
        decoded_data = []

        for code, byte in encoded_data:
            if code not in self.dictionary:
                raise ValueError(f"Invalid code {code} in encoded data")

            if byte == 256:  # Маркер конца
                entry = self.dictionary[code]
            else:
                entry = self.dictionary[code] + bytes([byte])
                # Добавляем в словарь только если это не последняя запись
                if byte != 256:
                    self.dictionary[len(self.dictionary)] = entry

            decoded_data.append(entry)

        return b''.join(decoded_data)


def compress_lz78(data: bytes) -> bytes:
    encoder = LZ78Encoder()
    encoded_data = encoder.encode(data)

    # Определяем необходимый размер для хранения кодов
    max_code = max((code for code, _ in encoded_data), default=0)
    code_bytes = (max_code.bit_length() + 7) // 8
    code_bytes = max(1, code_bytes)  # Минимум 1 байт

    compressed_data = bytearray()
    for code, byte in encoded_data:
        compressed_data.extend(code.to_bytes(code_bytes, 'big'))
        # Для byte=256 используем 2 байта
        if byte == 256:
            compressed_data.extend((255, 255))
        else:
            compressed_data.append(byte)

    # Добавляем заголовок (размер кода и маркер версии)
    header = bytes([code_bytes, 1])  # Версия 1
    return header + compressed_data


def decompress_lz78(compressed_data: bytes) -> bytes:
    if len(compressed_data) < 2:
        return b''

    code_bytes, version = compressed_data[:2]
    if version != 1:
        raise ValueError("Unsupported compression version")

    encoded_data = []
    pos = 2
    while pos + code_bytes <= len(compressed_data):
        code = int.from_bytes(compressed_data[pos:pos + code_bytes], 'big')
        pos += code_bytes

        if pos >= len(compressed_data):
            break

        byte = compressed_data[pos]
        pos += 1

        # Обработка маркера 255,255
        if byte == 255 and pos < len(compressed_data) and compressed_data[pos] == 255:
            byte = 256
            pos += 1

        encoded_data.append((code, byte))

    decoder = LZ78Decoder()
    return decoder.decode(encoded_data)
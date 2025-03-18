#lz78

class LZ78Encoder:
    def __init__(self):
        self.dictionary = {}
        self.next_code = 1

    def encode(self, data: bytes) -> list:
        """
        Кодирование LZ78.
        :param data: Входные данные (байтовая строка).
        :return: Закодированные данные (список кортежей).
        """
        encoded_data = []
        current_string = b""
        for byte in data:
            new_string = current_string + bytes([byte])
            if new_string not in self.dictionary:
                # Добавляем новую строку в словарь
                self.dictionary[new_string] = self.next_code
                self.next_code += 1
                # Кодируем текущую строку
                if current_string:
                    encoded_data.append((self.dictionary[current_string], byte))
                else:
                    encoded_data.append((0, byte))
                current_string = b""
            else:
                current_string = new_string
        # Обработка последней строки
        if current_string:
            encoded_data.append((self.dictionary[current_string], 0))
        return encoded_data


class LZ78Decoder:
    def __init__(self):
        self.dictionary = {0: b""}

    def decode(self, encoded_data: list) -> bytes:
        """
        Декодирование LZ78.
        :param encoded_data: Закодированные данные (список кортежей).
        :return: Восстановленные данные (байтовая строка).
        """
        decoded_data = []
        for code, byte in encoded_data:
            if code == 0:
                decoded_data.append(bytes([byte]))
                self.dictionary[len(self.dictionary)] = bytes([byte])
            else:
                string = self.dictionary[code]
                if byte != 0:
                    new_string = string + bytes([byte])
                    decoded_data.append(new_string)
                    self.dictionary[len(self.dictionary)] = new_string
                else:
                    decoded_data.append(string)
        return b"".join(decoded_data)


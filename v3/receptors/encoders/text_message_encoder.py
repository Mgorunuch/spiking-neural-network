from v3.receptors import encoder


class TextMessageEncoder(encoder.Encoder):
    def __init__(self):
        self.letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,?°'.split()

    def get_required_neurons_count(self):
        return len(self.letters)

    def encode(self, string=""):
        """
        Кодирует текстовый сигнал в массив индексов нейронов

        :param string: raw string
        :return: int[] (Индексы нейронов)
        """
        string = string.replace("°", "")
        string += "°"

        result = []

        for letter in string:
            for i in range(len(self.letters)):
                if letter == self.letters[i]:
                    result.append(i)
                    break

        return result

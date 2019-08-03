from receptors import decoder


class TextMessageDecoder(decoder.Decoder):
    def __init__(self):
        self.letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,?°'.split()

    def get_required_neurons_count(self):
        return len(self.letters)

    def encode(self, neuron):
        """
        Кодирует индекс нейрона в букву

        :param neuron: raw string
        :return: string (Индексы нейронов)
        """
        return self.letters[neuron]

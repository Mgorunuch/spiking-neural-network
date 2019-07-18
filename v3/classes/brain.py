from v3 import helpers


class Brain:
    """
    Класс создан для работы с нейронами.
    Является основной единицой для хранения данных.
    """

    neurons = {}

    def attach_neuron(self, neuron):
        """
        :param neuron: v3.classes Neuron
        :return: none
        """
        loc = neuron.get_raw_string_location(".")

        helpers.attach_to_dict_by_key(self.neurons, loc, neuron)

    def detach_neuron(self, neuron):
        """
        :param neuron: v3.classes Neuron
        :return: None
        """
        loc = neuron.get_raw_string_location(".")

        helpers.detach_from_dict_by_key(self.neurons, loc)

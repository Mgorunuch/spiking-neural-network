class Signal:
    def __init__(self, power, set_up=None, prev_signal=None, from_neuron=None):
        """
        :param power: Сила сигнала
        :param set_up: Функция для можификации сигнала
        """
        self.power = power
        self.prev_signal = prev_signal
        self.from_neuron = from_neuron
        if set_up is not None:
            set_up(self)

    def set_power(self, new_power):
        self.power = new_power

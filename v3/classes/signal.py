class Signal:
    def __init__(self, power, set_up=None):
        """
        :param power: Сила сигнала
        :param set_up: Функция для можификации сигнала
        """
        self.power = power
        if set_up is not None:
            set_up(self)

    def set_power(self, new_power):
        self.power = new_power

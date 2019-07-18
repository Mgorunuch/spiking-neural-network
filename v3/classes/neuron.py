class Neuron:
    def __init__(
            self,
            location_x,
            location_y,
            location_z,
            set_up_function=None,
            inactivity_function=None,
            apply_signal_function=None,
            check_spike_function=None,
            before_spike_function=None,
            after_spike_function=None,
            current_milliseconds=0,
    ):
        self.location = {
            "x": str(location_x),
            "y": str(location_y),
            "z": str(location_z),
        }
        self.inactivity_function = inactivity_function
        self.apply_signal_function = apply_signal_function
        self.check_spike_function = check_spike_function
        self.before_spike_function = before_spike_function
        self.after_spike_function = after_spike_function
        self.last_activity = current_milliseconds
        self.connections = {}
        if set_up_function is not None:
            set_up_function(self)

    def get_raw_string_location(self, delimiter="."):
        """
        Возвращает стринг позиции нейрона

        :param delimiter: Разделитель координат
        :return: string
        """
        loc = (self.location["x"], self.location["y"], self.location["z"])

        return delimiter.join(loc)

    def proceed_inactivity(self, milliseconds_passed):
        """
        Функция предназначена для модификации на основе времени неактивности

        :param milliseconds_passed: Пройдено миллисекунд с последней активности
        :return: None
        """
        if self.inactivity_function is not None:
            self.inactivity_function(self, milliseconds_passed)

    def register_activity(self, current_ms):
        """
        Функция преднаначена для записи последней активности. Вызывается автоматически.

        :param current_ms: текущее время в ms
        :return: None
        """
        self.last_activity = current_ms

    def attach_connection(self, connection):
        """
        Создает соединение между текущим и переданым нейроном

        :param connection: Соединение
        :return: None
        """
        loc = self.get_raw_string_location(".")

        if loc != connection.from_neuron.get_raw_string_location("."):
            raise Exception("Попытка сделать соединение к неравильному нейрону")

        self.connections[loc] = connection

    def remove_connection(self, neuron):
        """
        Разрушает соединение между текущим и переданым нейроном

        :param neuron: Нейрон для разрушения соединения
        :return: None
        """
        loc = neuron.get_raw_string_location(".")

        del self.connections[loc]

    def apply_input_signal(self, signal):
        """
        Функция применения сигнала к нейрону

        :param signal: v3.Signal Входноый сигнал
        :return: None
        """
        if self.apply_signal_function is not None:
            self.apply_signal_function(self, signal)

    def has_spike(self):
        """
        Функция проверки наличия спайка

        :return: bool
        """
        if self.check_spike_function is not None:
            self.check_spike_function(self)

    def before_spike(self):
        """
        Запускается перед спайком

        :return: None
        """
        if self.before_spike_function is not None:
            self.before_spike_function(self)

    def after_spike(self):
        """
        Запускается после спайка

        :return: None
        """
        if self.after_spike_function is not None:
            self.after_spike_function(self)


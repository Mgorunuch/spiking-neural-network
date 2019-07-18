class Neuron:
    def __init__(self, location_x, location_y, location_z, inactivity_function=None, current_milliseconds=0):
        self.location = {
            "x": str(location_x),
            "y": str(location_y),
            "z": str(location_z),
        }
        self.inactivity_function = inactivity_function
        self.last_activity = current_milliseconds
        self.connections = {}

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
            self.inactivity_function(milliseconds_passed)

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

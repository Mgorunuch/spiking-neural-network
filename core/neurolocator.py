import helpers
import random
from classes import location


class Neurolocator:
    @staticmethod
    def create_input_neurons(
            create_neuron_function,
            count_per_row=1,
            rows=1,
            remoteness=1,
            x_offset=0,
            y_offset=0,
            z_offset=0
    ):
        """
        ВНИМАНИЕ! Глубина - Z. Строки создаются по оси X. Движение происходит по оси Y.

        :param create_neuron_function: Функция создания нейрона
        :param count_per_row: Количество на строку
        :param rows: Строк
        :param remoteness: Отдаленность
        :param x_offset: Базовый сдвиг по координате x
        :param y_offset: Базовый сдвиг по координате y
        :param z_offset: Базовый сдвиг по координате z
        :return: []Neuron
        """
        neurons = []
        for row in range(rows):
            for neuron_number in range(count_per_row):
                x = row * remoteness + x_offset
                y = neuron_number * remoteness + y_offset
                z = 0 + z_offset
                neurons.append(create_neuron_function(x, y, z))

        return neurons

    @staticmethod
    def create_output_neurons(
            create_neuron_function,
            count_per_row=1,
            rows=1,
            remoteness=1,
            x_offset=0,
            y_offset=0,
            z_offset=0
    ):
        """
        ВНИМАНИЕ! Глубина - Z. Строки создаются по оси Y. Движение происходит по оси X.

        :param create_neuron_function: Функция создания нейрона
        :param count_per_row: Количество на строку
        :param rows: Строк
        :param remoteness: Отдаленность
        :param x_offset: Базовый сдвиг по координате x
        :param y_offset: Базовый сдвиг по координате y
        :param z_offset: Базовый сдвиг по координате z
        :return: []Neuron
        """
        neurons = []
        for row in range(rows):
            for neuron_number in range(count_per_row):
                x = neuron_number * remoteness + x_offset
                y = row * remoteness + y_offset
                z = 0 + z_offset
                neurons.append(create_neuron_function(x, y, z))

        return neurons

    @staticmethod
    def create_base_neurons(
            create_neuron_function,
            x_coord,

            y_from,
            y_to,
            y_remoteness,

            z_from,
            z_to,
            z_remoteness,
    ):
        """
        Нейроны генерируются по квадрате Z на плоскость
        с небольшим смещением по оси Y / X в одну из сторон

        :param create_neuron_function: Функция для генерации обычных нейронов
        :param x_coord: Координата X (статический параметр)

        :param y_from: С данной Y координаты идет генерация
        :param y_to: Да данной Y координаты идет генерация
        :param y_remoteness: Удаленность нейронов друг от друга по оси y

        :param z_from: С данной Z координаты идет генерация
        :param z_to: Да данной Z координаты идет генерация
        :param z_remoteness: Удаленность нейронов по оси Z
        :return:
        """
        neurons = []

        z = z_from

        while z < z_to:
            y = y_from

            while y < y_to:
                neurons.append(
                    create_neuron_function(x_coord, y, z)
                )
                y += y_remoteness

            z += z_remoteness

        return neurons

    @staticmethod
    def get_allowed_connection_ranges(c_x, c_y, c_z, remoteness):
        """
        Создает ренджи в пределах которых разрешено создавать конекшны

        :param c_x: X точки просчета
        :param c_y: Y точки просчета
        :param c_z: Z точки просчета
        :param remoteness: Отдаленность от точки просчета
        :return:
        """
        return {
            "x": {
                "from": c_x - remoteness,
                "to": c_x + remoteness,
            },
            "y": {
                "from": c_y - remoteness,
                "to": c_y + remoteness,
            },
            "z": {
                "from": c_z - remoteness,
                "to": c_z + remoteness,
            }
        }

    @staticmethod
    def get_allowed_neurons_in_ranges(ranges, dict_neurons):
        """
        Список нейронов в поданых ренджах

        :param ranges: Ренджи
        :param dict_neurons: Всего нейронов
        :return: []Neuron
        """
        neurons = []

        x_ranges = helpers.dict_items_in_range(dict_neurons, ranges["x"]["from"], ranges["x"]["to"])
        for x_range in range(len(x_ranges)):
            y_ranges = helpers.dict_items_in_range(x_ranges[x_range], ranges["y"]["from"], ranges["y"]["to"])
            for y_range in range(len(y_ranges)):
                z_ranges = helpers.dict_items_in_range(y_ranges[y_range], ranges["z"]["from"], ranges["z"]["to"])
                for z_range in range(len(z_ranges)):
                    neurons.append(z_ranges[z_range])

        return neurons

    @staticmethod
    def get_connections(from_neuron, to_neurons, back_generation_percent, create_connection_function):
        """
        Функция для создания соединений между нейронами

        :param from_neuron: Neuron с которым производится создание соединения
        :param to_neurons: []Neuron массив нейронов с которыми создаются соединения
        :param back_generation_percent: Процент генерации обратного соединения
        :param create_connection_function: Функция для создания нейрона. Возврат None если не создаем соединеник
        :return: []NeuronConnection
        """
        connections = []

        for to_neuron in to_neurons:
            if from_neuron.get_raw_string_location(".") == to_neuron.get_raw_string_location("."):
                continue

            is_back = random.randint(0, 100) < back_generation_percent

            if is_back:
                connection = create_connection_function(to_neuron, from_neuron)
            else:
                connection = create_connection_function(from_neuron, to_neuron)

            if connection is not None:
                connections.append(connection)

        return connections

    @staticmethod
    def get_connection_points(
            from_location,
            to_location,
            connection_generation_frequency,
    ):
        """
        Генерирует точки возможные точки соединения.

        :param from_location: Начальная точка (ядро нейрона)
        :param to_location: Конечная точка (конец аксона)
        :param connection_generation_frequency: количество точек между началом и концом
        :return: массив Location
        """
        connection_generation_frequency += 1

        from_caret = from_location.get_caret()
        to_caret = to_location.get_caret()

        mult_increment = helpers.multiplier_increment(
            from_caret,
            to_caret,
            connection_generation_frequency,
        )

        arr = []
        for i in range(1, connection_generation_frequency):
            arr.append(
                location.Location(
                    from_location.x * (mult_increment[0] * i),
                    from_location.y * (mult_increment[1] * i),
                    from_location.z * (mult_increment[2] * i),
                )
            )

        return arr

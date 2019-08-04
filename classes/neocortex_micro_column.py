from classes import location
from core import neurolocator
import math
import helpers


class NeucortexMicroColumn:
    def __init__(self, input_neurons, output_neurons, neurons, connections, allowed_connections):
        self.neurons = neurons
        self.input_neurons = input_neurons
        self.output_neurons = output_neurons
        self.connections = connections
        self.allowed_connections = allowed_connections

    @staticmethod
    def generate_micro_column(max_x, max_y, max_z, inputs_count, outputs_count, connection_generation_frequency):
        """
        Создание микроколонки

        :param max_x: максимальный размер по оси X
        :param max_y: масимальный размер по оси Y
        :param max_z: максимальный размер по оси Z
        :param inputs_count: Количество входящих нейронов
        :param outputs_count: Количество исходящих нейронов
        :param connection_generation_frequency: Частота соединений на входных аксонах

        :return: NeucortexMicroColumn
        """
        neurons = []
        input_neurons = []
        output_neurons = []
        connections = []
        allowed_connections = []
        input_locations = []

        if inputs_count == 1:
            input_locations.append(
                location.Location(
                    math.ceil(max_x / 2),
                    math.ceil(max_y / 2),
                    0,
                )
            )

        if inputs_count > 1:
            raise Exception("Количество входных нейронов не может быть более 1-го."
                            "Напишите распределение для большего количества вручную")

        per_layer = max_z / 6
        layers_ranges = {
            1: [0, per_layer * 1],
            2: [per_layer * 1, per_layer * 2],
            3: [per_layer * 2, per_layer * 3],
            4: [per_layer * 3, per_layer * 4],
            5: [per_layer * 4, per_layer * 5],
            6: [per_layer * 5, per_layer * 6],
        }

        for input_location in input_locations:
            allowed_connections += neurolocator.Neurolocator.get_connection_points(
                input_location,
                location.Location(
                    input_location.x,
                    input_location.y,
                    layers_ranges[6][0] + (layers_ranges[6][1] - layers_ranges[6][0]) / 2,
                ),
                connection_generation_frequency,
            )

        return NeucortexMicroColumn(neurons, input_neurons, output_neurons, connections, allowed_connections)

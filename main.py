import matplotlib
import matplotlib.pyplot as plt
import random
import numpy as np

# neuron [neuron_key, power, connections[neuron_location]connection_multiplier], last_power_up_step, power_history[tick_id]power]
# neurons[row][neuron_id]neuron
# spike_chain[tick][neuron_location][]power
# power_ups[tick][]neuron_location
# spike_resets[tick][]neuron_location


class Neuron:
    KEY_INDEX = 0
    POWER_INDEX = 1
    CONNECTIONS_INDEX = 2
    LAST_ACTIVITY_TICK = 3
    POWER_HISTORY_INDEX = 4
    DELIMITER = "_"

    @staticmethod
    def get_neuron_power(neuron):
        return neuron[Neuron.POWER_INDEX]

    @staticmethod
    def get_neuron_connections(neuron):
        return neuron[Neuron.CONNECTIONS_INDEX]

    @staticmethod
    def get_neuron_key(neuron):
        return neuron[Neuron.KEY_INDEX]

    @staticmethod
    def get_neuron_last_activity_tick(neuron):
        return neuron[Neuron.LAST_ACTIVITY_TICK]

    @staticmethod
    def get_neuron_power_history(neuron):
        return neuron[Neuron.POWER_HISTORY_INDEX]

    @staticmethod
    def parse_neuron_key(key):
        return key.split(Neuron.DELIMITER)

    @staticmethod
    def generate_neuron_key(row, index):
        return str(row) + Neuron.DELIMITER + str(index)

    @staticmethod
    def create_neuron(row, index, power):
        return [
            Neuron.generate_neuron_key(row, index),
            power,
            {},
            0,
            {'1': power}
        ]


class Main:
    CURRENT_TICK = 1
    SPIKE_GENERATION_POWER = 60
    BASE_POWER_LEVEL = 30
    DELIMITER = "_"

    GENERATED_CONNECTION_FROM = -1
    GENERATED_CONNECTION_TO = 1

    NEURON_TICK_REGENERATION_POWER = 1
    NEURON_TICK_ATTENUATION_POWER = 1

    NEURON_AFTER_SPIKE_POWER = -5

    NEURON_MIN_POWER = -5
    NEURON_MAX_POWER = 65

    neurons = {}
    spike_chain = {}
    power_ups = {}
    spike_resets = {}

    ROWS = 0
    COLS = 0

    spike_append_function = None

    def __init__(self, rows, columns, spike_append_function):
        self.generate_neurons(rows, columns)
        self.generate_connections()
        self.spike_append_function = spike_append_function

        self.ROWS = rows
        self.COLS = columns

    def proceed_tick(self):
        # print("Proceed tick started " + str(self.CURRENT_TICK))

        self.proceed_spike_resets()

        self.proceed_spikes()
        self.proceed_power_ups()

        self.store_power_to_history()

        self.CURRENT_TICK += 1

    def store_power_to_history(self):
        for row in range(self.ROWS):
            row = str(row)
            for col in range(self.COLS):
                col = str(col)
                current_power = self.neurons[row][col][Neuron.POWER_INDEX]
                self.neurons[row][col][Neuron.POWER_HISTORY_INDEX][self.CURRENT_TICK] = current_power

    def recalculation(self):
        for row in range(self.ROWS):
            row = str(row)
            for col in range(self.COLS):
                col = str(col)
                self.recalculate_neuron_power(row + "_" + col)

    def generate_neurons(self, rows, columns):
        for row in range(rows):
            for column in range(columns):
                self.register_neuron(str(row), str(column), Neuron.create_neuron(row, column, self.BASE_POWER_LEVEL))

    def generate_connections(self):
        for row_key, row in self.neurons.items():
            connect_row_key = str(int(row_key) + 1)

            if connect_row_key not in self.neurons:
                return

            for neuron_key, neuron in row.items():
                for connect_neuron_key, connect_neuron in self.neurons[connect_row_key].items():
                    connection_power = random.randint(self.GENERATED_CONNECTION_FROM, self.GENERATED_CONNECTION_TO)
                    connect_key = Neuron.get_neuron_key(connect_neuron)
                    self.neurons[row_key][neuron_key][Neuron.CONNECTIONS_INDEX][connect_key] = connection_power

    def register_neuron(self, row, neuron_id, neuron):
        if row not in self.neurons:
            self.neurons[row] = {}

        self.neurons[row][neuron_id] = neuron

    def attach_neuron_power(self, neuron_key, power):
        row, col = Neuron.parse_neuron_key(neuron_key)

        current_power = self.neurons[row][col][Neuron.POWER_INDEX]

        self.set_neuron_power(neuron_key, power + current_power)

    def set_neuron_power(self, neuron_key, power, force=False):
        row, col = Neuron.parse_neuron_key(neuron_key)

        if force:
            self.neurons[row][col][Neuron.POWER_INDEX] = power
            return

        if neuron_key == "1_1":
            print("Set power [" + str(self.CURRENT_TICK) + "] " + str(power))

        if self.neurons[row][col][Neuron.POWER_INDEX] < self.BASE_POWER_LEVEL:
            return

        new_power = self.neurons[row][col][Neuron.POWER_INDEX] + power
        if new_power < self.NEURON_MIN_POWER:
            self.neurons[row][col][Neuron.POWER_INDEX] = self.NEURON_MIN_POWER
            return

        if new_power > self.NEURON_MAX_POWER:
            self.neurons[row][col][Neuron.POWER_INDEX] = self.NEURON_MAX_POWER
            return

        self.neurons[row][col][Neuron.POWER_INDEX] = power

    def append_power_to_neuron(self, neuron_key, power):
        self.attach_neuron_power(neuron_key, power)

        if self.CURRENT_TICK not in self.power_ups:
            self.power_ups[self.CURRENT_TICK] = []

        self.power_ups[self.CURRENT_TICK].append(neuron_key)

    def check_neuron_spike(self, power):
        return power > self.SPIKE_GENERATION_POWER

    def register_spike(self, spike_tick, row, neuron_id, power):
        # print("--- Register spike -> " + row + "_" + neuron_id)

        if spike_tick not in self.spike_chain:
            self.spike_chain[spike_tick] = {}

        neuron_key = Neuron.generate_neuron_key(row, neuron_id)
        if neuron_key not in self.spike_chain[spike_tick]:
            self.spike_chain[spike_tick][neuron_key] = []

        self.spike_chain[spike_tick][neuron_key].append(power)

    def proceed_spikes(self):
        if self.CURRENT_TICK not in self.spike_chain:
            return

        for location, powers in self.spike_chain[self.CURRENT_TICK].items():
            self.recalculate_neuron_power(location)

            result_power = self.spike_append_function(powers)
            self.append_power_to_neuron(location, result_power)

    def proceed_spike_resets(self):
        if self.CURRENT_TICK not in self.spike_resets:
            return

        for location in self.spike_resets[self.CURRENT_TICK]:
            new_location = Neuron.parse_neuron_key(location)
            row = new_location[0]
            col = new_location[1]

            neuron = self.neurons[row][col]
            neuron_power = neuron[Neuron.POWER_INDEX]

            self.attach_neuron_power(location, (neuron_power * -1))

    def proceed_power_ups(self):
        if self.CURRENT_TICK not in self.power_ups:
            return

        for location in self.power_ups[self.CURRENT_TICK]:
            location = Neuron.parse_neuron_key(location)
            row = location[0]
            col = location[1]

            neuron = self.neurons[row][col]
            neuron_power = neuron[Neuron.POWER_INDEX]

            has_spike = self.check_neuron_spike(neuron_power)
            if not has_spike:
                continue

            # print("-- Spike -> " + row + "_" + col)

            neuron_connections = Neuron.get_neuron_connections(neuron)
            for connection, multiplier in neuron_connections.items():
                output_power = neuron[Neuron.POWER_INDEX] * multiplier
                output_location = Neuron.parse_neuron_key(connection)

                self.register_spike(self.CURRENT_TICK + 1, output_location[0], output_location[1], output_power)

            if self.CURRENT_TICK + 1 not in self.spike_resets:
                self.spike_resets[self.CURRENT_TICK + 1] = []

            self.spike_resets[self.CURRENT_TICK + 1].append(Neuron.generate_neuron_key(row, col))

    def recalculate_neuron_power(self, neuron_key):
        row, col = Neuron.parse_neuron_key(neuron_key)
        neuron = self.neurons[row][col]

        steps_difference = self.CURRENT_TICK - neuron[Neuron.LAST_ACTIVITY_TICK]
        if steps_difference == 0:
            return

        current_neuron_power = Neuron.get_neuron_power(neuron)
        if current_neuron_power == self.BASE_POWER_LEVEL:
            return

        power_difference = self.BASE_POWER_LEVEL - current_neuron_power

        if power_difference < 0:
            potential_power_attenuate = self.NEURON_TICK_ATTENUATION_POWER * steps_difference
            if abs(power_difference) < potential_power_attenuate:
                self.set_neuron_power(Neuron.generate_neuron_key(row, col), self.BASE_POWER_LEVEL, True)
                self.neurons[row][col][Neuron.LAST_ACTIVITY_TICK] = self.CURRENT_TICK
                return

            new_power = current_neuron_power - potential_power_attenuate
            self.set_neuron_power(Neuron.generate_neuron_key(row, col), new_power, True)
            self.neurons[row][col][Neuron.LAST_ACTIVITY_TICK] = self.CURRENT_TICK
            return

        if power_difference > 0:
            potential_power_regenerate = self.NEURON_TICK_REGENERATION_POWER * steps_difference
            if abs(power_difference) > potential_power_regenerate:
                self.set_neuron_power(Neuron.generate_neuron_key(row, col), self.BASE_POWER_LEVEL, True)
                self.neurons[row][col][Neuron.LAST_ACTIVITY_TICK] = self.CURRENT_TICK
                return

            new_power = current_neuron_power - potential_power_regenerate
            self.set_neuron_power(Neuron.generate_neuron_key(row, col), new_power, True)
            self.neurons[row][col][Neuron.LAST_ACTIVITY_TICK] = self.CURRENT_TICK
            return


def spike_append_function(powers):
    res = 0
    for power in powers:
        res = res + power
    return res


def create_neuron_graph(pw, row, col):
    history = Neuron.get_neuron_power_history(pw.neurons[row][col])
    t = np.array([*history.keys()])
    t = t.astype(np.int)
    v = np.array([*history.values()])

    fig, ax = plt.subplots()
    ax.plot(
        t,
        v,
    )

    ax.grid()

    fig.savefig("test.png")
    plt.show()


pw = Main(10, 8, spike_append_function)

pw.register_spike(1, '1', '1', 41)
pw.register_spike(1, '1', '2', 41)
pw.register_spike(1, '1', '3', 41)

#pw.register_spike(7, '1', '1', 41)
#pw.register_spike(7, '1', '2', 41)
#pw.register_spike(7, '1', '3', 41)

i = 0
while i < 14:
    pw.proceed_tick()
    pw.recalculation()
    i += 1

create_neuron_graph(pw, '2', '1')
create_neuron_graph(pw, '2', '2')
create_neuron_graph(pw, '2', '3')
create_neuron_graph(pw, '2', '4')
#create_neuron_graph(pw, '4', '5')
#create_neuron_graph(pw, '2', '5')
#create_neuron_graph(pw, '6', '1')

# matplotlib.use('Agg')
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot([1,2,3])
# fig.savefig('test.png')
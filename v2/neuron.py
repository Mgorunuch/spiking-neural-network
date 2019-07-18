import threading


class Neuron:
    def __init__(self, is_brake=False, is_input=False, is_output=False, power=0, base_power=0, spike_generation_power=0, after_spike_relax_ticks=0, power_lost_per_tick=0):
        self.is_brake = is_brake
        self.is_input = is_input
        self.is_output = is_output
        self.power = power
        self.base_power = base_power
        self.spike_generation_power = spike_generation_power
        self.after_spike_relax_ticks = after_spike_relax_ticks
        self.disabled_to_tick = 0
        self.power_history = []                                 # [NeuronConnection, power, *power_history][]
        self.last_demurrage_calculation_tick = 0
        self.power_lost_per_tick = power_lost_per_tick

    def has_spike(self):
        return self.power >= self.spike_generation_power

    def get_output(self):
        if self.is_brake:
            return 1
        return -1

    def append_spike_result(self, current_tick):
        self.power = self.base_power
        self.disabled_to_tick = current_tick + self.after_spike_relax_ticks
        self.power_history = []

    def attach_power(self, current_tick, power, power_history, connection):
        if self.disabled_to_tick <= current_tick:
            return

        self.power += power
        self.power_history.append([connection, power, power_history])

    def proceed_demurrage(self, current_tick):
        if self.disabled_to_tick <= current_tick:
            self.last_demurrage_calculation_tick = current_tick
            return

        if self.power == self.base_power:
            self.power_history = []
            self.last_demurrage_calculation_tick = current_tick
            return

        if self.last_demurrage_calculation_tick >= current_tick:
            return

        left_power = self.power - self.base_power
        ticks_passed = current_tick - self.last_demurrage_calculation_tick
        potential_power_lost = ticks_passed * self.power_lost_per_tick

        if potential_power_lost >= left_power:
            self.power_history = []
            self.power = self.base_power
            return

        self.power -= potential_power_lost
        self.recursive_clear_history(potential_power_lost)

    def recursive_clear_history(self, power_lost):
        item_key = len(self.power_history) - 1
        last_history_item = self.power_history[item_key]

        if last_history_item[1] <= 0:
            self.power_history.pop()
            self.recursive_clear_history(power_lost)
            return

        if power_lost > last_history_item[1]:
            power_lost -= last_history_item[1]
            self.power_history.pop()
            self.recursive_clear_history(power_lost)
            return

        if power_lost == last_history_item[1]:
            self.power_history.pop()
            return

        self.power_history[item_key][1] -= power_lost


class NeuronConnection:
    def __init__(self, base_multiplier=1):
        self.multiplier = base_multiplier

    def increase_multiplier(self, power):
        self.multiplier += power

    def decrease_multiplier(self, power):
        self.multiplier -= power


class ResultProcessor:
    @staticmethod
    def proceed_fail(connections, value):
        for i in range(len(connections)):
            connections[i].decrease_multiplier(value)

    @staticmethod
    def proceed_success(connections, value):
        for i in range(len(connections)):
            connections[i].increase_multiplier(value)


class LetterDecodedEncoder:
    def __init__(self):
        self.letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,?'.split('')

    def encode_string(self, string):
        result = []

        for letter in string:
            for i in range(len(self.letters)):
                if letter == self.letters[i]:
                    result.append(i)
                    break

        return result

    def decode_values(self, values):
        result = []
        for value in values:
            result.append(self.letters[value])

        return result


CURRENT_TICK = 0


class NeuronThread(threading.Thread):
    def __init__(self, q, neuron):
        threading.Thread.__init__(self, args=())
        self.queue = q
        self.daemon = True
        self.neuron = neuron

    def run(self):
        i = 0

        while True:
            i += 1
            power_data = self.queue.get()   # [Connection, power, power_history]

            self.neuron.proceed_demurrage(CURRENT_TICK)
            self.neuron.attach_power(CURRENT_TICK, power_data[1], power_data[2], power_data[0])

            if self.neuron.has_spike():
                output = self.neuron.get_output()
                history = self.neuron.power_history

                self.neuron.append_spike_result(CURRENT_TICK)

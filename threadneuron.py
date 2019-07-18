import threading
import time
import queue
import random

print_lock = threading.Lock()


class NeuronConnection:
    def __init__(self, from_connection, to_connection, multiplier):
        self.from_connection = from_connection
        self.to_connection = to_connection
        self.multiplier = multiplier


class NeuronParams:
    base_power = 1000
    power_recovery_per_tick = 100
    power_lost_per_tick = 100
    spike_power = 1000
    spike_generation_power = 5000
    connections = []
    current_power = 1000
    after_spike_power = 0
    after_spike_power_lost_ticks = 1
    neuron_renew_tick = 0
    recalculation_last_tick = 0

    def get_recovery_time(self):
        return (self.base_power - self.after_spike_power) / self.power_recovery_per_tick


class NeuronThread(threading.Thread):
    neuron_params = None

    def __init__(self, q, neuron_params, processor, key="", output=False, output_function=None, kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=kwargs)
        self.queue = q
        self.daemon = True
        self.neuron_params = neuron_params
        self.history = {}
        self.is_output = output
        self.output_function = output_function
        self.processor = processor
        self.key = key

    def run(self):
        i = 0

        while True:
            i += 1
            power = self.queue.get()
            self.recalculate_power()
            if power:
                if self.neuron_params.neuron_renew_tick > self.processor.TIME_TICKER:
                    continue

                power = self.modify_input_power(power)
                self.attach_input_power_to_neuron(power)
                if self.check_is_spike():
                    self.proceed_spike()

    def recalculate_power(self):
        current_tick = self.processor.TIME_TICKER

        if self.neuron_params.recalculation_last_tick >= current_tick:
            return

        if self.neuron_params.current_power <= self.neuron_params.base_power:
            return

        need_remove_lost_power = self.neuron_params.current_power - self.neuron_params.base_power
        passed_ticks = current_tick - self.neuron_params.recalculation_last_tick
        potential_lost = passed_ticks * self.neuron_params.power_lost_per_tick

        if potential_lost > need_remove_lost_power:
            self.neuron_params.current_power = self.neuron_params.base_power

        self.neuron_params.current_power = self.neuron_params.current_power - potential_lost
        self.neuron_params.recalculation_last_tick = current_tick

    # ready
    def modify_input_power(self, power):
        return power

    # ready
    def attach_input_power_to_neuron(self, power):
        current_power = self.neuron_params.current_power + power

        if current_power < self.neuron_params.base_power:
            self.neuron_params.current_power = self.neuron_params.base_power
        else:
            self.neuron_params.current_power = current_power

        current_tick = self.processor.TIME_TICKER
        if current_tick not in self.history:
            self.history[current_tick] = []

        self.history[current_tick].append(self.neuron_params.current_power)

    # ready
    def check_is_spike(self):
        return self.neuron_params.spike_generation_power <= self.neuron_params.current_power

    def proceed_spike(self):
        power = self.neuron_params.spike_power
        power = self.modify_spike_power(power)
        self.neuron_params.current_power = self.neuron_params.after_spike_power
        self.send_power_to_inputs(power)

        current_tick = self.processor.TIME_TICKER

        power_lost_time = self.neuron_params.after_spike_power_lost_ticks

        recovery_time = self.neuron_params.get_recovery_time()

        renew_neuron_tick = current_tick + power_lost_time + recovery_time

        self.neuron_params.neuron_renew_tick = renew_neuron_tick

        self.history[current_tick + power_lost_time] = [self.neuron_params.after_spike_power]
        self.history[renew_neuron_tick] = [self.neuron_params.base_power]

    def send_power_to_inputs(self, power):
        if self.is_output:
            self.nothing()
            return
        input_power = self.modify_input_power(power)
        for conn in self.neuron_params.connections:
            input_power = conn.multiplier * input_power
            self.processor.threads[conn.to_connection].queue.put(input_power)

    def modify_spike_power(self, power):
        return power

    def nothing(self):
        self.output_function(self.key)
        return True


class NeuronProcessor:
    def start(self):
        for tr in range(len(self.threads)):
            self.threads[tr].start()

        while True:
            self.ticker_function(self.TIME_TICKER, self)

            self.TIME_TICKER += 1
            time.sleep(0.1)

    def __init__(self, inputs=0, outputs=0, seed=0, row_cols=[], output_function=None, ticker_function=None):
        random.seed(seed)
        self.threads = []
        self.TIME_TICKER = 0
        self.ticker_function = ticker_function

        for i in range(inputs):
            from_attach = 0
            to_attach = inputs
            connections = []
            for r in range(row_cols[0]):
                connections.append(
                    NeuronConnection(from_attach + i, to_attach + r, random.randint(-5, 5))
                )

            params = NeuronParams()
            params.connections = connections

            q = queue.Queue()
            self.threads.append(NeuronThread(processor=self, q=q, neuron_params=params))

        from_attach = inputs + row_cols[0]
        to_attach = inputs + row_cols[0]
        if len(row_cols) > 1:
            to_attach += row_cols[1]
        else:
            to_attach += outputs

        for rc in range(len(row_cols)):
            for i in range(row_cols[rc]):
                connections = []

                for j in range(from_attach, to_attach):
                    connections.append(
                        NeuronConnection(from_attach - (row_cols[rc] - i), j, random.randint(0, 5))
                    )

                params = NeuronParams()
                params.connections = connections

                q = queue.Queue()
                self.threads.append(NeuronThread(processor=self, q=q, neuron_params=params))

            from_attach += row_cols[rc]
            if len(row_cols) < rc + 1:
                to_attach += row_cols[rc + 1]
            else:
                to_attach += outputs

        for o in range(outputs):
            q = queue.Queue()
            params = NeuronParams()
            self.threads.append(NeuronThread(processor=self, key=str(o), q=q, neuron_params=params, output=True, output_function=output_function))

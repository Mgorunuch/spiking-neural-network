import helpers


class SpikeLogger:
    @staticmethod
    def add_spike(neuron):
        time = helpers.current_milliseconds_time()
        with open("spikes.txt", "a") as myfile:
            myfile.write(str(time) + "|" + neuron.get_raw_string_location('.') + "\n")

import helpers


class SpikeLogger:
    @staticmethod
    def add_spike(brain, neuron):
        time = brain.get_current_ms()
        with open("logs/spikes.txt", "a") as myfile:
            myfile.write(str(time) + "|" + neuron.get_raw_string_location('.') + "\n")

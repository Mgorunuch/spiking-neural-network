import helpers


class ConnectionActivityLogger:
    @staticmethod
    def log(brain, connection):
        time = brain.get_current_ms()
        with open("logs/connection_activity.txt", "a") as myfile:
            myfile.write(str(time)
                         + "|"
                         + connection.from_neuron.get_raw_string_location('.')
                         + ":"
                         + connection.to_neuron.get_raw_string_location('.')
                         + "\n")
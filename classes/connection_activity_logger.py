import helpers


class ConnectionActivityLogger:
    @staticmethod
    def log(connection):
        time = helpers.current_milliseconds_time()
        with open("connection_activity.txt", "a") as myfile:
            myfile.write(str(time)
                         + "|"
                         + connection.from_neuron.get_raw_string_location('.')
                         + "-"
                         + connection.to_neuron.get_raw_string_location('.')
                         + "\n")
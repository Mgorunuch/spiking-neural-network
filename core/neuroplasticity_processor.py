class NeuroplasticityProcessor:
    @staticmethod
    def proceed_output_plasticity(last_chain_neuron, result, depth=0):
        nl = last_chain_neuron.get_raw_string_location('.')
        last_signal = last_chain_neuron.prev_signal

        if depth > 99:
            return

        if last_signal.from_neuron is None:
            return

        last_connection = last_signal.from_neuron.connections[nl]
        if result:
            last_connection.multiplier += 1
        else:
            last_connection.multiplier -= 1

        depth += 1

        NeuroplasticityProcessor.proceed_output_plasticity(last_signal.from_neuron, result, depth)

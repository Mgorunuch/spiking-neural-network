from core import neurolocator


def generate_output_neurons_connections(
        output_neurons,
        connection_generation_remoteness,
        back_connection_generation_percent,
        create_connection_function,
        brain
):
    # Прорабатываем соединения для исходящих нейронов
    for neuron in output_neurons:
        allowed_ranges = neurolocator.Neurolocator.get_allowed_connection_ranges(
            c_x=int(neuron.location["x"]),
            c_y=int(neuron.location["y"]),
            c_z=int(neuron.location["z"]),
            remoteness=connection_generation_remoteness,
        )

        allowed_neurons = neurolocator.Neurolocator.get_allowed_neurons_in_ranges(allowed_ranges, brain.neurons)

        connections = neurolocator.Neurolocator.get_connections(
            from_neuron=neuron,
            to_neurons=allowed_neurons,
            back_generation_percent=back_connection_generation_percent,
            create_connection_function=create_connection_function
        )

        return connections
from classes import signal


brain = None
input_neurons = None
output_neurons = None
encoder = None
decoder = None

current_act = 0
wait_text = 'а'


def start_learn(br, inp, out, enc, dec):
    global brain, input_neurons, output_neurons, encoder, decoder, current_act, wait_text

    brain = br
    input_neurons = inp
    output_neurons = out
    encoder = enc
    decoder = dec

    current_act = 0
    wait_text = 'a'

    index = encoder.encode('а')[0]
    input_neurons[index].get_thread().get_queue().put(
        signal.Signal(1000)
    )


def is_output_valid(neuron):
    global decoder, wait_text

    decoded = decoder.encode(neuron.custom_key)

    return decoded == wait_text

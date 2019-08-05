import queue
from core import neurolocator, neuroplasticity_processor
from classes import neuron_connection, neuro_thread, signal, brain, neuron, location, spike_logger, connection_activity_logger
from receptors.encoders import text_message_encoder
from receptors.decoders import text_message_decoder
from receptors import decoder, encoder
import threading
import generators

lock = threading.Lock()

MAIN_X_COORD = 1
MAIN_Y_COORD = 1
MAIN_Z_FROM = 1
MAIN_Z_TO = 100

# Настройка входных нейронов
INPUT_NEURON_REMOTENESS = 10
INPUT_NEURONS_COUNT_PER_ROW = 3
INPUT_NEURONS_ROWS = 3
INPUT_COORD_OFFSET = {
    "x": MAIN_X_COORD,
    "y": MAIN_Y_COORD,
    "z": MAIN_Z_FROM,
}
INPUT_NEURON_SPIKE_ACTIVATION_POWER = 600
INPUT_NEURON_POWER_DUMPING_PER_MS = 1 / 100
INPUT_NEURON_BASE_POWER_LEVEL = 100
# Настройка соединений входных нейронов
INPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 0
INPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS = 12

# Настройка исходящих нейронов
OUTPUT_NEURON_REMOTENESS = 10
OUTPUT_NEURONS_COUNT_PER_ROW = 3
OUTPUT_NEURONS_ROWS = 3
OUTPUT_COORD_OFFSET = {
    "x": MAIN_X_COORD,
    "y": MAIN_Y_COORD,
    "z": MAIN_Z_TO,
}
OUTPUT_NEURON_SPIKE_ACTIVATION_POWER = 500
OUTPUT_NEURON_POWER_DUMPING_PER_MS = 1 / 100
OUTPUT_NEURON_BASE_POWER_LEVEL = 100
# Настройка соединений исходящих нейронов
OUTPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 100
OUTPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS = 2

# Настройка обыкновенных нейронов
BASE_NEURONS_X_REMOTENESS = 8
BASE_NEURONS_Y_REMOTENESS = 8
BASE_NEURONS_Z_REMOTENESS = 8

BASE_NEURONS_X_FROM = MAIN_X_COORD
BASE_NEURONS_Y_FROM = MAIN_Y_COORD
BASE_NEURONS_Z_FROM = MAIN_Z_FROM + BASE_NEURONS_Z_REMOTENESS

BASE_NEURONS_X_TO = BASE_NEURONS_X_FROM + BASE_NEURONS_X_REMOTENESS * 5
BASE_NEURONS_Y_TO = BASE_NEURONS_Y_REMOTENESS * 5
BASE_NEURONS_Z_TO = MAIN_Z_TO - BASE_NEURONS_Z_REMOTENESS

BASE_NEURON_SPIKE_ACTIVATION_POWER = 400
BASE_NEURON_POWER_DUMPING_PER_MS = 1 / 200
BASE_NEURON_BASE_POWER_LEVEL = 100
# Настройка соединений базовых нейронов
BASE_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 20
BASE_NEURONS_CONNECTION_GENERATION_REMOTENESS = 12


ENCODER = text_message_encoder.TextMessageEncoder()
DECODER = text_message_decoder.TextMessageDecoder()

# Проверка валидности енкодера
if isinstance(ENCODER, encoder.Encoder) is not True:
    raise Exception("ENCODER не наследник класса Encoder")

# Проверка валидности декодера
if isinstance(DECODER, decoder.Decoder) is not True:
    raise Exception("ENCODER не наследник класса Encoder")


def input_neuron_set_up_function(neuron_instance):
    neuron_instance.spike_activation_power = INPUT_NEURON_SPIKE_ACTIVATION_POWER
    neuron_instance.power_damping_ms = INPUT_NEURON_POWER_DUMPING_PER_MS
    neuron_instance.base_power_level = INPUT_NEURON_BASE_POWER_LEVEL
    neuron_instance.power = neuron_instance.base_power_level
    neuron_instance.inactive_to_ms = neuron_instance.last_activity


def output_neuron_set_up_function(neuron_instance):
    neuron_instance.spike_activation_power = OUTPUT_NEURON_SPIKE_ACTIVATION_POWER
    neuron_instance.power_damping_ms = OUTPUT_NEURON_POWER_DUMPING_PER_MS
    neuron_instance.base_power_level = OUTPUT_NEURON_BASE_POWER_LEVEL
    neuron_instance.power = neuron_instance.base_power_level
    neuron_instance.inactive_to_ms = neuron_instance.last_activity


def base_neuron_set_up_function(neuron_instance):
    neuron_instance.spike_activation_power = BASE_NEURON_SPIKE_ACTIVATION_POWER
    neuron_instance.power_damping_ms = BASE_NEURON_POWER_DUMPING_PER_MS
    neuron_instance.base_power_level = BASE_NEURON_BASE_POWER_LEVEL
    neuron_instance.power = neuron_instance.base_power_level
    neuron_instance.inactive_to_ms = neuron_instance.last_activity


def neuron_apply_signal_function(neuron_instance, input_signal, current_ms):
    if neuron_instance.inactive_to_ms > current_ms:
        return

    neuron_instance.prev_signal = input_signal
    neuron_instance.power += input_signal.power


def neuron_check_spike_function(neuron_instance, current_ms):
    return neuron_instance.power >= neuron_instance.spike_activation_power


def neuron_inactivity_function(neuron_instance, ms_passed):
    if neuron_instance.power <= neuron_instance.base_power_level:
        return

    potential_damp_power = ms_passed * neuron_instance.power_damping_ms
    can_damp_power = neuron_instance.power - neuron_instance.base_power_level
    if potential_damp_power >= can_damp_power:
        neuron_instance.power = neuron_instance.base_power_level
        return

    neuron_instance.power = neuron_instance.power - potential_damp_power


def get_spike_power_function(neuron_instance):
    return neuron_instance.base_power_level


def neuron_after_spike_function(neuron_instance, current_ms):
    neuron_instance.power = neuron_instance.base_power_level
    neuron_instance.inactive_to_ms = current_ms + 1000


def output_neuron_after_spike_function(neuron_instance, current_ms):
    with lock:
        is_valid = False
        response_result = input('Is response valid? y/n (n)')

        if response_result == 'y':
            is_valid = True

        neuroplasticity_processor.NeuroplasticityProcessor.proceed_output_plasticity(neuron_instance, is_valid)
        print("Output spike!")


def create_input_neuron_function(x, y, z):
    # Входные нейроны не будут просчитываться через функцию неактивности
    return neuron.Neuron(
        location=location.Location(
            x,
            y,
            z,
        ),
        set_up_function=input_neuron_set_up_function,
        inactivity_function=neuron_inactivity_function,
        apply_signal_function=neuron_apply_signal_function,
        check_spike_function=neuron_check_spike_function,
        current_milliseconds=0,
        before_spike_function=None,
        after_spike_function=neuron_after_spike_function,
        get_spike_power_function=get_spike_power_function,
        is_output=False,
        is_input=True,
    )


def create_output_neuron_function(x, y, z):
    # Выходные нейроны не будут просчитываться через функцию неактивности
    return neuron.Neuron(
        location=location.Location(
            x,
            y,
            z,
        ),
        set_up_function=output_neuron_set_up_function,
        inactivity_function=neuron_inactivity_function,
        apply_signal_function=neuron_apply_signal_function,
        check_spike_function=neuron_check_spike_function,
        current_milliseconds=0,
        before_spike_function=None,
        after_spike_function=output_neuron_after_spike_function,
        get_spike_power_function=get_spike_power_function,
        is_output=True,
        is_input=False,
    )


def create_base_neurons_function(x, y, z):
    return neuron.Neuron(
        location=location.Location(
            x,
            y,
            z,
        ),
        set_up_function=base_neuron_set_up_function,
        inactivity_function=neuron_inactivity_function,
        apply_signal_function=neuron_apply_signal_function,
        check_spike_function=neuron_check_spike_function,
        current_milliseconds=0,
        before_spike_function=None,
        after_spike_function=neuron_after_spike_function,
        get_spike_power_function=get_spike_power_function,
        is_output=False,
        is_input=False,
    )


# Временная переменная для хранения данных
TMP_created_connections = {}


# Функция проработки сигнала в соединении
def connection_proceed_function(connection_instance, output_signal):
    output_signal.power = output_signal.power * connection_instance.multiplier
    connection_instance.to_neuron.get_thread().get_queue().put(output_signal)


def connection_set_up_function(connection_instance):
    connection_instance.multiplier = 5


# Фунция для создания соединения
def create_connection_function(from_neuron, to_neuron):
    from_key = from_neuron.get_raw_string_location('.')
    to_key = to_neuron.get_raw_string_location('.')

    # Проверяем тыкает ли нейрон сам на себя
    if from_key == to_key:
        return None

    # Проверяем создавали ли мы такое же соединеник
    if from_key + "-" + to_key in TMP_created_connections:
        return None

    # Проверяем создавали ли мы обратное соединеник
    if to_key + "-" + from_key in TMP_created_connections:
        return None

    # Если соединений не создавали. Создаем соединение и записываем во временную переменную
    TMP_created_connections[from_key + "-" + to_key] = True
    return neuron_connection.NeuronConnection(
        from_neuron=from_neuron,
        to_neuron=to_neuron,
        proceed_function=connection_proceed_function,
        set_up=connection_set_up_function,
    )


def create_signal_function(activated_neuron, spike_power):
    prev_signal = activated_neuron.prev_signal

    return signal.Signal(power=spike_power, prev_signal=prev_signal, from_neuron=activated_neuron)


input_neurons = neurolocator.Neurolocator.create_input_neurons(
    create_neuron_function=create_input_neuron_function,
    count_per_row=INPUT_NEURONS_COUNT_PER_ROW,
    rows=INPUT_NEURONS_ROWS,
    remoteness=INPUT_NEURON_REMOTENESS,
    x_offset=INPUT_COORD_OFFSET["x"],
    y_offset=INPUT_COORD_OFFSET["y"],
    z_offset=INPUT_COORD_OFFSET["z"],
)

output_neurons = neurolocator.Neurolocator.create_output_neurons(
    create_neuron_function=create_output_neuron_function,
    count_per_row=OUTPUT_NEURONS_COUNT_PER_ROW,
    rows=OUTPUT_NEURONS_ROWS,
    remoteness=OUTPUT_NEURON_REMOTENESS,
    x_offset=OUTPUT_COORD_OFFSET["x"],
    y_offset=OUTPUT_COORD_OFFSET["y"],
    z_offset=OUTPUT_COORD_OFFSET["z"],
)

base_neurons = neurolocator.Neurolocator.create_base_neurons(
    create_neuron_function=create_base_neurons_function,
    x_from=BASE_NEURONS_X_FROM,
    x_to=BASE_NEURONS_X_TO,
    x_remoteness=BASE_NEURONS_X_REMOTENESS,
    y_from=BASE_NEURONS_Y_FROM,
    y_to=BASE_NEURONS_Y_TO,
    y_remoteness=BASE_NEURONS_Y_REMOTENESS,
    z_from=BASE_NEURONS_Z_FROM,
    z_to=BASE_NEURONS_Z_TO,
    z_remoteness=BASE_NEURONS_Z_REMOTENESS,
)

sl = None
cal = None
# sl = spike_logger.SpikeLogger()
# cal = connection_activity_logger.ConnectionActivityLogger()
br = brain.Brain(create_signal_function, sl, cal)

for nr in range(len(input_neurons)):
    br.attach_neuron(input_neurons[nr])

for nr in range(len(output_neurons)):
    br.attach_neuron(output_neurons[nr])

for nr in range(len(base_neurons)):
    br.attach_neuron(base_neurons[nr])

with open("neurons.txt", "a") as myfile:
    for neuron in input_neurons + base_neurons + output_neurons:
        myfile.write(neuron.get_raw_string_location('.') + "\n")

all_connections = []

# Прорабатываем соединения для входных нейронов
all_connections += generators.generate_neurons_connections(
    input_neurons,
    INPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    INPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
    create_connection_function,
    br,
)

# Прорабатываем соединения для основных нейронов
all_connections += generators.generate_neurons_connections(
    base_neurons,
    BASE_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    BASE_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
    create_connection_function,
    br,
)

"""
# Прорабатываем соединения для исходящих нейронов
all_connections += generators.generate_neurons_connections(
    output_neurons,
    OUTPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    OUTPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
    create_connection_function,
    br,
)
"""


with open("connections.txt", "a") as myfile:
    for connection in all_connections:
        myfile.write(
            connection.from_neuron.get_raw_string_location('.')
            + "-"
            + connection.to_neuron.get_raw_string_location('.')
            + "\n")

# Разбрасываем соединения по нейронам
for connection in all_connections:
    connection.from_neuron.attach_connection(connection)

# Создаем потоки для запуска мозга
for neuron in input_neurons + base_neurons + output_neurons:
    q = queue.Queue()
    thread = neuro_thread.NeuroThread(q, neuron, br, lock)
    neuron.set_thread(thread)

# Запускаем мозг
for neuron in input_neurons + base_neurons + output_neurons:
    neuron.register_activity(br.get_current_ms())
    neuron.get_thread().start()

# Удаляем слежебные переменные
# del all_connections
# del base_neurons
# del TMP_created_connections


for neuron in input_neurons:
    neuron.get_thread().get_queue().put(signal.Signal(10000))

# TODO: Продумать обработки нейрогенеза и нейропластичности

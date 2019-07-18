from v3.core import neurolocator
from v3.classes import neuron
from v3.classes import brain
from v3.classes import neuron_connection

MAIN_X_COORD = 0
MAIN_Y_COORD = 0
MAIN_Z_FROM = 0
MAIN_Z_TO = 500

# Настройка входных нейронов
INPUT_NEURON_REMOTENESS = 5
INPUT_NEURONS_COUNT_PER_ROW = 10
INPUT_NEURONS_ROWS = 1
INPUT_COORD_OFFSET = {
    "x": MAIN_X_COORD,
    "y": MAIN_Y_COORD,
    "z": MAIN_Z_FROM,
}
# Настройка соединений входных нейронов
INPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 0
INPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS = 15

# Настройка исходящих нейронов
OUTPUT_NEURON_REMOTENESS = 5
OUTPUT_NEURONS_COUNT_PER_ROW = 10
OUTPUT_NEURONS_ROWS = 1
OUTPUT_COORD_OFFSET = {
    "x": MAIN_X_COORD,
    "y": MAIN_Y_COORD,
    "z": MAIN_Z_TO,
}
# Настройка соединений исходящих нейронов
OUTPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 100
OUTPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS = 15

# Настройка обыкновенных нейронов
BASE_NEURONS_X_COORD = MAIN_X_COORD
BASE_NEURONS_Y_REMOTENESS = INPUT_NEURON_REMOTENESS
BASE_NEURONS_Y_FROM = MAIN_Y_COORD + BASE_NEURONS_Y_REMOTENESS
BASE_NEURONS_Y_TO = INPUT_NEURONS_COUNT_PER_ROW * INPUT_NEURON_REMOTENESS - BASE_NEURONS_Y_REMOTENESS
BASE_NEURONS_Z_REMOTENESS = 5
BASE_NEURONS_Z_FROM = MAIN_Z_FROM + BASE_NEURONS_Z_REMOTENESS
BASE_NEURONS_Z_TO = MAIN_Z_TO - BASE_NEURONS_Z_REMOTENESS
# Настройка соединений базовых нейронов
BASE_NEURONS_BACK_CONNECTION_GENERATION_PERCENT = 20
BASE_NEURONS_CONNECTION_GENERATION_REMOTENESS = 15


def create_input_neuron_function(x, y, z):
    # Входные нейроны не будут просчитываться через функцию неактивности
    return neuron.Neuron(x, y, z, None, 0)


def create_output_neuron_function(x, y, z):
    # Выходные нейроны не будут просчитываться через функцию неактивности
    return neuron.Neuron(x, y, z, None, 0)


def create_base_neurons_function(x, y, z):
    # TODO: Сделать функцию просчета ожидания
    return neuron.Neuron(x, y, z, None, 0)


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
    x_coord=BASE_NEURONS_X_COORD,
    y_from=BASE_NEURONS_Y_FROM,
    y_to=BASE_NEURONS_Y_TO,
    y_remoteness=BASE_NEURONS_Y_REMOTENESS,
    z_from=BASE_NEURONS_Z_FROM,
    z_to=BASE_NEURONS_Z_TO,
    z_remoteness=BASE_NEURONS_Z_REMOTENESS,
)

br = brain.Brain()
for nr in range(len(input_neurons)):
    br.attach_neuron(input_neurons[nr])

for nr in range(len(output_neurons)):
    br.attach_neuron(output_neurons[nr])

for nr in range(len(base_neurons)):
    br.attach_neuron(base_neurons[nr])


# Временная переменная для хранения данных
TMP_created_connections = {}


def create_connection_function(from_neuron, to_neuron):
    from_key = from_neuron.get_raw_string_location()
    to_key = to_neuron.get_raw_string_location()

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
    )


all_connections = []

# Прорабатываем соединения для входных нейронов
for neuron in input_neurons:
    allowed_ranges = neurolocator.Neurolocator.get_allowed_connection_ranges(
        c_x=int(neuron.location["x"]),
        c_y=int(neuron.location["y"]),
        c_z=int(neuron.location["z"]),
        remoteness=INPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    )
    allowed_neurons = neurolocator.Neurolocator.get_allowed_neurons_in_ranges(allowed_ranges, br.neurons)

    connections = neurolocator.Neurolocator.get_connections(
        from_neuron=neuron,
        to_neurons=allowed_neurons,
        back_generation_percent=INPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
        create_connection_function=create_connection_function
    )

    all_connections = all_connections + connections

# Прорабатываем соединения для основных нейронов
for neuron in base_neurons:
    allowed_ranges = neurolocator.Neurolocator.get_allowed_connection_ranges(
        c_x=int(neuron.location["x"]),
        c_y=int(neuron.location["y"]),
        c_z=int(neuron.location["z"]),
        remoteness=BASE_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    )
    allowed_neurons = neurolocator.Neurolocator.get_allowed_neurons_in_ranges(allowed_ranges, br.neurons)

    connections = neurolocator.Neurolocator.get_connections(
        from_neuron=neuron,
        to_neurons=allowed_neurons,
        back_generation_percent=BASE_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
        create_connection_function=create_connection_function
    )

    all_connections = all_connections + connections

# Прорабатываем соединения для исходящих нейронов
for neuron in output_neurons:
    allowed_ranges = neurolocator.Neurolocator.get_allowed_connection_ranges(
        c_x=int(neuron.location["x"]),
        c_y=int(neuron.location["y"]),
        c_z=int(neuron.location["z"]),
        remoteness=OUTPUT_NEURONS_CONNECTION_GENERATION_REMOTENESS,
    )
    allowed_neurons = neurolocator.Neurolocator.get_allowed_neurons_in_ranges(allowed_ranges, br.neurons)

    connections = neurolocator.Neurolocator.get_connections(
        from_neuron=neuron,
        to_neurons=allowed_neurons,
        back_generation_percent=OUTPUT_NEURONS_BACK_CONNECTION_GENERATION_PERCENT,
        create_connection_function=create_connection_function
    )

    all_connections = all_connections + connections

# Разбрасываем соединения по нейронам
for connection in all_connections:
    connection.from_neuron.attach_connection(connection)

# Удаляем слежебные переменные
del all_connections
del base_neurons
del TMP_created_connections

print(br)

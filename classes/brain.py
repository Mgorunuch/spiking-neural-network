import helpers
from classes import signal
import threading

print_lock = threading.Lock()


class Brain:
    """
    Класс создан для работы с нейронами.
    Является основной единицой для хранения данных.
    """

    def __init__(self, spike_logger=None):
        self.spike_logger = spike_logger

    neurons = {}

    def get_current_ms(self):
        return helpers.current_milliseconds_time()

    def attach_neuron(self, neuron):
        """
        :param neuron: v3.classes Neuron
        :return: none
        """
        loc = neuron.get_raw_string_location(".")

        helpers.attach_to_dict_by_key(self.neurons, loc, neuron)

    def detach_neuron(self, neuron):
        """
        :param neuron: v3.classes Neuron
        :return: None
        """
        loc = neuron.get_raw_string_location(".")

        helpers.detach_from_dict_by_key(self.neurons, loc)

    def thread_run(self, neuro_thread, input_signal):
        """
        Функция итерации треада

        :param neuro_thread: v3.NeuroThread
        :param input_signal: v3.Signal
        :return: None
        """

        # Вспомогательные переменные
        neuron = neuro_thread.neuron
        current_ms = self.get_current_ms()

        # Просчитываем неактивность нейрона
        ms_passed = current_ms - neuron.get_last_activity()
        neuron.proceed_inactivity(ms_passed)

        # Применяем входящий сигнал
        neuron.apply_input_signal(input_signal, current_ms)

        # Проверяем спайк
        has_spike = neuron.has_spike(current_ms)
        if has_spike is True:
            # Начинаем работу со спайком
            neuron.before_spike(current_ms)

            spike_power = neuron.get_spike_power()
            output_signal = signal.Signal(spike_power)

            connections = neuron.connections.values()

            # Начнаем отправлять сигналы в связвнные нейроны
            for connection in connections:
                # Просчитываем неактивность и отправляем данные в сигнал
                conn_ms_passed = connection.get_last_activity()
                connection.proceed_inactivity(conn_ms_passed)

                connection.proceed(output_signal)

                # Регистрируем активность в соединении
                connection.register_activity(current_ms)

            if self.spike_logger is not None:
                with print_lock:
                    self.spike_logger.add_spike(neuron)

            # Заканчиваем работу со спайком
            neuron.after_spike(current_ms)

            # Записываем в нейрон информацию о последней активности
            neuron.register_activity(current_ms)

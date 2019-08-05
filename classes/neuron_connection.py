import threading

print_lock = threading.Lock()


class NeuronConnection:
    def __init__(
            self,
            from_neuron=None,
            to_neuron=None,
            proceed_function=None,
            set_up=None,
            before_proceed_function=None,
            after_proceed_function=None,
            inactivity_function=None,
            current_milliseconds=0,
    ):
        """
        :param from_neuron: От какого нейрона идет сигнал Neuron
        :param to_neuron: До какого нейрона идет сигнал Neuron
        :param proceed_function: REQUIRED! Основная функция обработки сигнала
        :param set_up: Функция которая создана для модификации класса соединения
        :param before_proceed_function: Функция запускающаяся после перез запуском основной функции
        :param after_proceed_function: Функция запускающаяся после запуска основной функции
        :param inactivity_function: Функция просчета неактивности
        :param current_milliseconds: Текущее время
        """
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.proceed_function = proceed_function
        self.before_proceed_function = before_proceed_function
        self.after_proceed_function = after_proceed_function
        if set_up is not None:
            set_up(self)
        self.inactivity_function = inactivity_function
        self.last_activity = current_milliseconds

    def proceed_inactivity(self, milliseconds_passed):
        """
        Функция предназначена для модификации на основе времени неактивности

        :param milliseconds_passed: Пройдено миллисекунд с последней активности
        :return: None
        """
        if self.inactivity_function is not None:
            self.inactivity_function(milliseconds_passed)

    def register_activity(self, current_ms):
        """
        Функция преднаначена для записи последней активности. Вызывается автоматически.

        :param current_ms: текущее время в ms
        :return: None
        """
        self.last_activity = current_ms

    def get_last_activity(self):
        """
        Функция преднаначена для получения времени последней активноти

        :return: int
        """
        return self.last_activity

    def proceed(self, signal):
        """
        :param signal: класс v3.Signal
        :return: None

        Симуляция синаптического соединения
        """
        self.before_proceed(signal)

        if self.proceed_function is not None:
            self.proceed_function(self, signal)

        self.after_proceed(signal)

    def before_proceed(self, signal):
        """
        :param signal: класс v3.Signal
        :return: None

        Симуляция пресинаптической мембраны
        """
        if self.before_proceed_function is not None:
            self.before_proceed_function(self, signal)

    def after_proceed(self, signal):
        """
        :param signal: класс v3.Signal
        :return: None

        Симуляция пост синаптической мембраны
        """
        if self.after_proceed_function is not None:
            self.after_proceed_function(self, signal)

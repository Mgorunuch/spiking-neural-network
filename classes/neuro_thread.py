import threading


class NeuroThread(threading.Thread):
    def __init__(self, queue, neuron, brain):
        threading.Thread.__init__(self, args=())
        self.queue = queue
        self.daemon = True
        self.neuron = neuron
        self.brain = brain

    def get_queue(self):
        return self.queue

    def run(self):
        while True:
            # Получаем сигнал
            input_signal = self.queue.get()
            self.brain.thread_run(self, input_signal)

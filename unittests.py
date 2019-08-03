import unittest
import helpers
from classes.brain import Brain
from classes.neuron import Neuron
from classes.neuron_connection import NeuronConnection
from classes.signal import Signal


class TestHelperMethods(unittest.TestCase):

    def test_attach_dict(self):
        a = {}
        helpers.attach_to_dict_by_key(a, "a.b", 1)
        self.assertEqual(a, {"a": {"b": 1}})

    def test_detach_dict(self):
        a = {"a": {"b": 10}}
        helpers.detach_from_dict_by_key(a, "a.b")
        self.assertEqual(a, {"a": {}})

    def test_get_from_dict(self):
        a = {"a": {"b": 1}}
        res = helpers.get_from_dict_by_key(a, "a.b", 2)
        self.assertEqual(res, 1)

    def test_get_from_dict_default(self):
        a = {"a": {"b": 1}}
        res = helpers.get_from_dict_by_key(a, "a.c", 2)
        self.assertEqual(res, 2)


class TestBrainMethods(unittest.TestCase):

    def test_attach_neuron(self):
        neuron = Neuron(1, 1, 1)
        brain = Brain()
        brain.attach_neuron(neuron)

        res = helpers.get_from_dict_by_key(brain.neurons, "1.1.1", 0)

        self.assertNotEqual(res, 0)

    def test_detach_neuron(self):
        neuron = Neuron(1, 1, 1)
        brain = Brain()
        brain.attach_neuron(neuron)
        brain.detach_neuron(neuron)

        res = helpers.get_from_dict_by_key(brain.neurons, "1.1.1", 0)

        self.assertEqual(res, 0)


class TestNeuronConnection(unittest.TestCase):

    def test_before_proceed(self):
        nc = NeuronConnection(before_proceed_function=lambda conn, signal: signal.set_power(10))
        s = Signal(20)

        nc.proceed(s)

        self.assertEqual(s.power, 10)

    def test_proceed(self):
        nc = NeuronConnection(proceed_function=lambda conn, signal: signal.set_power(10))
        s = Signal(20)

        nc.proceed(s)

        self.assertEqual(s.power, 10)

    def test_after_proceed(self):
        nc = NeuronConnection(after_proceed_function=lambda conn, signal: signal.set_power(10))
        s = Signal(20)

        nc.proceed(s)

        self.assertEqual(s.power, 10)


if __name__ == '__main__':
    unittest.main()
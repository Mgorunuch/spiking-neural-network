import threadneuron

letters = [
    'а',
    'б',
    'в',
    'г',
    'д',
    'е',
    'ё',
    'ж',
    'з',
    'и',
    'й',
    'к',
    'л',
    'м',
    'н',
    'о',
    'п',
    'р',
    'с',
    'т',
    'у',
    'ф',
    'х',
    'ц',
    'ч',
    'ш',
    'щ',
    'ъ',
    'ы',
    'ь',
    'э',
    'ю',
    'я',
    ' ',
    '.',
    ',',
    '?',
]


def encode_string(string):
    encoded_numbers = []
    for ecLetter in string:
        for i in range(len(letters)):
            letter_lib = letters[i]
            if ecLetter == letter_lib:
                encoded_numbers.append(i)

    return encoded_numbers


encoded_string = encode_string('привет.')


def output_function(key):
    print(letters[int(key)])


def ticker_function(tick, np):
    if tick < len(encoded_string):
        val = encoded_string[tick]
        np.threads[val].queue.put(10000, False)


np = threadneuron.NeuronProcessor(len(letters), len(letters), 3, [5], output_function, ticker_function)
np.start()


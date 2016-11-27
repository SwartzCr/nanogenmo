import collections
import operator
import bisect
import json
import random

def build(fi):
    pairs = collections.defaultdict(list)
    for line in fi:
        line = line.lstrip()
        freq, a, b, c = line.split()
        key = ' '.join((a, b))
        pairs[key].append(c + ':' + freq)
    return pairs

def save_built_array(ar):
    out = open("squeezedarray", 'w')
    for key in sorted(ar.keys()):
        out.write('%s|%s\n' % (key, ' '.join(ar[key])))

def gen_sentence(pairs, start="BEGIN", first="BEGIN", first_word_freqs=None, word_len=0):
    if start=="BEGIN" and first_word_freqs:
        start = choose_next_word(first_word_freqs[0], first_word_freqs[1])
    second = start
    sentence = []
    if second != "BEGIN":
        sentence.append(second)
    while second != "END":
        choices, freqs = get_next_word(pairs, first, second)
        next_word = choose_next_word(choices, freqs)
        while next_word == "END" and len(sentence) < word_len:
            if len(choices) > 1:
                next_word = choose_next_word(choices, freqs)
            else:
                break
        first = second
        second = next_word
        if second != "END":
            sentence.append(second)
    return sentence

def accumulate(iterable, func=operator.add):
        it = iter(iterable)
        word, total = next(it)
        total = int(total)
        yield word, total
        for word, numb in it:
            total = func(total, int(numb))
            yield word, total

def wrapper(options):
    out = [[],[]]
    for word, total in accumulate(gen_option_split(options)):
        out[0].append(word)
        out[1].append(total)
    return out

def gen_option_split(options):
    for option in options:
        yield option.rsplit(":", 1)

def get_next_word(pairs, first, second):
    options = pairs[(first+" "+ second)]
    return wrapper(options)

def choose_next_word(choices, freqs):
    r = random.random() * freqs[-1]
    return choices[bisect.bisect(freqs, r)]

def gen_len_sentence(length, pairs, start="BEGIN", first_word_freqs=None):
    try:
        if start not in first_word_freqs[0]:
            start = "BEGIN"
        sentence = [start]
        my_length = length
        if start == "BEGIN":
            my_length = length + 1
        sentence = gen_sentence(pairs, start=sentence[-1], first_word_freqs=first_word_freqs)
        while len(sentence) < my_length:
            seed = sentence[-1]
            possibilities = pairs["BEGIN "+seed]
            if len(possibilities) == 1 and possibilities[0].startswith("END"):
                seed = "BEGIN"
            follow = gen_sentence(pairs, start=sentence[-1], first_word_freqs=first_word_freqs, word_len=length)
            sentence.extend(follow[1:])
        if sentence[0] == "BEGIN":
            sentence.pop(0)
        return " ".join(sentence)
    except IndexError:
        return gen_len_sentence(length, pairs, start=start, first_word_freqs=first_word_freqs)

def gen_pairs_from_my_file(filename):
    with open(filename, 'r') as f:
        pairs = build(f)
    return pairs

def load_book(filep):
    with open(filep, 'r') as f:
        return json.load(f)

def format_sentence_seeds(book_model):
    out = []
    for section in book_model:
        for sentence in section[1]:
            if sentence:
                out.append((sentence.split()[0], len(sentence.split())))
    return out

replacements = {"dont": "don't",
                "cant": "can't",
                "i": "I",
                "im": "I'm",
                "wont": "won't",
                "aint": "ain't",
                "couldve": "could've",
                "didnt": "didn't",
                "hadnt": "hadn't",
                "havent": "haven't",
                "howd": "how'd",
                "ive": "I've",
                "isnt": "isn't",
                "itll": "it'll",
                "mustve": "must've",
                "shouldnt": "shouldn't",
                "thatll": "that'll",
                "theyd" : "they'd",
                "wed": "we'd",
                "weve": "we've",
                "wholl": "who'll",
                "wouldve": "would've",
                "youd": "you'd",
                "theyre": "they're",
                "youre": "you're",
                "youll": "you'll",
                "youve": "you've",
                "doesnt": "doesn't"}

def format_sentence(sentence):
    sentence = sentence.split()
    for idx, word in enumerate(sentence):
        if replacements.get(word):
            sentence[idx] = replacements[word]
    sentence[0] = sentence[0].capitalize()
    sentence = " ".join(sentence)
    return sentence

def make_book(book_model, sentence_seeds, pairs, choices):
    out = ""
    for section in book_model:
        out += "#"+section[0]+"\n\n"
        for i in range(len(section[1])*10):
            start, length = random.choice(sentence_seeds)
            if length > 15 or length < 8:
                length = random.choice(range(8,15))
            sentence = gen_len_sentence(length, pairs, start=start, first_word_freqs=choices)
            formatted_sentence = format_sentence(sentence)
            out += formatted_sentence + ". "
        out += "\n\n"
    return out

def main():
    pairs = gen_pairs_from_my_file("numebered_full_tris")
    book_model = load_book("book_structure")
    sentence_seeds = format_sentence_seeds(book_model)
    choices = get_next_word(pairs, "BEGIN", "BEGIN")
    book = ""
    book = make_book(book_model, sentence_seeds, pairs, choices)
    with open("book.md", 'w') as f:
        f.write(book)

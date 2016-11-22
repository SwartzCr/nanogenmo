import collections
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

def gen_sentence(pairs, start="BEGIN", first_word_freqs=None):
    first = "BEGIN"
    if start=="BEGIN" and first_word_freqs:
        start = random.choice(first_word_freqs)
    second = start
    sentence = []
    if second != "BEGIN":
        sentence.append(second)
    while second != "END":
        choices = get_next_word(pairs, first, second)
        next_word = random.choice(choices)
        first = second
        second = next_word
        if second != "END":
            sentence.append(second)
    return sentence

def get_next_word(pairs, first, second):
    options = pairs[(first+" "+ second)]
    choices = []
    for option in options:
        word, freq = option.rsplit(":", 1)
        for i in range(int(freq)):
            choices.append(word)
    return choices

def gen_len_sentence(length, pairs, start="BEGIN", first_word_freqs=None):
    try:
        if start not in first_word_freqs:
            start = "BEGIN"
        sentence = [start]
        my_length = length
        if start == "BEGIN":
            my_length = length + 1
        while len(sentence) < my_length:
            follow = gen_sentence(pairs, start=sentence[-1], first_word_freqs=first_word_freqs)
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
    with open(filep, 'r'):
        return json.load(filep)

def format_sentence_seeds(book_model):
    out = []
    for section in book_model:
        out.append((section[1].split()[0], len(section[1].split())))
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
    sentence = " ".join(sentence)
    return sentence.capitalize()

def make_book(book_model, sentence_seeds, pairs, choices):
    out = ""
    for section in book_model:
        out.append("#"+section[0]+"\n\n")
        for i in range(len(section[1])*10):
            start, length = random.choice(sentence_seeds)
            sentence = gen_len_sentence(length, pairs, start=start, first_word_freqs=choices)
            formatted_sentence = format_sentence(sentence)
            out.append(formatted_sentence + ". ")
        out.append("\n\n")
    return out

def main():
    pairs = gen_pairs_from_my_file("numebered_full_tris")
    book_model = load_book("book_structure")
    sentence_seeds = format_sentence_seeds(book_model)
    choices = get_next_word(pairs, "BEGIN", "BEGIN")
    book = make_book(book_model, sentence_seeds, pairs, choices)
    with open("book.md", 'w') as f:
        f.write(book)

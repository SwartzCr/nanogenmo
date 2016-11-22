import collections
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
        temp_start = start
        while len(sentence) < my_length:
            follow = gen_sentence(pairs, start=temp_start, first_word_freqs=first_word_freqs)
            sentence.extend(follow[1:])
            for i in range(len(sentence)-1, -1, -1):
                if sentence[i] in first_word_freqs:
                    temp_start = sentence[i]
                    sentence = sentence[:i+1]
                    break
        if sentence[0] == "BEGIN":
            sentence.pop(0)
        return " ".join(sentence)
    except IndexError:
        return gen_len_sentence(length, pairs, start=start, first_word_freqs=first_word_freqs)

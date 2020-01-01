import re


class WordEntropyScore(object):
    ''' A class to calculate a string's score based on word entropy.

    Word entropy is similar to information entropy in information theory.
    It equals to sum(p * log p) over all words in the string where p is probability of a word.
    The word probability comes from existing statistics in word_entropy.csv.

    Attributes
    ----------
    _entropy_dict : Dictionary
        A dictionary of probabilities for each word.
    '''

    def __init__(self):
        self._entropy_dict = {}
        # Read word entropies from file and store them into dict.
        with open('word_entropy.csv', 'r') as input_file:
            input_file.readline()
            for line in input_file:
                word, entropy = line.split(',')
                entropy = float(entropy)
                self._entropy_dict[word] = entropy

    def calculate_score(self, text_content):
        word_cnt = {}
        for word in text_content.split():
            word = word.lower()
            word = re.sub(r'[^a-z\ \']+', "", word)
            if word in word_cnt:
                word_cnt[word] += 1
            else:
                word_cnt[word] = 1

        return sum(cnt * self._entropy_dict.get(word, 0)
                   for word, cnt in word_cnt.items())

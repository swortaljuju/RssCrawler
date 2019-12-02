class WordEntropyScore(object):
    def __init__(self):
        self._entropy_dict = {}
        with open('word_entropy.csv','r') as input_file:
            for line in input_file:
                word, entropy = line.split(',')
                entropy = float(entropy)
                self._entropy_dict[word] = entropy

    def calculateScore(self, text_content):
        word_cnt = {}
        for word in text_content.split():
            word = word.lower()
            word = re.sub('[^a-z\ \']+', "", word)
            if word in word_cnt:
                word_cnt[word] += 1
            else:
                word_cnt[word] = 1
    
        return sum(cnt * self._entropy_dict.get(word, 0) for word, cnt in word_cnt.items())                    
            
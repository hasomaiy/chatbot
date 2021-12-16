from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
import re
from nltk.tag import pos_tag

class prop:


    def preliminary_processing(self, sentence, loaction1):
        div_sentence = self.get_uip(sentence)
        div_sentence = div_sentence.lower()
        words=self.loadSpellCheck(loaction1)
        div_sentence = self.iterate_spell(div_sentence,words)
        temp_list = []
        lmtzr = WordNetLemmatizer()

        input_str = \
            self.semantic_restructure(div_sentence.lower())
        if input_str:
            input_str = input_str
        else:
            input_str = div_sentence
        input_str = input_str.split()
        for q in input_str:
            temp_list.append(lmtzr.lemmatize(q))
        input_str = sorted(temp_list)
        input_str = ' '.join(input_str)
        input_str = self.remove_single_letters(input_str,loaction1)
        input_str = input_str.upper()
        preliminary_processing_result = {"div_sentence": div_sentence,
                                         "input_str": input_str}
        return preliminary_processing_result



    ## Removes all special characters, symbols and punctuations
    def get_uip(self, sentence):
        sentence = sentence.replace('?', '')
        sentence = sentence.replace('', '')
        sentence = sentence.replace(':', '')
        sentence = sentence.replace(',', '')
        sentence = sentence.replace('-', '')
        sentence = sentence.replace('_', '')
        sentence = sentence.replace('(', '')
        sentence = sentence.replace(')', '')
        sentence = sentence.replace('.', '*$')
        sentence = sentence.replace(';', '')
        userinput2 = sentence
        return userinput2

    ## Removing unnecessary words (Optional and may differ from Bot to Bot
    def remove_single_letters(self, sentence,path):
        try:

            location_remove_words = path + '/Remove_Words/remove_words2.txt'

            stop = set(open(location_remove_words).read().split())
            sent = [i for i in sentence.lower().split() if i not in stop]
            sent = ' '.join(sent)
            sent_to_compare = sent.split(" ")

            if (len(sent_to_compare) == 0):
                location_remove_words = path + '/Remove_Words/remove_words.txt'
                stop = set(open(location_remove_words).read().split())
                sent = [i for i in sentence.lower().split() if i not in stop]
                sent = ' '.join(sent)

        except:
            location_remove_words = path + '/remove_words.txt'
            stop = set(open(location_remove_words).read().split())
            sent = [i for i in sentence.lower().split() if i not in stop]
            sent = ' '.join(sent)

        return sent



    def words(self, text):
        return re.findall(r'\w+', text.lower())

    def redFiles(self, path):
        self.WORDS = Counter(self.words(open(path).read()))

    def getWords(self):
        return self.WORDS

    def getCount(self):
        return sum(self.words.values())

    def P(self, word, N=0):
        '''Probability of `word`.'''

        N = self.getCount()
        return self.words[word] / N

    def correction(self, word):
        '''Most probable spelling correction for word.'''

        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        '''Generate possible spelling corrections for word.'''

        return self.known([word]) or self.known(self.edits1(word)) \
               or self.known(self.edits2(word)) or [word]

    def known(self, word):
        '''The subset of `words` that appear in the dictionary of WORDS.'''

        return set(w for w in word if w in self.words)

    def edits1(self, word):
        '''All edits that are one edit away from `word`.'''
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for (L, R) in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for (L, R) in splits
                      if len(R) > 1]
        replaces = [L + c + R[1:] for (L, R) in splits if R for c in
                    letters]
        inserts = [L + c + R for (L, R) in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        '''All edits that are two edits away from `word`.'''
        return (e2 for e1 in self.edits1(word) for e2 in
                self.edits1(e1))

    def spell_check(self, input_message):
        return self.correction(input_message)

    def iterate_spell(self, div_input, WORDS):
        self.words = WORDS
        myip = div_input
        myip3 = []
        myip4 = []
        myip2 = myip.split()
        for i in range(0, len(myip2)):
            myip3 = self.correction(''.join(myip2[i])).split()
            myip4 = myip4 + myip3

        correct_spelling = ' '.join(myip4)

        return correct_spelling


    def loadSpellCheck(self, path):
        loaction = path + '/spell_correcter.txt'
        self.redFiles(loaction)
        return self.getWords()

    def redFiles(self, path):
        self.WORDS = Counter(self.words(open(path).read()))

    def getWords(self):
        return self.WORDS

    def semantic_restructure(self, text):
        ts = pos_tag(text.split())
        vb = [word for (word, pos) in ts if pos == 'VB']
        vb = ' '.join(vb)
        vbd = [word for (word, pos) in ts if pos == 'VBD']
        vbd = ' '.join(vbd)
        vbg = [word for (word, pos) in ts if pos == 'VBG']
        vbg = ' '.join(vbg)
        vbn = [word for (word, pos) in ts if pos == 'VBN']
        vbn = ' '.join(vbn)
        vbp = [word for (word, pos) in ts if pos == 'VBP']
        vbp = ' '.join(vbp)
        jj = [word for (word, pos) in ts if pos == 'JJ']
        jj = ' '.join(jj)
        jjr = [word for (word, pos) in ts if pos == 'JJR']
        jjr = ' '.join(jjr)
        jjs = [word for (word, pos) in ts if pos == 'JJS']
        jjs = ' '.join(jjs)
        vbz = [word for (word, pos) in ts if pos == 'VBZ']
        vbz = ' '.join(vbz)
        nns = [word for (word, pos) in ts if pos == 'NNS']
        nns = ' '.join(nns)
        nnp = [word for (word, pos) in ts if pos == 'NNP']
        nnp = ' '.join(nnp)
        nnps = [word for (word, pos) in ts if pos == 'NNPS']
        nnps = ' '.join(nnps)
        nn = [word for (word, pos) in ts if pos == 'NN']
        nn = ' '.join(nn)
        cd = [word for (word, pos) in ts if pos == 'CD']
        cd = ' '.join(cd)
        rb = [word for (word, pos) in ts if pos == 'RB']
        rb = ' '.join(rb)
        wdt = [word for (word, pos) in ts if pos == 'WDT']
        wdt = ' '.join(wdt)
        wp = [word for (word, pos) in ts if pos == 'WP']
        wp = ' '.join(wp)
        wrb = [word for (word, pos) in ts if pos == 'WRB']
        wrb = ' '.join(wrb)

        div_input = vb + ' ' + vbd + ' ' + vbg + ' ' + vbn + ' ' + vbp \
                    + ' ' + vbz + ' ' + jj + ' ' + jjr + ' ' + jjs + ' ' + nns + ' ' + nnp + ' ' + nnps + ' ' + nn \
                    + ' ' + cd + ' ' + rb + ' ' + wdt + ' ' + wp + ' ' + wrb
        div_input = ' '.join(div_input.split())
        div_input = div_input.split(" ")
        temp_inp = []

        for i in div_input:
            if i not in temp_inp:
                temp_inp.append(i)

        div_input = " ".join(temp_inp)
        return div_input









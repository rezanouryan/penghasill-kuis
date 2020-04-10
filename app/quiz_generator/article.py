import wikipedia as wiki
import nltk
from nltk.tokenize import sent_tokenize
import re

import requests
from bs4 import BeautifulSoup

import text_to_num as t2n
from .quiz import Quiz
from .question_sentence import QuestionSentence
from math import floor
from random import random, shuffle

T2N_LANG = 'en'


def dbpedia(q):
    q = q.replace(' ', '_')
    url = 'http://dbpedia.org/page/{}'.format(q)
    r = requests.get(url)
    if r.status_code != 200:
        return None

    contents = r.content.decode('utf8')
    soup = BeautifulSoup(contents, 'lxml')

    try:
        abstract = soup.find('span', attrs={
            "xml:lang": "en",
            "property": "dbo:abstract"
        })

        text = abstract.text
        return text
    except Exception as e:
        print(str(e))
        return None


class Article():

    def __init__(self, name):
        self.name = name

        self.page = dbpedia(name)
        if self.page == None:
            return

        self.quiz = Quiz([])

        self.generate_questions_for(self.page.encode('utf8'))

    ''' 
    NOT CURRENTLY USED, but maye be useful at a later point when knowing the
    section a question was sourced from might be of use.
    '''
    # def iterate_sections(self):
    #     # Iterate through article's sections
    #     for section in self.page.sections:
    #         print section
    #         sec = self.page.section(section).encode('ascii', 'ignore')
    #         if sec is None:
    #             continue
    #         self.generate_questions_for(sec)

    '''
    tokenizes and chunks a sentence based on a simple grammar
    '''

    def get_question_data(self, s):
        tokens = nltk.word_tokenize(s)
        tagged = nltk.pos_tag(tokens)
        grammar = """  
                    NUMBER: {<$>*<CD>+<NN>*}
                    LOCATION: {<IN><NNP>+<,|IN><NNP>+} 
                    PROPER: {<NNP|NNPS><NNP|NNPS>+}
                    """
        #
        # HIT!: {<PROPER><NN>?<VBZ|VBN>+}
        # DATE: {<IN>(<$>*<CD>+<NN>*)}

        chunker = nltk.RegexpParser(grammar)
        result = chunker.parse(tagged)
        return result

    '''
    splits a Wikipedia section into sentences and then chunks/tokenizes each
    sentence
    '''

    def generate_questions_for(self, sec):
        # Rid of all parentheses for easier processing
        _sec = "".join(re.split('\(',
                                sec.decode("utf-8").replace(")", "("))[0::2])

        print(_sec)

        for sentence in sent_tokenize(_sec):
            qdata = self.get_question_data(sentence)
            if len(qdata) >= 75 and len(qdata) <= 150:
                qdata = []

            self.create_questions(sentence, qdata)

    '''
    given a setence in chunked and original form, produce the params necessary
    to create a Question, and then add that to our Quiz object
    '''

    def create_questions(self, sentence, chunked):
        gaps = []

        for word in chunked:
            if type(word) != tuple:
                target = []
                for y in word:
                    target.append(y[0])
                orig_phrase = " ".join(target)

                if word.label() == "NUMBER":
                    modified_phrase = orig_phrase[:]

                    try:
                        # convert spelled out word to numerical value
                        modified_phrase = t2n.text2num(
                            modified_phrase, lang=T2N_LANG)
                    except:
                        try:
                            test = int(modified_phrase) + \
                                float(modified_phrase)
                        except:
                            # if the word could not be converted and
                            # was not already numerical, ignore it
                            continue

                    if self.probably_range(modified_phrase):
                        return

                    gaps.append((word.label(), orig_phrase, modified_phrase))
                elif word.label() in ["LOCATION", "PROPER"]:
                    gaps.append((word.label(), orig_phrase, orig_phrase))

        if len(gaps) >= 1 and len(gaps) == len(set(gaps)):

            gaps_filtered = [gap for gap in gaps if gap[0]
                             == 'NUMBER' or gap[0] == 'LOCATION']

            if len(gaps_filtered):
                self.quiz.add(QuestionSentence(sentence, gaps_filtered))

    '''
    Wikipedia returns non-hyphenated number ranges, so we need to check for mushed together years
    and remove them. Not a complete solution to the problem, but most of the incidents are years
    '''

    def probably_range(self, val):
        s = str(val)
        if s.count("19") > 1 or s.count("20") > 1 or (s.count("19") == 1 and s.count("20") == 1):
            return True
        return False


def get_random_int(min, max):
    return (floor(random() * (max-min+1)) + min)


def get_wrong_answer(label, correct_answer, other_gaps, gap_index):

    def is_year(num):
        return num >= 1400 and num < 2050

    def clean_up(num_as_str):
        return str(num_as_str).replace(",", "").replace("S", "")

    def pos_or_neg():
        i = get_random_int(0, 2)
        return (1 if i > 0 else -1)

    if label == 'PROPER':
        return other_gaps[floor(random) * len(other_gaps)][1]
    else:
        num_as_str = clean_up(correct_answer)
        num = int(num_as_str)
        if str(num) == num_as_str:
            if is_year(num):
                lower_bound = num - 50
                for i in range(gap_index):
                    to_compare = int(clean_up(other_gaps[i][2]))
                    if is_year(to_compare) and to_compare > lower_bound:
                        lower_bound = to_compare + 1

                upper_bound = num + 30
                for i in range(gap_index+1, len(other_gaps)):
                    to_compare = int(clean_up(other_gaps[i][2]))
                    if is_year(to_compare) and to_compare < upper_bound:
                        upper_bound = to_compare - 1

                if upper_bound - lower_bound < 4:
                    raise ValueError("Range to small")

                generated = num + get_random_int(1, 10) * pos_or_neg()
                generated = min(upper_bound, generated)
                generated = max(lower_bound, generated)

                if num <= 2017:
                    return min(generated, 2017)

                return generated
            to_ret = int(
                max(0, num + (get_random_int(num * .01, num * 2) * pos_or_neg())))
            if to_ret > 30 and to_ret < 45:
                to_ret = 31
            return to_ret
        else:
            return float(num_as_str) + (float(num_as_str) * .01 * pos_or_neg())


def get_wrong_answers(label, correct_answer, other_gaps, gap_index):
    MAX_RETRIES = 20
    wrong_1 = str(get_wrong_answer(label, correct_answer, other_gaps, gap_index))
    wrong_2 = str(get_wrong_answer(label, correct_answer, other_gaps, gap_index))
    any_answer_same = None
    for i in range(MAX_RETRIES):
        any_answer_same = (wrong_1 == wrong_2) or (
            wrong_1 == correct_answer) or (wrong_2 == correct_answer)

        if not any_answer_same:
            break

        wrong_1 = str(get_wrong_answer(label, correct_answer, other_gaps, gap_index))
        wrong_2 = str(get_wrong_answer(label, correct_answer, other_gaps, gap_index))

    if (any_answer_same):
        to_ret = [str(int(wrong_1) + 1), str(int(wrong_2) - 1)]
        return to_ret

    return [wrong_1, wrong_2]


def convert_to_redacted(text, answer, label):
    from re import sub
    _answer = str(answer).replace(' ,', ',')

    if label == 'NUMBER':
        _answer = re.sub(r'/[^0-9.,]/g', '', str(_answer))
        if _answer == "":
            _answer = answer

    redacted = text.replace(_answer, "_____")
    redacted_ans = _answer
    return (redacted, redacted_ans)


def get_question_set(text, gaps):
    max_g, min_g = len(gaps) - 1, 0
    gap_index = get_random_int(min_g, max_g)
    correct = gaps[gap_index]
    correct_answer = correct[2]
    label = correct[0]

    redacted_text, redacted_ans = convert_to_redacted(text, correct[1], label)

    if label == 'LOCATION':
        pass
    else:
        wrong_answers = []
        try:
            wrong_answers = get_wrong_answers(
                label, correct_answer, gaps, gap_index)

            wrong_answers += [correct_answer]
            shuffle(wrong_answers)

            return {
                "question": redacted_text,
                "opt1": str(wrong_answers[0]),
                "opt2": str(wrong_answers[1]),
                "opt3": str(wrong_answers[2]),
                "answer": str(correct_answer)
            }
        except:
            return None

import nltk
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')

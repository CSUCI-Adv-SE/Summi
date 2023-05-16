from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import heapq
import nltk
nltk.download('punkt')
nltk.download('stopwords')


def summarizer_text_local(text):
    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if not word.lower() in stop_words]

    # Calculate word frequencies
    word_frequencies = Counter(words)

    # Calculate sentence scores
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence)
        for word in sentence_words:
            if word in word_frequencies.keys():
                if len(sentence_words) < 30:
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] = word_frequencies[word]/2

    # Get the top 3 sentences with the highest scores
    summary_sentences = heapq.nlargest(
        3, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

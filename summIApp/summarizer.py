import nltk
nltk.download('punkt')
nltk.download('stopwords')
import heapq
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def summarizer(text):
    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if not word.lower() in stop_words]

    # Calculate word frequencies
    word_frequencies = {}
    for word in words:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

    # Find the most frequent word
    max_frequency = max(word_frequencies.values())

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
    summary_sentences = heapq.nlargest(3, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

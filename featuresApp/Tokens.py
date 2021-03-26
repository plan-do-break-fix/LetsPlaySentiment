from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def tokenize(text: str, normal=True) -> List[str]:
    text = text.lower() if normal else text
    return nltk.word_tokenize(text)


def drop_stopwords(tokens: List[str]) -> List[str]:
    return filter(lambda token: \
                         True if token in stopwords.words("english") \
                         else False,
                  tokens)


def lemmatize(tokens: List[str]) -> List[str]:
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]
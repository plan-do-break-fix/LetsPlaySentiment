import re

from contraction import contractions_dict

def resurrect_expletives(text: str, mode="static") -> str:
    if mode == "static":
        return text.replace("[ __ ]", "fuck")


def strip_additions(text: str) -> str:
    return re.sub(" ?\[ __ ] ?", " ").strip()


def expand_contractions(text: str) -> str:
    for word in contractions_dict.keys():
        text = text.replace(word, contractions_dict[word])
    return text
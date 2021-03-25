from re import search

"""Used to keep regex.search() calls to a minimum."""
def confirmed_match(target: str, **kwargs) -> bool:

    if "match_strings" not in kwargs.keys() and \
                "match_regexes" not in kwargs.keys():
        print("Unmatchable terms have been passed to confirmed_match.")
        raise ValueError

    match_strings = kwargs["match_strings"] \
                  if "match_strings" in kwargs.keys() else False
    unmatch_strings = kwargs["unmatch_strings"] \
                  if "unmatch_strings" in kwargs.keys() else False
    match_regexes = kwargs["match_regexes"] \
                  if "match_regexes" in kwargs.keys() else False
    unmatch_regexes = kwargs["unmatch_regexes"] \
                  if "unmatch_regexes" in kwargs.keys() else False

    if unmatch_strings:
        if any([term in target for term in unmatch_strings]):
            return False
    if unmatch_regexes:
        if any([search(regex, target) for regex in unmatch_regexes]):
            return False
    if match_strings:
        if any([term in target for term in match_strings]):
            return True
    if match_regexes:
        if any([search(regex, target) for regex in match_regexes]):
            return True
    return False


import json

"""Allows sparse JSON using null for standard matching."""
def load_search_terms(fpath) -> dict:
    with open(fpath, "r") as _f:
        search_terms = json.load(_f)
    for key in search_terms.keys():
        if not search_terms[key]:
            search_terms[key] = {"match_strings": [key.lower()]}
    return search_terms
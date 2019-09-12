# https://git.nzoss.org.nz/tim-mcnamara/detect-delimiter/blob/master/detect_delimiter.py

from collections import Counter
import string
import copy
from typing import Optional, List

SILLY_DELIMITERS = frozenset(string.ascii_letters + string.digits + '.')


def same(sequence):
    elements = iter(sequence)
    try:
        first = next(elements)
    except StopIteration:
        return True
    for el in elements:
        if el != first:
            return False
    return True


def detect(text: str, default: Optional[str] = None, whitelist: Optional[List[str]] = None,
           blacklist: Optional[List[str]] = SILLY_DELIMITERS) -> Optional[str]:
    r"""
    Detects the delimiter used in text formats such as CSV and its
    many counsins.

    >>> detect(r"looks|like|the vertical bar\nis|the|delimiter\n")
    '|'

    `detect_delimiter.detect()` looks at the text provided to try to
    find an uncommon delimiter, such as `' for whatever reason.

    >>> detect('looks\x10like\x10something stupid\nis\x10the\x10delimiter')
    '\x10'

    When `detect()` doesn't know, it returns `None`:

    >>> text = "not really any delimiters in here.\nthis is just text.\n"
    >>> detect(text)

    It's possible to provide a default, which will be used in that case:

    >>> detect(text, default=',')
    ','

    By default, it will prevent avoid checking alpha-numeric characters
    and the period/full stop character ("."). This can be adjusted via
    the `blacklist` parameter.

    If you believe that you know the delimiter, it's possible to provide
    a list of possible delimiters to check for via the `whitelist` parameter.
    If you don't provide a value, `[',', ';', ':', '|', '\t']` will be checked.
    """
    if whitelist:
        candidates = whitelist
    else:
        candidates = list(',;:|\t')

    sniffed_candidates = Counter()
    likely_candidates = []

    lines = []
    # todo: support streaming
    text_ = copy.copy(text)
    while len(lines) < 5:
        for line in text_.splitlines():
            lines.append(line)

    for c in candidates:
        fields_for_candidate = []

        for line in lines:
            for char in line:
                if char not in blacklist:
                    sniffed_candidates[char] += 1
            fields = line.split(c)
            n_fields = len(fields)

            # if the delimiter isn't present in the
            # first line, it won't be present in the others
            if n_fields == 1:
                break
            fields_for_candidate.append(n_fields)

        if not fields_for_candidate:
            continue

        if same(fields_for_candidate):
            likely_candidates.append(c)

    # no delimiter found
    if not likely_candidates:
        if whitelist is None and sniffed_candidates:
            new_whitelist = [char for (char, _count) in sniffed_candidates.most_common()]
            return detect(text, whitelist=new_whitelist) or default
        return default

    if default in likely_candidates:
        return default

    return likely_candidates[0]



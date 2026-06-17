"""
Search helpers: tokenization, relevance ranking, and fuzzy "did you mean".

Kept separate from the ORM so the algorithmic core is easy to test in isolation.
The database (``ProductQuerySet.search``) narrows candidates with a cheap boolean
filter; these helpers rank that filtered subset and offer spelling suggestions.

Why rank in Python: SQLite (without the FTS5 extension) can't order rows by
relevance. So we let the DB do the cheap part (narrow the set) and score the
already-small result here. For a large corpus the production upgrade is an
inverted index (e.g. SQLite FTS5 / Postgres GIN) with BM25 ranking.
"""

import difflib
import re

from .constants import ProductSearch

_TOKEN_RE = re.compile(r"\w+")


def tokenize(query):
    """Split a raw query string into normalized search tokens.

    Lowercased ``\\w+`` tokens, tokens shorter than ``MIN_TOKEN_LEN`` dropped,
    duplicates removed (order preserved), capped at ``MAX_TOKENS`` to bound
    pathological input.
    """
    if not query:
        return []

    seen = set()
    tokens = []
    for match in _TOKEN_RE.findall(query.lower()):
        if len(match) < ProductSearch.MIN_TOKEN_LEN or match in seen:
            continue
        seen.add(match)
        tokens.append(match)
        if len(tokens) >= ProductSearch.MAX_TOKENS:
            break
    return tokens


def relevance(product, tokens):
    """Weighted relevance score for ``product`` against ``tokens``.

    Name hits outweigh description hits (term-frequency aware), with bonuses when
    every token appears in the name and when the name matches the query exactly.
    """
    if not tokens:
        return 0

    name = product.name.lower()
    description = product.description.lower()

    score = 0
    tokens_in_name = 0
    for token in tokens:
        name_hits = name.count(token)
        if name_hits:
            score += ProductSearch.NAME_WEIGHT * name_hits
            tokens_in_name += 1
        if token in description:
            score += ProductSearch.DESCRIPTION_WEIGHT

    if tokens_in_name == len(tokens):
        score += ProductSearch.ALL_TOKENS_IN_NAME_BONUS
    if name == " ".join(tokens):
        score += ProductSearch.EXACT_NAME_BONUS

    return score


def rank(products, tokens):
    """Return ``products`` ordered by descending relevance, name as tiebreak.

    Decorate-sort-undecorate: score each product once, then sort by
    ``(-score, name)`` so ties stay alphabetical and ordering is deterministic.
    For top-k over a very large candidate set, ``heapq.nlargest(k, ...)`` would
    avoid the full sort (O(n log k)); here we rank the whole filtered subset.
    """
    products = list(products)
    if not tokens:
        return products
    return sorted(products, key=lambda p: (-relevance(p, tokens), p.name.lower()))


def build_vocabulary():
    """Set of known terms (product names, tags, categories) for suggestions.

    Touches the DB, so it is built on demand (only when a search returns nothing).
    Imported lazily to avoid a circular import with ``models``.
    """
    from .models import Category, Product, Tag

    vocabulary = set()
    for queryset in (
        Product.objects.values_list("name", flat=True),
        Tag.objects.values_list("name", flat=True),
        Category.objects.values_list("name", flat=True),
    ):
        for value in queryset:
            vocabulary.update(tokenize(value))
    return vocabulary


def suggest(tokens, vocabulary):
    """Return a corrected query string if ``tokens`` look misspelled, else None.

    For each token not already known, find the closest vocabulary term by
    edit-distance similarity (``difflib`` -- no extra dependency). If at least one
    token is corrected, return the rebuilt query; otherwise None. A BK-tree would
    make this scale to a very large vocabulary.
    """
    if not tokens or not vocabulary:
        return None

    vocabulary_list = list(vocabulary)
    corrected = []
    changed = False
    for token in tokens:
        if token in vocabulary:
            corrected.append(token)
            continue
        matches = difflib.get_close_matches(
            token, vocabulary_list, n=1, cutoff=ProductSearch.FUZZY_CUTOFF
        )
        if matches and matches[0] != token:
            corrected.append(matches[0])
            changed = True
        else:
            corrected.append(token)

    return " ".join(corrected) if changed else None

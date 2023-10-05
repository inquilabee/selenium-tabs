from contextlib import suppress
from urllib.parse import urlparse

import tldextract


def get_domain(url: str) -> str:
    with suppress():
        return tldextract.extract(url).domain

    return urlparse(url).netloc

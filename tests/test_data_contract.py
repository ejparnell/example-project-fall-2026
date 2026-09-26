from collections import Counter
from pathlib import Path

from fall_ai_studio.catalog import load_catalog

AUTHORITATIVE_SOURCE = Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv")
AUTHORITATIVE_SHA256 = "507d8d670c9c3c8d58f400d42eed09270b6b01354332770081bdb455d53b8c84"


def test_authoritative_source_matches_the_september_data_contract():
    catalog = load_catalog(AUTHORITATIVE_SOURCE, expected_sha256=AUTHORITATIVE_SHA256)

    action_counts = Counter(len(card.actions) for card in catalog.cards.values())
    assert catalog.source.row_count == 2022
    assert catalog.source.card_count == 1267
    assert action_counts == {0: 8, 1: 536, 2: 691, 3: 32}

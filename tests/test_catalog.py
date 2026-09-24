import csv
from pathlib import Path

import pytest

from fall_ai_studio.catalog import (
    CardAction,
    CatalogValidationError,
    load_catalog,
    load_deck,
)

SOURCE_HEADERS = [
    "Card ID",
    "Card Name",
    "Expansion",
    "Collection No.",
    "Stage (Pokémon)/Type (Energy and Trainer)",
    "Rule",
    "Category",
    "Previos stage",
    "HP",
    "Type",
    "Weakness",
    "Resistance (Type)",
    "Retreat",
    "Move Name",
    "Cost",
    "Damage",
    "Effect Explanation",
]


def test_catalog_aggregates_source_rows_into_one_card_record(tmp_path):
    source = tmp_path / "cards.csv"
    rows = [
        [
            "721",
            "Sprigatito",
            "PAL",
            "12",
            "Basic",
            "n/a",
            "Pokémon",
            "n/a",
            "70",
            "{G}",
            "{R}",
            "",
            "1",
            "Scratch",
            "{C}",
            "10",
            "",
        ],
        [
            "721",
            "Sprigatito",
            "PAL",
            "12",
            "Basic",
            "n/a",
            "Pokémon",
            "n/a",
            "70",
            "{G}",
            "{R}",
            "",
            "1",
            "Seed Bomb",
            "{G}{C}",
            "30",
            "n/a",
        ],
    ]
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SOURCE_HEADERS)
        writer.writerows(rows)

    catalog = load_catalog(source)

    assert catalog.source.row_count == 2
    assert len(catalog.cards) == 1
    assert catalog.cards[721].previous_stage is None
    assert catalog.cards[721].actions == (
        CardAction(order=1, name="Scratch", cost="{C}", damage="10", effect=None),
        CardAction(order=2, name="Seed Bomb", cost="{G}{C}", damage="30", effect=None),
    )


def test_reference_deck_contains_60_known_cards():
    from kaggle_environments.envs.cabt.cabt import deck as official_cabt_deck

    catalog = load_catalog(Path("data/pokemon-tcg-ai-battle-challenge-strategy/EN Card Data.csv"))

    deck = load_deck(Path("config/reference-deck.json"), catalog)

    assert deck.name == "official-cabt-reference-deck"
    assert len(deck.card_ids) == 60
    assert set(deck.card_ids) == {3, 721, 722, 723, 1092, 1121, 1145, 1163, 1219, 1227, 1262}
    assert list(deck.card_ids) == official_cabt_deck


def test_catalog_rejects_inconsistent_card_level_values(tmp_path):
    source = tmp_path / "cards.csv"
    first = [
        "721",
        "Sprigatito",
        "PAL",
        "12",
        "Basic",
        "n/a",
        "Pokémon",
        "n/a",
        "70",
        "{G}",
        "{R}",
        "",
        "1",
        "Scratch",
        "{C}",
        "10",
        "",
    ]
    second = first.copy()
    second[8] = "80"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SOURCE_HEADERS)
        writer.writerows([first, second])

    with pytest.raises(CatalogValidationError, match="inconsistent card-level fields"):
        load_catalog(source)


def test_catalog_rejects_more_than_three_actions_for_one_card(tmp_path):
    source = tmp_path / "cards.csv"
    row = [
        "721",
        "Sprigatito",
        "PAL",
        "12",
        "Basic",
        "n/a",
        "Pokémon",
        "n/a",
        "70",
        "{G}",
        "{R}",
        "",
        "1",
        "Scratch",
        "{C}",
        "10",
        "",
    ]
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(SOURCE_HEADERS)
        writer.writerows([row] * 4)

    with pytest.raises(CatalogValidationError, match="more than three Card Actions"):
        load_catalog(source)

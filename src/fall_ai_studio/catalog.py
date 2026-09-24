"""Load the authoritative card export behind a small, validated interface."""

from __future__ import annotations

import csv
import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

EXPECTED_HEADERS = (
    "Card ID",
    "Card Name",
    "Expansion",
    "Collection No.",
    "Stage (Pokémon)/Type (Energy and Trainer)",
    "Rule",
    "Category",
    "Previous stage",
    "HP",
    "Type",
    "Weakness",
    "Resistance (Type)",
    "Retreat",
    "Move Name",
    "Cost",
    "Damage",
    "Effect Explanation",
)

HEADER_ALIASES = {"Previos stage": "Previous stage"}
CARD_FIELDS = EXPECTED_HEADERS[:13]


class CatalogValidationError(ValueError):
    """Raised when source rows cannot form trustworthy Card Records."""


@dataclass(frozen=True)
class SourceReceipt:
    path: str
    sha256: str
    row_count: int
    card_count: int


@dataclass(frozen=True)
class CardAction:
    order: int
    name: str | None
    cost: str | None
    damage: str | None
    effect: str | None


@dataclass(frozen=True)
class CardRecord:
    card_id: int
    name: str
    expansion: str | None
    collection_number: str | None
    stage_or_type: str | None
    rule: str | None
    category: str | None
    previous_stage: str | None
    hp: str | None
    card_type: str | None
    weakness: str | None
    resistance: str | None
    retreat: str | None
    actions: tuple[CardAction, ...]


@dataclass(frozen=True)
class Catalog:
    source: SourceReceipt
    cards: Mapping[int, CardRecord]


@dataclass(frozen=True)
class Deck:
    name: str
    source: str
    card_ids: tuple[int, ...]
    sha256: str


def _optional(value: str | None) -> str | None:
    if value is None or value.strip().casefold() in {"", "n/a"}:
        return None
    return value


def _card_values(row: Mapping[str, str]) -> tuple[str | None, ...]:
    return tuple(_optional(row[field]) for field in CARD_FIELDS)


def _record(values: tuple[str | None, ...], actions: list[CardAction]) -> CardRecord:
    card_id_text, name, *rest = values
    if card_id_text is None or name is None:
        raise CatalogValidationError("Card ID and Card Name are required")
    return CardRecord(int(card_id_text), name, *rest, tuple(actions))


def load_catalog(path: str | Path, *, expected_sha256: str | None = None) -> Catalog:
    """Return validated Card Records, aggregating ordered actions by Card ID."""

    source_path = Path(path)
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if expected_sha256 is not None and source_hash != expected_sha256:
        raise CatalogValidationError(
            f"Source SHA-256 mismatch: expected {expected_sha256}, got {source_hash}"
        )

    grouped: dict[int, tuple[tuple[str | None, ...], list[CardAction]]] = {}
    row_count = 0
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        original_headers = tuple(reader.fieldnames or ())
        normalized_headers = tuple(HEADER_ALIASES.get(name, name) for name in original_headers)
        if normalized_headers != EXPECTED_HEADERS:
            raise CatalogValidationError(
                "Unexpected source headers: "
                f"expected {EXPECTED_HEADERS!r}, got {original_headers!r}"
            )
        reader.fieldnames = list(normalized_headers)

        for row_count, row in enumerate(reader, start=1):
            values = _card_values(row)
            card_id_text = values[0]
            if card_id_text is None:
                raise CatalogValidationError(f"Row {row_count} has no Card ID")
            card_id = int(card_id_text)
            prior = grouped.get(card_id)
            if prior is None:
                actions: list[CardAction] = []
                grouped[card_id] = (values, actions)
            else:
                prior_values, actions = prior
                if values != prior_values:
                    raise CatalogValidationError(
                        f"Card ID {card_id} has inconsistent card-level fields at row {row_count}"
                    )

            action_values = tuple(
                _optional(row[field])
                for field in ("Move Name", "Cost", "Damage", "Effect Explanation")
            )
            if any(value is not None for value in action_values):
                if len(actions) >= 3:
                    raise CatalogValidationError(
                        f"Card ID {card_id} has more than three Card Actions at row {row_count}"
                    )
                actions.append(CardAction(len(actions) + 1, *action_values))

    cards = {card_id: _record(values, actions) for card_id, (values, actions) in grouped.items()}
    receipt = SourceReceipt(str(source_path), source_hash, row_count, len(cards))
    return Catalog(receipt, MappingProxyType(cards))


def load_deck(path: str | Path, catalog: Catalog) -> Deck:
    """Load a 60-card deck whose card IDs all exist in the supplied Catalog."""

    deck_path = Path(path)
    raw = deck_path.read_bytes()
    document = json.loads(raw)
    if document.get("schema") != "fall-ai-studio/reference-deck/v1":
        raise CatalogValidationError("Reference deck has an unsupported schema")
    card_ids = document.get("cards")
    if not isinstance(card_ids, list) or not all(type(card_id) is int for card_id in card_ids):
        raise CatalogValidationError("Reference deck cards must be a list of integer Card IDs")
    if len(card_ids) != 60:
        raise CatalogValidationError(f"Reference deck must contain 60 cards, got {len(card_ids)}")
    unknown = sorted(set(card_ids).difference(catalog.cards))
    if unknown:
        raise CatalogValidationError(f"Reference deck contains unknown Card IDs: {unknown}")
    name = document.get("name")
    source = document.get("source")
    if not isinstance(name, str) or not isinstance(source, str):
        raise CatalogValidationError("Reference deck name and source must be strings")
    return Deck(name, source, tuple(card_ids), hashlib.sha256(raw).hexdigest())

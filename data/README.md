# Pokémon TCG AI Battle Challenge Data

## Dataset Description

This competition provides card metadata and reference materials for the Pokémon Trading Card Game environment used in the simulator.

The dataset contains card identifiers, card names, expansion information, gameplay metadata, and reference images for the cards available in the competition environment. These files help participants understand the card pool and map the card IDs used in the simulator to their corresponding card details.

English and Japanese versions of the card data are provided. They describe the same card pool in different languages.

## Location

All supplied files are stored in [`pokemon-tcg-ai-battle-challenge-strategy`](pokemon-tcg-ai-battle-challenge-strategy).

## Primary Files

| File | Description |
|---|---|
| `Card_ID_List_EN.pdf` | English reference document listing the available cards, including card ID, name, expansion, collection number, and card image. |
| `Card_ID_List_JP.pdf` | Japanese version of the card reference document. |
| `EN Card Data.csv` | Structured English metadata for the available cards. |
| `JP Card Data.csv` | Structured Japanese metadata for the available cards. |

> **Repository note:** Each supplied PDF is larger than GitHub's 100 MB per-file limit. The PDFs remain in the local project data folder but are excluded from standard Git tracking. Use an approved shared-data location or configure Git LFS before distributing them through GitHub.

## Supplied Alternate Files

The source folder also contains `Card_ID List_EN_.pdf`, `Card_ID List_JP_.pdf`, `EN_Card_Data.csv`, and `JP_Card_Data.csv`. They have been retained exactly as supplied so no source data is lost.

- The two PDF files ending in `_` are byte-for-byte duplicates of their primary counterparts.
- The CSV files with underscores are alternate exports. They are not byte-for-byte duplicates of the primary CSVs: they use different line endings and contain some field-level corrections or substitutions.
- Select and document one version of each language dataset before analysis. Do not combine rows from the primary and alternate exports without first reconciling their differences.

## CSV Schema

Both language datasets share the same general structure:

| Column | Description |
|---|---|
| `Card ID` | Unique identifier for a card used by the simulator. |
| `Card Name` | Name of the card. |
| `Expansion` | Expansion set to which the card belongs. |
| `Collection No.` | Card's collection number within the expansion. |
| `Stage (Pokémon) / Type (Energy and Trainer)` | Pokémon evolution stage, or the card type for Energy and Trainer cards. |
| `Rule` | Special rule text associated with the card, when applicable. |
| `Category` | Card category, such as Pokémon, Trainer, or Energy. |
| `Previous stage` | Previous evolution stage required for the Pokémon card. The primary English export misspells this header as `Previos stage`. |
| `HP` | Hit Points of the Pokémon. |
| `Type` | Pokémon type, such as Grass, Fire, or Water. |
| `Weakness` | Pokémon weakness type. |
| `Resistance (Type)` | Pokémon resistance type. |
| `Retreat` | Energy cost required to retreat the Pokémon. |
| `Move Name` | Name of the attack, ability, or move. |
| `Cost` | Energy cost required to use the move. |
| `Damage` | Damage dealt by the move. |
| `Effect Explanation` | Move effect or other explanatory rule text. |

## Recommended First Checks

Before modeling:

1. Confirm which CSV export the team will use and record its checksum.
2. Load the CSV with a parser that supports quoted multiline fields.
3. Validate the number and names of columns.
4. Check whether one card ID appears on multiple rows because a card has multiple moves or abilities.
5. Profile missing values and values such as `n/a` before converting fields to numeric types.

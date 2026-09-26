# Aggregate source rows into Card Records

The Catalog will expose one Card Record per simulator `Card ID` and aggregate each ID's zero to three ordered move, attack, or ability rows as Card Actions. It normalizes blank and `n/a` missing values but rejects repeated rows whose card-level fields disagree, preserving all row-level action evidence without making callers mistake the Authoritative Source's 2,022 rows for 2,022 distinct cards; the validated source contains 1,267 Card Records and no card-level inconsistencies within repeated IDs.

# Organize code around three deep modules

The installable package will expose three deep modules: Catalog hides source normalization plus card and deck validation; Battle runs a policy under an evaluation plan and returns structured results; Evidence creates and verifies Run Receipts, Artifact Manifests, and Artifact Bundles. CLI commands, notebooks, and tests cross these same interfaces, with CABT and an in-memory test adapter at the simulator seam and the Baseline Agent and Integration Control at the policy seam; additional abstractions wait until a second real adapter exists.

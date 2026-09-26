# Record completion in Issue Work Bundles

Each completed Issue will commit a versioned Issue Work Bundle through its linked pull request. The
bundle uses a report-style README as its human entry point, preserves exact repository-relative
snapshots of the source, configuration, automation, documentation, and test files needed to review
the work, records executed verification, and binds every file to the Issue and source commit with a
manifest and SHA-256 hash. Bundle Integrity rejects missing, extra, changed, unsafe, or symlinked
content. These bounded work records make individual Issue handoffs inspectable without weakening
the separate rule that only canonical GitHub Actions may approve a monthly milestone bundle.

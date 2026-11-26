# Architecture and limitations

The API delegates file extraction to `DocumentProcessor`, keeps source filename/page/character offsets with clauses, and stores a pack in a replaceable service layer. `DocumentComparisonPipeline` returns original clause evidence for each comparison. Models are singleton-loaded only when a comparison is requested.

Document-level precedence is deliberately not treated as clause-level legal supersession: a contradiction under signed amendment precedence is surfaced as `SUPERSEDED` with review required. Incomplete scope cannot establish a conflict. OCR is not implemented because no OCR runtime is present; scanned PDFs with no extractable text fail clearly rather than yielding invented clauses.

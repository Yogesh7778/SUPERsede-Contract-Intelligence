# API

Start with `python -m uvicorn src.api.main:app --reload`. The interactive contract is available at `/docs`.

- `GET /health` returns service health without loading models.
- `POST /packs` creates a document pack.
- `POST /packs/{pack_id}/documents` accepts a TXT, PDF, or DOCX file plus `document_id` and `document_type`. Files over 20 MB and unsupported types are rejected.
- `GET /packs/{pack_id}` returns extraction status, metadata, clauses, and completed results.
- `POST /packs/{pack_id}/compare` accepts optional `evaluation_date` and `similarity_threshold`, loads models once per process, and returns classifications plus clause evidence.

Uploads are stored under `data/uploads` for the process lifetime. The service interface is intentionally isolated so SQLite can be substituted when durable multi-process storage is needed.

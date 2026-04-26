# AI Document Analyst Foundation MVP Design

## 1. Objective

Build the first production-like MVP slice of AI Document Analyst as a generic document intelligence platform for `PDF` and `TXT` files. The system should support document upload, parsing, chunking, embeddings, retrieval, reranking, question answering with citations, and document summarization through a backend API and a demo frontend.

This first iteration is intentionally platform-first rather than domain-first. The goal is to establish a clean, extensible architecture that can later absorb OCR, `DOCX`, image ingestion, structured extraction for contracts, and evaluation workflows without redesigning core interfaces.

## 2. Scope

### In Scope

- Upload one or more `PDF` or `TXT` documents
- Persist file metadata and processing status
- Parse text-based PDFs and plain text files into a common structured representation
- Split parsed content into retrievable chunks with page and section metadata
- Generate embeddings for chunks and index them in a vector store
- Support semantic search over indexed chunks
- Apply reranking before answer generation
- Answer questions with evidence-backed citations
- Generate short and detailed document summaries
- Provide a demo UI for upload, browsing documents, semantic search, QA, and summary
- Support Docker-based local deployment

### Out of Scope for This Slice

- `DOCX` ingestion
- OCR for scanned PDFs or images
- Contract-specific structured extraction
- Benchmark dataset creation and evaluation dashboards
- Advanced query history UX
- Multi-tenant auth and permissions
- Horizontal scaling and distributed workers

## 3. Product Direction

The MVP should feel like a document analysis system, not just a chat wrapper around a PDF. The user journey is:

1. Upload a document
2. Wait for ingestion to complete
3. Inspect the document and its structure
4. Ask questions and receive grounded answers with citations
5. Run semantic search to inspect relevant source chunks
6. Generate summaries in multiple modes

The most important product qualities for this slice are:

- grounded answers
- visible evidence and traceability
- stable ingestion pipeline
- replaceable infrastructure components
- simple but convincing demo experience

## 4. Architecture

### 4.1 System Shape

Use a modular monolith for the MVP:

- one `FastAPI` backend service
- one `React + Vite` frontend
- one relational database for app metadata
- one vector database for embeddings
- one local file storage area for uploaded and processed artifacts

This avoids early microservice complexity while keeping boundaries explicit enough to evolve later.

### 4.2 Core Backend Modules

#### Ingestion Service

Responsibilities:

- accept uploaded files
- validate supported file types
- assign document identifiers
- persist raw files
- create document records
- trigger the processing pipeline

#### Parser Service

Responsibilities:

- parse `PDF` and `TXT`
- normalize extracted content into a shared schema
- preserve page associations for PDFs
- detect headings or section-like structure where feasible

#### Chunking Module

Responsibilities:

- convert parsed content into retrieval chunks
- preserve `doc_id`, `page_num`, `section_title`, and `chunk_index`
- support configurable chunk size and overlap
- keep ordering stable for summary generation

#### Embedding Indexer

Responsibilities:

- generate embeddings for chunks
- persist chunks and metadata in the relational store
- upsert vectors and metadata into the vector database

#### Retrieval Module

Responsibilities:

- perform semantic search using query embeddings
- apply optional metadata filters
- return top-k candidate chunks with scores

#### Reranker Module

Responsibilities:

- rerank the retrieved candidate set
- produce the final evidence set for QA and summary support

#### QA and Summary Module

Responsibilities:

- assemble grounded prompts from reranked chunks
- generate short answers with citations
- refuse when evidence is insufficient
- produce short and detailed summaries

#### API Layer

Responsibilities:

- expose upload, listing, search, QA, summary, and health endpoints
- validate requests and serialize responses

## 5. Data Flow

### 5.1 Upload and Ingestion Flow

1. Client sends `POST /documents/upload`
2. Backend validates file type and stores the raw file under `storage/raw/<doc_id>/`
3. Backend inserts a `document` record with status `uploaded`
4. Processing pipeline starts
5. Parser converts the source into `StructuredDocument`
6. Chunker creates normalized chunks
7. Embedder generates vectors
8. Indexer writes chunks to the relational store and vectors to the vector database
9. Document status transitions to `ready`

If any stage fails, the document status transitions to `failed` and stores a human-readable error message.

### 5.2 Search Flow

1. Client sends `POST /search`
2. Backend embeds the query
3. Retrieval module fetches top-k chunks from vector search
4. Optional metadata filters narrow the candidate set
5. Backend returns scored results with document and page references

### 5.3 QA Flow

1. Client sends `POST /qa`
2. Backend embeds the query
3. Retrieval fetches approximately top 20 chunks
4. Reranker reduces the set to approximately top 5 chunks
5. Prompt builder composes grounded context from the reranked chunks
6. LLM generates a concise answer constrained to the evidence
7. Backend returns the answer with citations and snippets

If the evidence does not support an answer, the API returns a refusal message such as:

`I could not find enough evidence in the document.`

### 5.4 Summary Flow

1. Client sends `POST /summary`
2. Backend loads document chunks in document order
3. Summary module generates `short` or `detailed` output
4. Backend returns the summary text and basic source metadata

## 6. Core Data Contracts

### 6.1 StructuredDocument

This is the canonical parser output shared across ingestion stages.

```json
{
  "doc_id": "123",
  "pages": [
    {
      "page_num": 1,
      "blocks": [
        {
          "type": "heading",
          "text": "Introduction",
          "section_title": "Introduction"
        },
        {
          "type": "paragraph",
          "text": "This agreement...",
          "section_title": "Introduction"
        }
      ]
    }
  ]
}
```

### 6.2 Chunk

This is the canonical retrieval unit.

```json
{
  "id": "chunk_001",
  "doc_id": "123",
  "page_num": 8,
  "chunk_index": 14,
  "section_title": "Termination",
  "text": "The agreement may be terminated with 30 days prior notice...",
  "metadata": {
    "source_type": "pdf",
    "parser": "pymupdf"
  }
}
```

### 6.3 RetrievedChunk

This is the retrieval and QA handoff object.

```json
{
  "chunk_id": "chunk_001",
  "doc_id": "123",
  "page_num": 8,
  "section_title": "Termination",
  "text": "The agreement may be terminated with 30 days prior notice...",
  "retrieval_score": 0.91,
  "rerank_score": 0.97
}
```

## 7. Persistence Model

### documents

- `id`
- `filename`
- `file_type`
- `storage_path`
- `upload_time`
- `language`
- `pages_count`
- `status`
- `ocr_used`
- `error_message`

### chunks

- `id`
- `doc_id`
- `page_num`
- `chunk_index`
- `text`
- `section_title`
- `metadata_json`

### queries

- `id`
- `query_text`
- `doc_id`
- `created_at`
- `mode`

### answers

- `id`
- `query_id`
- `answer_text`
- `citations_json`
- `latency_ms`

The vector database stores per chunk:

- `chunk_id`
- `doc_id`
- `page_num`
- `section_title`
- `text`
- `embedding`
- retrieval metadata used for filtering

## 8. API Surface

### Documents

- `POST /documents/upload`
- `GET /documents`
- `GET /documents/{id}`
- `DELETE /documents/{id}`

### Search

- `POST /search`

Response shape:

```json
{
  "results": [
    {
      "doc_id": "123",
      "page": 8,
      "score": 0.91,
      "text": "The agreement may be terminated with 30 days prior notice..."
    }
  ]
}
```

### QA

- `POST /qa`

Response shape:

```json
{
  "answer": "The termination notice period is 30 days.",
  "citations": [
    {
      "doc_id": "123",
      "page": 8,
      "text": "The agreement may be terminated with 30 days prior notice..."
    }
  ]
}
```

### Summary

- `POST /summary`

### Health

- `GET /health`

## 9. Technology Choices

### Backend

- `Python`
- `FastAPI`
- `Pydantic`
- `SQLAlchemy`
- `SQLite` for MVP, structured to allow later `PostgreSQL`

### Parsing

- `PyMuPDF` for PDF text extraction
- standard Python text loading for `TXT`

### Retrieval

- embedding model from `sentence-transformers`, preferably a modern `bge` or `e5` class model
- `Qdrant` as vector database for local developer experience and metadata filtering support

### Reranking

- cross-encoder reranker from `sentence-transformers` or `BAAI`

### LLM Layer

- provider abstraction with initial integration through `OpenRouter`

### Frontend

- `React`
- `Vite`
- lightweight styling, ideally `Tailwind CSS`

### Deployment

- `Docker`
- `Docker Compose`

## 10. Non-Functional Requirements

### Performance Targets

- ingestion for a medium document: `10-30s`
- search response: `<= 2s`
- QA response: `<= 10s`

### Reliability Requirements

System should fail gracefully for:

- empty documents
- broken PDFs
- very short texts
- unsupported files
- questions with no answer

### Extensibility Requirements

The architecture must allow future replacement of:

- embedding model
- reranker model
- LLM provider
- vector database
- parser implementation
- extraction schemas

### Configurability

The following should be externalized:

- chunk size
- chunk overlap
- embedding model name
- reranker model name
- LLM provider settings
- retrieval top-k
- rerank cut-off
- prompt templates

## 11. Frontend MVP

### Documents Page

- upload control
- document list
- processing status
- quick metadata view

### Document Detail View

- document metadata
- chunk or section sidebar
- searchable content preview
- page references in retrieved results

### QA View

- question input
- answer panel
- citations list
- source snippets with page labels

### Summary View

- mode selector: `short` or `detailed`
- generated summary output

For the first slice, an in-browser PDF renderer is optional. If it slows delivery, use metadata plus snippets instead of full PDF highlighting.

## 12. Phased Roadmap

### Phase 1: Foundation MVP

- `PDF` and `TXT` ingestion
- parser normalization
- chunking
- embeddings
- retrieval
- reranking
- QA with citations
- summary
- demo UI

### Phase 2: Intelligence Expansion

- `DOCX`
- OCR for scanned content
- metadata filtering expansion
- structured extraction for contracts
- query history

### Phase 3: Quality and Evaluation

- benchmark dataset
- retrieval metrics
- QA groundedness evaluation
- extraction accuracy evaluation
- summary consistency evaluation

## 13. Risks and Mitigations

### Risk: Weak PDF structure extraction

Mitigation:

- keep the parser contract simple
- treat heading detection as best-effort
- rely on page metadata even if section extraction is imperfect

### Risk: Hallucinated answers

Mitigation:

- strict grounded prompt design
- require citations in responses
- return refusal when evidence is insufficient

### Risk: Slow local inference

Mitigation:

- keep top-k small after reranking
- make models configurable
- support lighter default models for local demo runs

### Risk: Overbuilding too early

Mitigation:

- keep OCR, extraction, and evaluation out of the first implementation plan
- ship the smallest convincing end-to-end system first

## 14. Acceptance Criteria for the First Implementation Plan

The first implementation plan should be considered successful when:

- a user can upload a `PDF` or `TXT` file
- the file is parsed and indexed without manual steps
- the document becomes searchable
- QA returns grounded answers with page-level citations
- summary works in at least two modes
- the demo frontend can exercise the main user flows
- the whole system runs locally via `Docker Compose`

## 15. Explicit Deferrals

The following are intentionally deferred beyond the first implementation plan:

- scan OCR
- image ingestion
- contract extraction schema
- evaluation benchmark and metrics implementation
- auth
- cloud deployment

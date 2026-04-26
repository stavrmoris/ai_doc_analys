import type {
  DocumentRecord,
  QAResponse,
  SearchResponse,
  SummaryMode,
  SummaryResponse,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function readResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    return (await response.json()) as T;
  }

  let message = `Request failed with status ${response.status}`;

  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      message = payload.detail;
    }
  } catch {
    // Ignore JSON parsing failures and fall back to the HTTP status.
  }

  throw new Error(message);
}

export async function fetchDocuments(): Promise<DocumentRecord[]> {
  const response = await fetch(`${API_BASE}/documents`);

  return readResponse<DocumentRecord[]>(response);
}

export async function uploadDocument(file: File): Promise<DocumentRecord> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  return readResponse<DocumentRecord>(response);
}

export async function deleteDocument(documentId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    await readResponse(response);
  }
}

export async function searchDocuments(payload: {
  query: string;
  limit?: number;
  doc_id?: number | null;
}): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: payload.query,
      limit: payload.limit ?? 5,
      doc_id: payload.doc_id ?? null,
    }),
  });

  return readResponse<SearchResponse>(response);
}

export async function askQuestion(payload: {
  question: string;
  doc_id?: number | null;
}): Promise<QAResponse> {
  const response = await fetch(`${API_BASE}/qa`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: payload.question,
      doc_id: payload.doc_id ?? null,
    }),
  });

  return readResponse<QAResponse>(response);
}

export async function summarizeDocument(payload: {
  doc_id: number;
  mode: SummaryMode;
}): Promise<SummaryResponse> {
  const response = await fetch(`${API_BASE}/summary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readResponse<SummaryResponse>(response);
}

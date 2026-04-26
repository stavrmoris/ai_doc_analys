export type DocumentRecord = {
  id: number;
  filename: string;
  file_type: string;
  storage_path: string;
  upload_time: string;
  language: string | null;
  pages_count: number | null;
  status: string;
  error_message: string | null;
};

export type SearchResult = {
  doc_id: number;
  page_num: number | null;
  section_title: string | null;
  text: string;
  score: number;
};

export type SearchResponse = {
  results: SearchResult[];
};

export type Citation = {
  doc_id: number;
  page: number | null;
  text: string;
};

export type QAResponse = {
  answer: string;
  citations: Citation[];
};

export type SummaryMode = "short" | "detailed";

export type SummaryResponse = {
  summary: string;
};

export type MutationState = {
  loading: boolean;
  error: string | null;
};

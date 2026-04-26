import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import App from "./App";
import { askQuestion, deleteDocument, summarizeDocument } from "./lib/api";
import type { DocumentRecord } from "./types";

vi.mock("./lib/api", () => ({
  askQuestion: vi.fn(),
  deleteDocument: vi.fn(),
  searchDocuments: vi.fn(),
  summarizeDocument: vi.fn(),
  uploadDocument: vi.fn(),
}));

const documents: DocumentRecord[] = [
  {
    id: 1,
    filename: "contract-a.txt",
    file_type: "txt",
    storage_path: "/tmp/contract-a.txt",
    upload_time: "2026-04-25T10:00:00",
    language: null,
    pages_count: 1,
    status: "ready",
    error_message: null,
  },
  {
    id: 2,
    filename: "contract-b.txt",
    file_type: "txt",
    storage_path: "/tmp/contract-b.txt",
    upload_time: "2026-04-25T11:00:00",
    language: null,
    pages_count: 1,
    status: "ready",
    error_message: null,
  },
];

let selectedId = 1;

vi.mock("./hooks/useDocuments", () => ({
  useDocuments: () => ({
    documents,
    documentsError: null,
    documentsLoading: false,
    refresh: vi.fn(),
    selectedDocument: documents.find((document) => document.id === selectedId) ?? null,
    selectedId,
    setSelectedId: vi.fn(),
  }),
}));

const mockedAskQuestion = vi.mocked(askQuestion);
const mockedDeleteDocument = vi.mocked(deleteDocument);
const mockedSummarizeDocument = vi.mocked(summarizeDocument);

beforeEach(() => {
  selectedId = 1;
  vi.clearAllMocks();
});

test("ignores a stale QA response after selected document changes", async () => {
  let resolveAnswer: (value: Awaited<ReturnType<typeof askQuestion>>) => void = () => undefined;
  mockedAskQuestion.mockReturnValueOnce(
    new Promise((resolve) => {
      resolveAnswer = resolve;
    }),
  );

  const { rerender } = render(<App />);

  fireEvent.change(screen.getByLabelText(/question/i), {
    target: { value: "What is the term?" },
  });
  fireEvent.click(screen.getByRole("button", { name: /^ask$/i }));

  selectedId = 2;
  rerender(<App />);
  resolveAnswer({
    answer: "Stale answer from contract A.",
    citations: [],
  });

  await waitFor(() => {
    expect(screen.queryByText(/stale answer/i)).not.toBeInTheDocument();
  });
});

test("ignores a stale summary response after selected document changes", async () => {
  let resolveSummary: (value: Awaited<ReturnType<typeof summarizeDocument>>) => void = () => undefined;
  mockedSummarizeDocument.mockReturnValueOnce(
    new Promise((resolve) => {
      resolveSummary = resolve;
    }),
  );

  const { rerender } = render(<App />);

  fireEvent.click(screen.getByRole("button", { name: /generate summary/i }));

  selectedId = 2;
  rerender(<App />);
  resolveSummary({
    summary: "Stale summary from contract A.",
  });

  await waitFor(() => {
    expect(screen.queryByText(/stale summary/i)).not.toBeInTheDocument();
  });
});

test("switches the interface language to Russian", async () => {
  render(<App />);

  fireEvent.click(screen.getByRole("button", { name: "RU" }));

  expect(await screen.findByRole("heading", { name: /ваши документы/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /запустить поиск/i })).toBeInTheDocument();
});

test("deletes a document from the library", async () => {
  mockedDeleteDocument.mockResolvedValueOnce(undefined);

  render(<App />);

  fireEvent.click(screen.getByRole("button", { name: /delete contract-a\.txt/i }));

  await waitFor(() => {
    expect(mockedDeleteDocument).toHaveBeenCalledWith(1);
  });
});

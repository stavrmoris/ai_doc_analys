import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { DocumentList } from "./DocumentList";
import type { DocumentRecord } from "../types";

const documents: DocumentRecord[] = [
  {
    id: 1,
    filename: "contract.txt",
    file_type: "txt",
    storage_path: "/tmp/contract.txt",
    upload_time: "2026-04-25T10:00:00",
    language: null,
    pages_count: 1,
    status: "ready",
    error_message: null,
  },
  {
    id: 2,
    filename: "invoice.pdf",
    file_type: "pdf",
    storage_path: "/tmp/invoice.pdf",
    upload_time: "2026-04-25T11:00:00",
    language: "en",
    pages_count: 3,
    status: "uploaded",
    error_message: null,
  },
];

test("renders empty document state", () => {
  render(<DocumentList documents={[]} onDelete={() => undefined} onSelect={() => undefined} selectedId={null} />);

  expect(screen.getByText(/no documents uploaded/i)).toBeInTheDocument();
});

test("marks the selected document semantically and calls onSelect", () => {
  const handleSelect = vi.fn();

  render(<DocumentList documents={documents} onDelete={() => undefined} onSelect={handleSelect} selectedId={2} />);

  expect(screen.getByRole("button", { name: /^invoice\.pdf$/i })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: /^contract\.txt$/i })).toHaveAttribute("aria-pressed", "false");

  fireEvent.click(screen.getByRole("button", { name: /^contract\.txt$/i }));

  expect(handleSelect).toHaveBeenCalledWith(1);
});

test("calls onDelete from the icon button", () => {
  const handleDelete = vi.fn();

  render(<DocumentList documents={documents} onDelete={handleDelete} onSelect={() => undefined} selectedId={1} />);

  fireEvent.click(screen.getByRole("button", { name: /delete invoice\.pdf/i }));

  expect(handleDelete).toHaveBeenCalledWith(2);
});

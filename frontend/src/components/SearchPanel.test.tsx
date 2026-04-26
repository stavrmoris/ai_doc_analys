import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { SearchPanel } from "./SearchPanel";
import { searchDocuments } from "../lib/api";

vi.mock("../lib/api", () => ({
  searchDocuments: vi.fn(),
}));

const mockedSearchDocuments = vi.mocked(searchDocuments);

test("clears document-scoped results when selected document changes", async () => {
  mockedSearchDocuments.mockResolvedValueOnce({
    results: [
      {
        doc_id: 1,
        page_num: 2,
        section_title: "Terms",
        text: "Termination requires 30 days notice.",
        score: 0.91,
      },
    ],
  });

  const { rerender } = render(<SearchPanel selectedDocumentId={1} />);

  fireEvent.change(screen.getByLabelText(/search query/i), {
    target: { value: "termination" },
  });
  fireEvent.click(screen.getByRole("button", { name: /run search/i }));

  expect(await screen.findByText(/termination requires 30 days notice/i)).toBeInTheDocument();

  rerender(<SearchPanel selectedDocumentId={2} />);

  await waitFor(() => {
    expect(screen.queryByText(/termination requires 30 days notice/i)).not.toBeInTheDocument();
  });
  expect(screen.getByText(/search results will appear here/i)).toBeInTheDocument();
});

test("ignores a stale search response after selected document changes", async () => {
  let resolveSearch: (value: Awaited<ReturnType<typeof searchDocuments>>) => void = () => undefined;
  mockedSearchDocuments.mockReturnValueOnce(
    new Promise((resolve) => {
      resolveSearch = resolve;
    }),
  );

  const { rerender } = render(<SearchPanel selectedDocumentId={1} />);

  fireEvent.change(screen.getByLabelText(/search query/i), {
    target: { value: "termination" },
  });
  fireEvent.click(screen.getByRole("button", { name: /run search/i }));

  rerender(<SearchPanel selectedDocumentId={2} />);
  resolveSearch({
    results: [
      {
        doc_id: 1,
        page_num: 2,
        section_title: "Terms",
        text: "Stale result from the previous document.",
        score: 0.91,
      },
    ],
  });

  await waitFor(() => {
    expect(screen.queryByText(/stale result/i)).not.toBeInTheDocument();
  });
  expect(screen.getByText(/search results will appear here/i)).toBeInTheDocument();
});

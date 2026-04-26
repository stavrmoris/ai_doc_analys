import { useEffect, useRef, useState } from "react";

import { useI18n } from "../i18n";
import { searchDocuments } from "../lib/api";
import { useMutationState } from "../hooks/useMutationState";
import type { SearchResult } from "../types";

type SearchPanelProps = {
  selectedDocumentId: number | null;
};

export function SearchPanel({ selectedDocumentId }: SearchPanelProps) {
  const { messages } = useI18n();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const searchState = useMutationState();
  const requestId = useRef(0);
  const selectedDocumentIdRef = useRef<number | null>(selectedDocumentId);

  useEffect(() => {
    requestId.current += 1;
    selectedDocumentIdRef.current = selectedDocumentId;
    setResults([]);
    searchState.reset();
  }, [selectedDocumentId]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      return;
    }

    searchState.start();
    const currentRequestId = requestId.current + 1;
    requestId.current = currentRequestId;
    const docId = selectedDocumentId;

    try {
      const response = await searchDocuments({
        query: trimmedQuery,
        doc_id: docId,
      });
      if (requestId.current !== currentRequestId || selectedDocumentIdRef.current !== docId) {
        return;
      }
      setResults(response.results);
      searchState.succeed();
    } catch (error) {
      if (requestId.current !== currentRequestId || selectedDocumentIdRef.current !== docId) {
        return;
      }
      setResults([]);
      searchState.fail(error);
    }
  }

  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <p className="eyebrow">{messages.search.eyebrow}</p>
          <h2>{messages.search.title}</h2>
        </div>
        <p className="panel__meta">
          {selectedDocumentId ? `${messages.misc.docLabel} #${selectedDocumentId}` : messages.search.allDocs}
        </p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field">
          <span>{messages.search.queryLabel}</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={messages.search.placeholder}
          />
        </label>
        <button type="submit" className="primary-button" disabled={searchState.loading || !query.trim()}>
          {searchState.loading ? messages.search.running : messages.search.run}
        </button>
      </form>
      {searchState.error ? <p className="feedback feedback--error">{searchState.error}</p> : null}
      {!searchState.error && results.length === 0 ? (
        <p className="empty-state">{messages.search.empty}</p>
      ) : null}
      <ul className="result-list">
        {results.map((result, index) => (
          <li key={`${result.doc_id}-${result.page_num}-${index}`} className="result-card">
            <div className="result-card__meta">
              <span>{messages.misc.docLabel} #{result.doc_id}</span>
              <span>{messages.search.score} {result.score.toFixed(3)}</span>
              <span>{result.page_num ? `${messages.search.page} ${result.page_num}` : messages.search.noPage}</span>
            </div>
            {result.section_title ? <strong>{result.section_title}</strong> : null}
            <p>{result.text}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}

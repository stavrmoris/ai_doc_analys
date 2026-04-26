import { useEffect, useState } from "react";

import { useI18n } from "../i18n";
import type { Citation } from "../types";

type QAPanelProps = {
  answer: string | null;
  loading: boolean;
  onAsk: (question: string) => void | Promise<void>;
  citations?: Citation[];
  error?: string | null;
  selectedDocumentId?: number | null;
};

export function QAPanel({
  answer,
  citations = [],
  error = null,
  loading,
  onAsk,
  selectedDocumentId = null,
}: QAPanelProps) {
  const { messages } = useI18n();
  const [question, setQuestion] = useState("");

  useEffect(() => {
    setQuestion("");
  }, [selectedDocumentId]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    void onAsk(trimmedQuestion);
  }

  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <p className="eyebrow">{messages.qa.eyebrow}</p>
          <h2>{messages.qa.title}</h2>
        </div>
        <p className="panel__meta">
          {selectedDocumentId ? `${messages.misc.docLabel} #${selectedDocumentId}` : messages.qa.allDocs}
        </p>
      </div>
      <form className="stack" onSubmit={handleSubmit}>
        <label className="field">
          <span>{messages.qa.questionLabel}</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={messages.qa.placeholder}
            rows={4}
          />
        </label>
        <button type="submit" className="primary-button" disabled={loading || !question.trim()}>
          {loading ? messages.qa.asking : messages.qa.ask}
        </button>
      </form>
      {error ? <p className="feedback feedback--error">{error}</p> : null}
      {!error && !answer ? <p className="empty-state">{messages.qa.empty}</p> : null}
      {answer ? (
        <div className="answer-card">
          <p>{answer}</p>
          {citations.length ? (
            <ul className="citation-list">
              {citations.map((citation, index) => (
                <li key={`${citation.doc_id}-${citation.page}-${index}`}>
                  <strong>{messages.misc.docLabel} #{citation.doc_id}</strong>
                  <span>{citation.page ? `${messages.qa.page} ${citation.page}` : messages.qa.noPage}</span>
                  <p>{citation.text}</p>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

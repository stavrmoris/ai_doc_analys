import { useEffect, useRef, useState } from "react";

import { askQuestion, deleteDocument, summarizeDocument } from "./lib/api";
import { DocumentList } from "./components/DocumentList";
import { DocumentUpload } from "./components/DocumentUpload";
import { QAPanel } from "./components/QAPanel";
import { SearchPanel } from "./components/SearchPanel";
import { SummaryPanel } from "./components/SummaryPanel";
import { useDocuments } from "./hooks/useDocuments";
import { useMutationState } from "./hooks/useMutationState";
import { I18nProvider, useI18n } from "./i18n";
import type { Citation, SummaryMode } from "./types";

function AppContent() {
  const { locale, setLocale, messages } = useI18n();
  const {
    documents,
    documentsError,
    documentsLoading,
    refresh,
    selectedDocument,
    selectedId,
    setSelectedId,
  } = useDocuments();
  const qaState = useMutationState();
  const summaryState = useMutationState();
  const deleteState = useMutationState();
  const [answer, setAnswer] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [summary, setSummary] = useState<string | null>(null);
  const [summaryMode, setSummaryMode] = useState<SummaryMode>("short");
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const qaRequestId = useRef(0);
  const summaryRequestId = useRef(0);
  const selectedIdRef = useRef<number | null>(selectedId);

  useEffect(() => {
    selectedIdRef.current = selectedId;
    qaRequestId.current += 1;
    summaryRequestId.current += 1;
    setAnswer(null);
    setCitations([]);
    setSummary(null);
    qaState.reset();
    summaryState.reset();
  }, [selectedId]);

  async function handleAsk(question: string) {
    const requestId = qaRequestId.current + 1;
    qaRequestId.current = requestId;
    const docId = selectedId;
    qaState.start();

    try {
      const response = await askQuestion({
        question,
        doc_id: docId,
      });
      if (qaRequestId.current !== requestId || selectedIdRef.current !== docId) {
        return;
      }
      setAnswer(response.answer);
      setCitations(response.citations);
      qaState.succeed();
    } catch (error) {
      if (qaRequestId.current !== requestId || selectedIdRef.current !== docId) {
        return;
      }
      setAnswer(null);
      setCitations([]);
      qaState.fail(error);
    }
  }

  async function handleSummarize() {
    if (!selectedId) {
      return;
    }

    const requestId = summaryRequestId.current + 1;
    summaryRequestId.current = requestId;
    const docId = selectedId;
    summaryState.start();

    try {
      const response = await summarizeDocument({
        doc_id: docId,
        mode: summaryMode,
      });
      if (summaryRequestId.current !== requestId || selectedIdRef.current !== docId) {
        return;
      }
      setSummary(response.summary);
      summaryState.succeed();
    } catch (error) {
      if (summaryRequestId.current !== requestId || selectedIdRef.current !== docId) {
        return;
      }
      setSummary(null);
      summaryState.fail(error);
    }
  }

  async function handleDelete(documentId: number) {
    setDeletingId(documentId);
    deleteState.start();

    try {
      await deleteDocument(documentId);
      await refresh();
      deleteState.succeed();
    } catch (error) {
      deleteState.fail(error);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <div className="hero__topline">
            <p className="eyebrow">{messages.hero.eyebrow}</p>
            <div className="language-switcher" role="group" aria-label={messages.localeLabel}>
              {(["en", "ru", "zh"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  className="language-switcher__button"
                  data-active={locale === value}
                  aria-pressed={locale === value}
                  onClick={() => setLocale(value)}
                >
                  {messages.languages[value]}
                </button>
              ))}
            </div>
          </div>
          <h1>{messages.hero.title}</h1>
          <p className="hero__copy">{messages.hero.copy}</p>
        </div>
        <div className="hero__stats">
          <div>
            <strong>{documents.length}</strong>
            <span>{messages.hero.documents}</span>
          </div>
          <div>
            <strong>{selectedDocument ? selectedDocument.file_type.toUpperCase() : "--"}</strong>
            <span>{messages.hero.selectedType}</span>
          </div>
        </div>
      </section>

      <div className="dashboard-grid">
        <aside className="dashboard-column dashboard-column--sidebar">
          <DocumentUpload onUploaded={refresh} />
          {documentsLoading ? <p className="feedback">{messages.misc.loadingDocuments}</p> : null}
          {documentsError ? <p className="feedback feedback--error">{documentsError}</p> : null}
          {deleteState.error ? <p className="feedback feedback--error">{deleteState.error}</p> : null}
          <DocumentList
            documents={documents}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onDelete={handleDelete}
            deletingId={deletingId}
          />
        </aside>

        <section className="dashboard-column dashboard-column--main">
          <section className="panel panel--compact">
            <div className="panel__header">
              <div>
                <p className="eyebrow">{messages.selection.eyebrow}</p>
                <h2
                  className={selectedDocument ? "selection-title" : undefined}
                  title={selectedDocument ? selectedDocument.filename : undefined}
                >
                  {selectedDocument ? selectedDocument.filename : messages.selection.emptyTitle}
                </h2>
              </div>
            </div>
            <p className="selection-copy">
              {selectedDocument
                ? `${messages.selection.docMeta} #${selectedDocument.id} · ${
                    selectedDocument.language ?? messages.selection.unknownLanguage
                  } · ${selectedDocument.pages_count ?? "N/A"} ${messages.selection.pages}`
                : messages.selection.allDocsHint}
            </p>
          </section>

          <SearchPanel selectedDocumentId={selectedId} />
          <QAPanel
            answer={answer}
            citations={citations}
            error={qaState.error}
            loading={qaState.loading}
            onAsk={handleAsk}
            selectedDocumentId={selectedId}
          />
          <SummaryPanel
            error={summaryState.error}
            hasSelection={selectedId !== null}
            loading={summaryState.loading}
            mode={summaryMode}
            onModeChange={setSummaryMode}
            onSummarize={handleSummarize}
            summary={summary}
          />
        </section>
      </div>
    </main>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AppContent />
    </I18nProvider>
  );
}

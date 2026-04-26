import type { DocumentRecord } from "../types";
import { useI18n } from "../i18n";
import { StatusBadge } from "./StatusBadge";

type DocumentListProps = {
  documents: DocumentRecord[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onDelete: (id: number) => void | Promise<void>;
  deletingId?: number | null;
};

function formatUploadTime(value: string, locale: string) {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function TrashIcon() {
  return (
    <svg aria-hidden="true" className="danger-button__icon" viewBox="0 0 24 24" width="16" height="16">
      <path d="M9 3h6l1 2h4v2H4V5h4l1-2Z" />
      <path d="M7 9h10l-.7 11H7.7L7 9Z" />
    </svg>
  );
}

function SpinnerIcon() {
  return (
    <svg
      aria-hidden="true"
      className="danger-button__icon danger-button__icon--spin"
      viewBox="0 0 24 24"
      width="16"
      height="16"
    >
      <path d="M12 3a9 9 0 1 1-8.1 5.1" />
    </svg>
  );
}

export function DocumentList({ documents, selectedId, onSelect, onDelete, deletingId = null }: DocumentListProps) {
  const { locale, messages } = useI18n();

  if (!documents.length) {
    return (
      <section className="panel panel--fill">
        <div className="panel__header">
          <div>
            <p className="eyebrow">{messages.library.eyebrow}</p>
            <h2>{messages.library.title}</h2>
          </div>
        </div>
        <p className="empty-state">{messages.library.empty}</p>
      </section>
    );
  }

  return (
    <section className="panel panel--fill">
      <div className="panel__header">
        <div>
          <p className="eyebrow">{messages.library.eyebrow}</p>
          <h2>{messages.library.title}</h2>
        </div>
        <p className="panel__meta">{documents.length} {messages.library.total}</p>
      </div>
      <ul className="document-list" aria-label={messages.library.title}>
        {documents.map((document) => (
          <li key={document.id}>
            <div
              className="document-card"
              data-active={document.id === selectedId}
            >
              <div className="document-card__row">
                <button
                  type="button"
                  className="document-card__select"
                  aria-pressed={document.id === selectedId}
                  onClick={() => onSelect(document.id)}
                  title={document.filename}
                >
                  <strong className="document-card__title">{document.filename}</strong>
                </button>
                <div className="document-card__actions">
                  <StatusBadge status={document.status} />
                  <button
                    type="button"
                    className="danger-button"
                    onClick={() => onDelete(document.id)}
                    disabled={deletingId === document.id}
                    aria-label={`${messages.library.delete} ${document.filename}`}
                    title={messages.library.delete}
                  >
                    {deletingId === document.id ? <SpinnerIcon /> : <TrashIcon />}
                  </button>
                </div>
              </div>
              <div className="document-card__row document-card__row--meta">
                <span>{document.file_type.toUpperCase()}</span>
                <span>{formatUploadTime(document.upload_time, locale)}</span>
              </div>
              <div className="document-card__row document-card__row--meta">
                <span>{messages.library.language}: {document.language ?? messages.library.unknown}</span>
                <span>{messages.library.pages}: {document.pages_count ?? "N/A"}</span>
              </div>
              {document.error_message ? (
                <p className="feedback feedback--error">{document.error_message}</p>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

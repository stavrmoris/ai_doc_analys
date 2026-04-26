import { useI18n } from "../i18n";
import type { SummaryMode } from "../types";

type SummaryPanelProps = {
  hasSelection: boolean;
  loading: boolean;
  mode: SummaryMode;
  onModeChange: (mode: SummaryMode) => void;
  onSummarize: () => void | Promise<void>;
  summary: string | null;
  error: string | null;
};

export function SummaryPanel({
  error,
  hasSelection,
  loading,
  mode,
  onModeChange,
  onSummarize,
  summary,
}: SummaryPanelProps) {
  const { messages } = useI18n();
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <p className="eyebrow">{messages.summary.eyebrow}</p>
          <h2>{messages.summary.title}</h2>
        </div>
      </div>
      <div className="stack">
        <div className="mode-toggle" role="group" aria-label="Summary mode">
          <button
            type="button"
            className="secondary-button"
            data-active={mode === "short"}
            aria-pressed={mode === "short"}
            onClick={() => onModeChange("short")}
          >
            {messages.summary.short}
          </button>
          <button
            type="button"
            className="secondary-button"
            data-active={mode === "detailed"}
            aria-pressed={mode === "detailed"}
            onClick={() => onModeChange("detailed")}
          >
            {messages.summary.detailed}
          </button>
        </div>
        <button
          type="button"
          className="primary-button"
          disabled={loading || !hasSelection}
          onClick={() => void onSummarize()}
        >
          {loading ? messages.summary.generating : messages.summary.generate}
        </button>
      </div>
      {!hasSelection ? <p className="empty-state">{messages.summary.empty}</p> : null}
      {error ? <p className="feedback feedback--error">{error}</p> : null}
      {!error && summary ? <article className="summary-card">{summary}</article> : null}
    </section>
  );
}

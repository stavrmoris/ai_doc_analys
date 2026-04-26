import { useCallback, useEffect, useState } from "react";

import { fetchDocuments } from "../lib/api";
import type { DocumentRecord } from "../types";

type UseDocumentsResult = {
  documents: DocumentRecord[];
  documentsLoading: boolean;
  documentsError: string | null;
  refresh: () => Promise<void>;
  selectedDocument: DocumentRecord | null;
  selectedId: number | null;
  setSelectedId: (id: number | null) => void;
};

export function useDocuments(): UseDocumentsResult {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [documentsError, setDocumentsError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    setDocumentsLoading(true);
    setDocumentsError(null);

    try {
      const nextDocuments = await fetchDocuments();
      setDocuments(nextDocuments);
      setSelectedId((currentSelectedId) => {
        if (!nextDocuments.length) {
          return null;
        }

        if (
          currentSelectedId !== null &&
          nextDocuments.some((document) => document.id === currentSelectedId)
        ) {
          return currentSelectedId;
        }

        return nextDocuments[0].id;
      });
    } catch (error) {
      setDocumentsError(error instanceof Error ? error.message : "Unable to load documents.");
    } finally {
      setDocumentsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    documents,
    documentsLoading,
    documentsError,
    refresh,
    selectedDocument: documents.find((document) => document.id === selectedId) ?? null,
    selectedId,
    setSelectedId,
  };
}

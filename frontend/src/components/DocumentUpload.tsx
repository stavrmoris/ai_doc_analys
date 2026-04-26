import { useRef } from "react";

import { useI18n } from "../i18n";
import { uploadDocument } from "../lib/api";
import { useMutationState } from "../hooks/useMutationState";

type DocumentUploadProps = {
  onUploaded: () => Promise<void> | void;
};

export function DocumentUpload({ onUploaded }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const uploadState = useMutationState();
  const { messages } = useI18n();

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    uploadState.start();

    try {
      await uploadDocument(file);
      uploadState.succeed();
      await onUploaded();
    } catch (error) {
      uploadState.fail(error);
    } finally {
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  return (
    <section className="panel panel--compact">
      <div className="panel__header">
        <div>
          <p className="eyebrow">{messages.upload.eyebrow}</p>
          <h2>{messages.upload.title}</h2>
        </div>
      </div>
      <label className="upload-dropzone" htmlFor="document-upload">
        <input
          ref={inputRef}
          id="document-upload"
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          disabled={uploadState.loading}
        />
        <span>{uploadState.loading ? messages.upload.uploading : messages.upload.chooseFile}</span>
        <small>{messages.upload.help}</small>
      </label>
      {uploadState.error ? <p className="feedback feedback--error">{uploadState.error}</p> : null}
    </section>
  );
}

import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { QAPanel } from "./QAPanel";

test("submits question through callback", () => {
  const handleAsk = vi.fn();

  render(<QAPanel answer={null} loading={false} onAsk={handleAsk} />);

  fireEvent.change(screen.getByLabelText(/question/i), {
    target: { value: "What is the term?" },
  });
  fireEvent.click(screen.getByRole("button", { name: /ask/i }));

  expect(handleAsk).toHaveBeenCalledWith("What is the term?");
});

test("clears a drafted question when selected document changes", () => {
  const { rerender } = render(
    <QAPanel answer={null} loading={false} onAsk={() => undefined} selectedDocumentId={1} />,
  );
  const question = screen.getByLabelText(/question/i);

  fireEvent.change(question, {
    target: { value: "What is the term?" },
  });

  expect(question).toHaveValue("What is the term?");

  rerender(<QAPanel answer={null} loading={false} onAsk={() => undefined} selectedDocumentId={2} />);

  expect(screen.getByLabelText(/question/i)).toHaveValue("");
});

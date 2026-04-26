import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { SummaryPanel } from "./SummaryPanel";

test("marks the active summary mode semantically", () => {
  const handleModeChange = vi.fn();

  render(
    <SummaryPanel
      error={null}
      hasSelection
      loading={false}
      mode="short"
      onModeChange={handleModeChange}
      onSummarize={() => undefined}
      summary={null}
    />,
  );

  expect(screen.getByRole("button", { name: /short/i })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: /detailed/i })).toHaveAttribute("aria-pressed", "false");

  fireEvent.click(screen.getByRole("button", { name: /detailed/i }));

  expect(handleModeChange).toHaveBeenCalledWith("detailed");
});

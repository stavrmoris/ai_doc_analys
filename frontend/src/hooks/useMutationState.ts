import { useState } from "react";

import type { MutationState } from "../types";

export function useMutationState(initialLoading = false) {
  const [state, setState] = useState<MutationState>({
    loading: initialLoading,
    error: null,
  });

  return {
    ...state,
    start() {
      setState({
        loading: true,
        error: null,
      });
    },
    succeed() {
      setState({
        loading: false,
        error: null,
      });
    },
    fail(error: unknown) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : "Something went wrong.",
      });
    },
    reset() {
      setState({
        loading: false,
        error: null,
      });
    },
  };
}

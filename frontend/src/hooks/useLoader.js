import { useEffect, useState } from "react";

export function useLoader(fetcher) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err) => {
        if (!cancelled) setState({ data: null, loading: false, error: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [fetcher, attempt]);

  function retry() {
    setState((s) => ({ ...s, loading: true, error: null }));
    setAttempt((a) => a + 1);
  }

  function setData(next) {
    setState((s) => ({
      ...s,
      data: typeof next === "function" ? next(s.data) : next,
    }));
  }

  return { ...state, retry, setData };
}
import { useState, useEffect, useCallback } from 'react'

type AsyncFn<T> = () => Promise<T>

interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => void
}

/**
 * Generic hook for async API calls with loading/error state.
 */
export function useApi<T>(fn: AsyncFn<T>, deps: unknown[] = []): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const execute = useCallback(() => {
    setLoading(true)
    setError(null)
    fn()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    execute()
  }, [execute])

  return { data, loading, error, refetch: execute }
}

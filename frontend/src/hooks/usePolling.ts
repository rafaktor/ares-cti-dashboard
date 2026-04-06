import { useEffect, useRef } from 'react'

/**
 * Calls `callback` immediately (if `immediate` is true) then on every
 * `intervalMs` milliseconds. Cleans up on unmount.
 */
export function usePolling(
  callback: () => void,
  intervalMs: number,
  immediate = true
) {
  const cbRef = useRef(callback)

  // Keep ref current so the interval always calls the latest closure
  useEffect(() => {
    cbRef.current = callback
  })

  useEffect(() => {
    if (immediate) cbRef.current()
    const id = setInterval(() => cbRef.current(), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs, immediate])
}

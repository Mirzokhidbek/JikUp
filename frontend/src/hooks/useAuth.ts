import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { ApiError, api } from '../api/client'
import type { UserOut } from '../api/types'
import { STORAGE_KEY as RESUME_KEY } from './useResume'

export const ME_KEY = ['me'] as const

/** Forget every cached response except the session query, which mounted headers keep watching. */
function forgetData(client: QueryClient) {
  client.removeQueries({ predicate: (query) => query.queryKey[0] !== ME_KEY[0] })
}

/** Called when the server says the session is gone: show the signed-out state everywhere. */
export function signedOut(client: QueryClient) {
  localStorage.removeItem(RESUME_KEY)
  forgetData(client)
  client.setQueryData(ME_KEY, null)
}

/** Only same-site paths are allowed after login, so ?next= cannot send users elsewhere. */
export function safeNext(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') && !next.startsWith('/\\')
    ? next
    : '/'
}

export function useAuth() {
  const client = useQueryClient()
  const me = useQuery({
    queryKey: ME_KEY,
    queryFn: async (): Promise<UserOut | null> => {
      try {
        return await api.auth.me()
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      }
    },
    staleTime: Infinity,
    retry: false,
  })

  const signedIn = (user: UserOut) => {
    // Drop anything cached for a previous account before showing the new one.
    localStorage.removeItem(RESUME_KEY)
    forgetData(client)
    client.setQueryData(ME_KEY, user)
  }

  const login = useMutation({ mutationFn: api.auth.login, onSuccess: signedIn })
  const register = useMutation({ mutationFn: api.auth.register, onSuccess: signedIn })
  const logout = useMutation({ mutationFn: api.auth.logout, onSettled: () => signedOut(client) })

  return { user: me.data ?? null, isPending: me.isPending, login, register, logout }
}

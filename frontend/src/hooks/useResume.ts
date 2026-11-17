import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { ApiError, api } from '../api/client'

const STORAGE_KEY = 'jikup.resume'

export function useResume() {
  const client = useQueryClient()
  const [resumeId, setResumeId] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY))

  const remember = (id: string | null) => {
    if (id) localStorage.setItem(STORAGE_KEY, id)
    else localStorage.removeItem(STORAGE_KEY)
    setResumeId(id)
  }

  const resume = useQuery({
    queryKey: ['resume', resumeId],
    queryFn: async () => {
      try {
        return await api.getResume(resumeId as string)
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) remember(null)
        throw err
      }
    },
    enabled: resumeId !== null,
    retry: false,
  })

  const upload = useMutation({
    mutationFn: api.uploadResume,
    onSuccess: (data) => {
      client.setQueryData(['resume', data.id], data)
      remember(data.id)
    },
  })

  const remove = useMutation({
    mutationFn: (id: string) => api.deleteResume(id),
    onSuccess: (_, id) => {
      client.removeQueries({ queryKey: ['resume', id] })
      remember(null)
    },
  })

  return { resumeId, resume, upload, remove }
}

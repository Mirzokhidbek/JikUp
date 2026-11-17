import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import type { SearchHit } from '../api/types'
import ChatMessage, { type ChatTurn } from '../components/ChatMessage'
import Page from '../components/Page.tsx'
import { focusRing, muted, primaryButton, secondaryButton } from '../components/ui'
import { useEventStream } from '../hooks/useEventStream'
import { useI18n } from '../i18n/useI18n'

const MAX_QUESTION = 500
const EXAMPLES = ['chat.example1', 'chat.example2', 'chat.example3'] as const

export default function ChatPage() {
  const { t } = useI18n()
  const inputId = useId()
  const hintId = useId()
  const [question, setQuestion] = useState('')
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const nextId = useRef(1)
  const activeId = useRef<number | null>(null)
  const lastTurn = useRef<HTMLDivElement>(null)
  const stream = useEventStream()
  const streaming = stream.status === 'streaming'

  const patch = (id: number, change: (turn: ChatTurn) => Partial<ChatTurn>) =>
    setTurns((all) => all.map((turn) => (turn.id === id ? { ...turn, ...change(turn) } : turn)))

  useEffect(() => {
    const id = activeId.current
    if (id === null) return
    if (stream.status === 'stopped') patch(id, () => ({ status: 'stopped' }))
    if (stream.status === 'error')
      patch(id, () => ({ status: 'error', error: stream.error ?? undefined }))
  }, [stream.status, stream.error])

  useEffect(() => {
    lastTurn.current?.scrollIntoView({ block: 'nearest' })
  }, [turns.length])

  const ask = (text: string) => {
    const query = text.trim().slice(0, MAX_QUESTION)
    if (!query || streaming) return
    const id = nextId.current++
    activeId.current = id
    setTurns((all) => [...all, { id, question: query, answer: '', status: 'searching' }])
    setQuestion('')
    void stream.start('/chat', { query, limit: 6 }, ({ event, data }) => {
      if (event === 'filters') patch(id, () => ({ filters: data as ChatTurn['filters'] }))
      else if (event === 'sources')
        patch(id, () => ({ sources: data as SearchHit[], status: 'answering' }))
      else if (event === 'token' && typeof data === 'string')
        patch(id, (turn) => ({ answer: turn.answer + data }))
      else if (event === 'error') patch(id, () => ({ status: 'error' }))
      else if (event === 'done')
        patch(id, (turn) => (turn.status === 'error' ? {} : { status: 'done' }))
    })
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    ask(question)
  }

  return (
    <Page title={t('nav.chat')} lead={t('chat.subtitle')}>
      {turns.length === 0 ? (
        <section className="mt-8" aria-labelledby="examples-heading">
          <h2 id="examples-heading" className={`mb-2 text-sm ${muted}`}>
            {t('chat.examplesTitle')}
          </h2>
          <ul className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {EXAMPLES.map((key) => (
              <li key={key}>
                <button
                  type="button"
                  onClick={() => ask(t(key))}
                  className={`${secondaryButton} w-full justify-start rounded-full text-left font-medium`}
                >
                  {t(key)}
                </button>
              </li>
            ))}
          </ul>
        </section>
      ) : (
        <ol className="mt-8 space-y-8" aria-live="polite" aria-relevant="additions">
          {turns.map((turn) => (
            <ChatMessage key={turn.id} turn={turn} />
          ))}
        </ol>
      )}
      <div ref={lastTurn} />

      <form
        onSubmit={onSubmit}
        className="sticky bottom-0 mt-8 bg-white/90 py-4 backdrop-blur-md dark:bg-slate-950/90"
      >
        <label htmlFor={inputId} className="sr-only">
          {t('chat.inputLabel')}
        </label>
        <div className="flex items-end gap-2">
          <textarea
            id={inputId}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault()
                ask(question)
              }
            }}
            rows={2}
            maxLength={MAX_QUESTION}
            placeholder={t('chat.placeholder')}
            aria-describedby={hintId}
            className={`min-h-11 flex-1 resize-y rounded-xl bg-fill-strong px-4 py-3 text-sm placeholder:text-slate-500 dark:placeholder:text-slate-400 ${focusRing}`}
          />
          {streaming ? (
            <button type="button" onClick={stream.stop} className={secondaryButton}>
              {t('chat.stop')}
            </button>
          ) : (
            <button type="submit" disabled={!question.trim()} className={primaryButton}>
              {t('chat.send')}
            </button>
          )}
        </div>
        <p id={hintId} className={`mt-1 text-xs ${muted}`}>
          {t('chat.hint')}
        </p>
      </form>
    </Page>
  )
}

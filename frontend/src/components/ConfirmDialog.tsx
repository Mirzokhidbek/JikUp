import { useEffect, useId, useRef } from 'react'
import { useI18n } from '../i18n/useI18n'
import { card, focusRing, muted } from './ui'

type Props = {
  open: boolean
  title: string
  body: string
  confirmLabel: string
  onConfirm: () => void
  onClose: () => void
}

const button = `inline-flex min-h-11 items-center rounded-md px-4 text-sm font-medium ${focusRing}`

export default function ConfirmDialog({
  open,
  title,
  body,
  confirmLabel,
  onConfirm,
  onClose,
}: Props) {
  const { t } = useI18n()
  const ref = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  const bodyId = useId()

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      aria-describedby={bodyId}
      onClose={onClose}
      className={`${card} m-auto max-w-sm p-6 text-ink backdrop:bg-black/50 dark:text-slate-100`}
    >
      <h2 id={titleId} className="text-lg font-semibold">
        {title}
      </h2>
      <p id={bodyId} className={`mt-2 text-sm ${muted}`}>
        {body}
      </p>
      <div className="mt-6 flex justify-end gap-2">
        <button
          type="button"
          autoFocus
          onClick={onClose}
          className={`${button} border border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800`}
        >
          {t('copilot.cancel')}
        </button>
        <button
          type="button"
          onClick={onConfirm}
          className={`${button} bg-red-700 text-white hover:bg-red-800`}
        >
          {confirmLabel}
        </button>
      </div>
    </dialog>
  )
}

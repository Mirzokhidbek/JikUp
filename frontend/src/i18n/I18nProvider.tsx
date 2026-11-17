import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { I18nContext, STORAGE_KEY, initialLang, translate, type Lang } from './context'

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(initialLang)

  useEffect(() => {
    document.documentElement.lang = lang
    localStorage.setItem(STORAGE_KEY, lang)
  }, [lang])

  const value = useMemo(() => ({ lang, setLang, t: translate(lang) }), [lang])
  return <I18nContext value={value}>{children}</I18nContext>
}

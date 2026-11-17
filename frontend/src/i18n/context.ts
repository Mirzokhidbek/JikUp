import { createContext } from 'react'
import { en, type MessageKey } from './en'
import { ko } from './ko'
import { uz } from './uz'

export const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'uz', label: "O'zbekcha" },
  { code: 'ko', label: '한국어' },
] as const

export type Lang = (typeof LANGUAGES)[number]['code']
export const MESSAGES = { en, uz, ko }
export const STORAGE_KEY = 'jikup.lang'

export type Translate = (key: MessageKey, vars?: Record<string, string | number>) => string

export type I18nValue = { lang: Lang; setLang: (lang: Lang) => void; t: Translate }

export function isLang(value: string | null): value is Lang {
  return LANGUAGES.some((l) => l.code === value)
}

export function initialLang(): Lang {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (isLang(saved)) return saved
  const browser = navigator.language.slice(0, 2)
  return isLang(browser) ? browser : 'en'
}

export function translate(lang: Lang): Translate {
  return (key, vars) => {
    const text: string = MESSAGES[lang][key] ?? en[key]
    return vars ? text.replace(/\{(\w+)\}/g, (_, name: string) => String(vars[name] ?? '')) : text
  }
}

export const I18nContext = createContext<I18nValue | null>(null)

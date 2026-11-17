import { LANGUAGES, isLang } from '../i18n/context'
import { useI18n } from '../i18n/useI18n'
import { useTheme, type Theme } from '../theme/useTheme'
import { focusRing, iconButton } from './ui'

const THEME_ICONS: Record<Theme, string> = {
  system: 'M4 5h16v11H4zM9 20h6M12 16v4',
  light:
    'M12 4V2m0 20v-2m8-8h2M2 12h2m13.66-5.66 1.41-1.41M4.93 19.07l1.41-1.41m0-11.32L4.93 4.93m14.14 14.14-1.41-1.41M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z',
  dark: 'M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z',
}

export function ThemeToggle() {
  const { t } = useI18n()
  const { theme, cycle } = useTheme()
  const label = t(`theme.${theme}`)
  return (
    <button type="button" onClick={cycle} className={iconButton} aria-label={label} title={label}>
      <svg
        viewBox="0 0 24 24"
        className="size-5"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d={THEME_ICONS[theme]} />
      </svg>
    </button>
  )
}

export function LanguageSelect() {
  const { lang, setLang, t } = useI18n()
  return (
    <label className="flex items-center">
      <span className="sr-only">{t('language.label')}</span>
      <select
        value={lang}
        onChange={(e) => isLang(e.target.value) && setLang(e.target.value)}
        className={`h-11 rounded-lg bg-fill-strong px-2 text-sm ${focusRing}`}
      >
        {LANGUAGES.map(({ code, label }) => (
          <option key={code} value={code}>
            {label}
          </option>
        ))}
      </select>
    </label>
  )
}

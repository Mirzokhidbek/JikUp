import { Link } from 'react-router'
import { useI18n } from '../i18n/useI18n'
import { focusRing } from './ui'

export default function Logo() {
  const { t } = useI18n()
  return (
    <Link
      to="/"
      aria-label={t('nav.home')}
      className={`inline-flex min-h-11 shrink-0 items-center rounded-md ${focusRing}`}
    >
      <img
        src="/logo-light.png"
        alt="JikUp"
        width={480}
        height={164}
        className="h-9 w-auto dark:hidden"
      />
      <img
        src="/logo-dark.png"
        alt="JikUp"
        width={480}
        height={164}
        className="hidden h-9 w-auto dark:block"
      />
    </Link>
  )
}

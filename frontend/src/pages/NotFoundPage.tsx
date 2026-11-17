import { Link } from 'react-router'
import Page from '../components/Page.tsx'
import { link, muted } from '../components/ui'
import { useI18n } from '../i18n/useI18n'

export default function NotFoundPage() {
  const { t } = useI18n()
  return (
    <Page title={t('notFound.title')}>
      <p className={`mt-2 ${muted}`}>
        {t('notFound.body')}{' '}
        <Link to="/search" className={link}>
          {t('notFound.link')}
        </Link>
      </p>
    </Page>
  )
}

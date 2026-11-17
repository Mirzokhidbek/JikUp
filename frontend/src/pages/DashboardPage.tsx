import Page from '../components/Page.tsx'
import { useI18n } from '../i18n/useI18n'

export default function DashboardPage() {
  const { t } = useI18n()
  return <Page title={t('nav.dashboard')} />
}

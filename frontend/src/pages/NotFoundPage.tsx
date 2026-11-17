import { Link } from 'react-router'
import Page from '../components/Page.tsx'

export default function NotFoundPage() {
  return (
    <Page title="Page not found">
      <p className="mt-2 text-slate-600">
        This page does not exist.{' '}
        <Link to="/search" className="font-medium text-brand underline-offset-4 hover:underline">
          Go to job search
        </Link>
      </p>
    </Page>
  )
}

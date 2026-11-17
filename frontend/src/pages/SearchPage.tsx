import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import JobCard from '../components/JobCard'
import Page from '../components/Page.tsx'
import SearchFilters from '../components/SearchFilters'
import { EmptyState, ErrorState, ListSkeleton } from '../components/States'
import { focusRing, muted } from '../components/ui'
import { toQuery, useJobFilters } from '../hooks/useJobFilters'
import { useI18n } from '../i18n/useI18n'
import { PAGE_SIZE } from '../lib/constants'

const pageButton = `min-h-11 rounded-md border border-slate-300 px-4 text-sm font-medium hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-800 ${focusRing}`

export default function SearchPage() {
  const { t } = useI18n()
  const { filters, update, reset } = useJobFilters()
  const query = toQuery(filters)
  const jobs = useQuery({
    queryKey: ['jobs', query],
    queryFn: () => api.getJobs(query),
    placeholderData: keepPreviousData,
  })
  const total = jobs.data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <Page title={t('nav.search')}>
      <p className={`mt-1 ${muted}`}>{t('search.subtitle')}</p>
      <div className="mt-6 grid grid-cols-1 gap-8 lg:grid-cols-[18rem_minmax(0,1fr)]">
        <aside>
          <SearchFilters filters={filters} onChange={update} onReset={reset} />
        </aside>
        <section aria-labelledby="results-heading" aria-busy={jobs.isFetching}>
          <h2 id="results-heading" className={`mb-3 text-sm ${muted}`} aria-live="polite">
            {jobs.data ? t('search.results', { count: total }) : t('common.loading')}
          </h2>
          {jobs.isPending ? (
            <ListSkeleton />
          ) : jobs.isError ? (
            <ErrorState error={jobs.error} onRetry={() => void jobs.refetch()} />
          ) : jobs.data.items.length === 0 ? (
            <EmptyState title={t('search.empty')} hint={t('search.emptyHint')} />
          ) : (
            <>
              <ul className={`space-y-3 ${jobs.isPlaceholderData ? 'opacity-60' : ''}`}>
                {jobs.data.items.map((job) => (
                  <li key={job.id}>
                    <JobCard job={job} />
                  </li>
                ))}
              </ul>
              {pages > 1 && (
                <nav
                  aria-label={t('search.page', { page: filters.page, pages })}
                  className="mt-6 flex items-center justify-between gap-3"
                >
                  <button
                    type="button"
                    className={pageButton}
                    disabled={filters.page <= 1}
                    onClick={() => update({ page: filters.page - 1 })}
                  >
                    {t('search.prev')}
                  </button>
                  <span className={`text-sm ${muted}`}>
                    {t('search.page', { page: filters.page, pages })}
                  </span>
                  <button
                    type="button"
                    className={pageButton}
                    disabled={filters.page >= pages}
                    onClick={() => update({ page: filters.page + 1 })}
                  >
                    {t('search.next')}
                  </button>
                </nav>
              )}
            </>
          )}
        </section>
      </div>
    </Page>
  )
}

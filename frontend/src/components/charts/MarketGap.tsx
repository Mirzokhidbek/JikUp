import { Link } from 'react-router'
import type { SkillShare } from '../../api/types'
import { useResume } from '../../hooks/useResume'
import { useI18n } from '../../i18n/useI18n'
import { marketGap } from '../../lib/marketGap'
import { card, link, muted } from '../ui'

const chip = 'rounded-md px-2 py-0.5 text-sm'

export default function MarketGap({ market }: { market: SkillShare[] }) {
  const { t } = useI18n()
  const { resume } = useResume()
  const skills = resume.data?.parsed.skills

  return (
    <section className={`${card} p-5`} aria-labelledby="market-title">
      <h2 id="market-title" className="font-semibold">
        {t('market.title')}
      </h2>
      {!skills ? (
        <p className={`mt-2 text-sm ${muted}`}>
          {t('market.noResume')}{' '}
          <Link to="/copilot" className={`inline-flex min-h-11 items-center ${link}`}>
            {t('market.toCopilot')}
          </Link>
        </p>
      ) : (
        <MarketLists skills={skills} market={market} />
      )}
    </section>
  )
}

function MarketLists({ skills, market }: { skills: string[]; market: SkillShare[] }) {
  const { t } = useI18n()
  const { owned, missing } = marketGap(skills, market)
  return (
    <>
      <p className={`mt-0.5 text-sm ${muted}`}>{t('market.hint', { n: market.length })}</p>
      <p className="mt-3 text-sm font-medium">
        {t('market.coverage', { have: owned.length, n: market.length })}
      </p>
      <div className="mt-4 grid gap-5 sm:grid-cols-2">
        <section>
          <h3 className="mb-1.5 text-sm font-medium">{t('market.learn')}</h3>
          {missing.length === 0 ? (
            <p className={`text-sm ${muted}`}>-</p>
          ) : (
            <ol className="space-y-1 text-sm">
              {missing.slice(0, 6).map((s) => (
                <li key={s.name} className="flex items-center gap-2">
                  <span aria-hidden="true" className="text-red-700 dark:text-red-300">
                    ✗
                  </span>
                  {t('market.learnItem', { skill: s.name, share: s.share })}
                </li>
              ))}
            </ol>
          )}
        </section>
        <section>
          <h3 className="mb-1.5 text-sm font-medium">{t('market.have')}</h3>
          {owned.length === 0 ? (
            <p className={`text-sm ${muted}`}>{t('market.none')}</p>
          ) : (
            <ul className="flex flex-wrap gap-1.5">
              {owned.map((s) => (
                <li
                  key={s.name}
                  className={`${chip} bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200`}
                >
                  <span aria-hidden="true">✓ </span>
                  {s.name}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </>
  )
}

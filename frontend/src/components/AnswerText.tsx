import { Fragment, type ReactElement } from 'react'
import type { SearchHit } from '../api/types'
import { parseAnswer, type InlineToken } from '../lib/answerText'
import { link } from './ui'

type Props = { text: string; sources: SearchHit[]; anchorPrefix: string }

function Inline({
  tokens,
  titles,
  anchorPrefix,
}: {
  tokens: InlineToken[]
  titles: Map<number, { n: number; title: string }>
  anchorPrefix: string
}) {
  return tokens.map((token, i) => {
    if (token.type === 'bold')
      return (
        <strong key={i}>
          <Inline tokens={token.children} titles={titles} anchorPrefix={anchorPrefix} />
        </strong>
      )
    if (token.type === 'text') return <Fragment key={i}>{token.value}</Fragment>
    const source = titles.get(token.id)
    if (!source) return null
    return (
      <a
        key={i}
        href={`#${anchorPrefix}-${token.id}`}
        aria-label={source.title}
        title={source.title}
        className={`${link} text-sm`}
      >
        [{source.n}]
      </a>
    )
  })
}

export default function AnswerText({ text, sources, anchorPrefix }: Props) {
  const titles = new Map(sources.map((hit, i) => [hit.job.id, { n: i + 1, title: hit.job.title }]))
  const blocks = parseAnswer(text)
  const parts: ReactElement[] = []
  let items: ReactElement[] = []

  const flush = () => {
    if (items.length)
      parts.push(
        <ul key={`ul-${parts.length}`} className="ml-5 list-disc space-y-1">
          {items}
        </ul>,
      )
    items = []
  }

  blocks.forEach((block, i) => {
    const content = <Inline tokens={block.tokens} titles={titles} anchorPrefix={anchorPrefix} />
    if (block.type === 'item') {
      items.push(<li key={i}>{content}</li>)
      return
    }
    flush()
    parts.push(<p key={i}>{content}</p>)
  })
  flush()

  return <div className="space-y-2 leading-relaxed">{parts}</div>
}

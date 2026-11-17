export type InlineToken =
  | { type: 'text'; value: string }
  | { type: 'bold'; children: InlineToken[] }
  | { type: 'job'; id: number }

export type Block = { type: 'paragraph' | 'item'; tokens: InlineToken[] }

const BOLD = /\*\*(.+?)\*\*/g
const JOB = /\[job:(\d+)\]/g
const LIST_ITEM = /^\s*(?:[-*•]|\d+[.)])\s+/

function split(
  text: string,
  pattern: RegExp,
  onMatch: (match: RegExpMatchArray) => InlineToken,
  onText: (value: string) => InlineToken[],
): InlineToken[] {
  const tokens: InlineToken[] = []
  let last = 0
  for (const match of text.matchAll(pattern)) {
    if (match.index > last) tokens.push(...onText(text.slice(last, match.index)))
    tokens.push(onMatch(match))
    last = match.index + match[0].length
  }
  if (last < text.length) tokens.push(...onText(text.slice(last)))
  return tokens
}

function citations(text: string): InlineToken[] {
  return split(
    text,
    JOB,
    (m) => ({ type: 'job', id: Number(m[1]) }),
    (value) => [{ type: 'text', value }],
  )
}

export function tokenizeInline(text: string): InlineToken[] {
  return split(text, BOLD, (m) => ({ type: 'bold', children: citations(m[1]) }), citations)
}

export function parseAnswer(text: string): Block[] {
  return text
    .split('\n')
    .map((line) => line.trimEnd())
    .filter((line) => line.trim() !== '')
    .map((line) =>
      LIST_ITEM.test(line)
        ? { type: 'item', tokens: tokenizeInline(line.replace(LIST_ITEM, '')) }
        : { type: 'paragraph', tokens: tokenizeInline(line.replace(/^#+\s*/, '')) },
    )
}

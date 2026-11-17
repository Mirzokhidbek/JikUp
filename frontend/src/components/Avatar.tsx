import { displayName } from '../lib/user'

export default function Avatar({ email, size = 40 }: { email: string; size?: number }) {
  return (
    <span
      aria-hidden="true"
      style={{ width: size, height: size }}
      className="flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#3f7bff] to-[#1443e2] text-[15px] font-bold text-white"
    >
      {displayName(email).charAt(0)}
    </span>
  )
}

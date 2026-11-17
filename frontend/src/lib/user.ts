/** "aziz.karimov@x.com" -> "Aziz" */
export function displayName(email: string): string {
  const first = email.split('@')[0].split(/[._+-]/)[0] || email
  return first.charAt(0).toUpperCase() + first.slice(1)
}

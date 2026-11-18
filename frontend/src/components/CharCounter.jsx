export default function CharCounter({ length, max }) {
  const ratio = length / max
  const tone = ratio >= 1 ? 'char-counter--limit' : ratio >= 0.9 ? 'char-counter--near' : ''
  return (
    <span className={`char-counter ${tone}`} aria-live="polite">
      {length} / {max}
    </span>
  )
}

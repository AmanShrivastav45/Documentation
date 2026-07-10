const STYLES = {
  info: 'border-link-blue/40 bg-surface-light-gray text-text-primary',
  warning: 'border-badge-warning-text/40 bg-badge-warning-bg text-badge-warning-text',
  error: 'border-red-300 bg-red-50 text-red-900',
  success: 'border-green-300 bg-green-50 text-green-900',
}

export default function Callout({ type = 'info', children }) {
  const styles = STYLES[type] ?? STYLES.info
  return (
    <div
      role="note"
      data-callout-type={type}
      className={`not-prose my-4 rounded-md border-l-4 p-4 font-body ${styles}`}
    >
      {children}
    </div>
  )
}

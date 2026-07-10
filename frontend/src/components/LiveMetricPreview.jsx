const DEFAULT_DATA = [42, 55, 61, 58, 70, 76, 83, 88]

export default function LiveMetricPreview({ threshold, data = DEFAULT_DATA }) {
  const current = data[data.length - 1]
  const isOverThreshold = current > threshold
  const max = Math.max(...data, threshold)

  return (
    <div className="not-prose my-4 rounded-md border border-border-subtle p-4 font-body">
      <div className="mb-2 flex items-center justify-between text-sm text-text-secondary">
        <span>Current value</span>
        <span
          data-testid="current-value"
          className={`font-semibold ${isOverThreshold ? 'text-red-600' : 'text-green-600'}`}
        >
          {current}
        </span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-surface-light-gray">
        <div
          data-testid="gauge-bar"
          className={`h-full ${isOverThreshold ? 'bg-red-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min((current / max) * 100, 100)}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-text-muted">Threshold: {threshold}</p>
    </div>
  )
}

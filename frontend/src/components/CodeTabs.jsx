import { useState } from 'react'

export default function CodeTabs({ tabs }) {
  const [activeIndex, setActiveIndex] = useState(0)
  const active = tabs[activeIndex]

  return (
    <div className="not-prose my-4 overflow-hidden rounded-md border border-border-subtle font-body">
      <div role="tablist" className="flex border-b border-border-light bg-surface-light-gray">
        {tabs.map((tab, index) => (
          <button
            key={tab.label}
            role="tab"
            type="button"
            aria-selected={index === activeIndex}
            onClick={() => setActiveIndex(index)}
            className={`px-4 py-2 text-sm font-medium ${
              index === activeIndex
                ? 'border-b-2 border-link-blue text-link-blue'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <pre className="overflow-x-auto bg-text-strong p-4 text-sm text-surface-white">
        <code>{active.code}</code>
      </pre>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { collectAncestorIds, docPathToRoute } from '../lib/docsTree.js'

function TreeNode({ node, expandedIds, onToggle }) {
  const isFolder = Array.isArray(node.children)

  if (!isFolder) {
    return (
      <li>
        <NavLink
          to={docPathToRoute(node.path)}
          className={({ isActive }) =>
            `block rounded-md px-3 py-2 text-sm ${
              isActive
                ? 'bg-surface-white font-medium text-link-blue'
                : 'text-text-primary hover:bg-surface-white'
            }`
          }
        >
          {node.label}
        </NavLink>
      </li>
    )
  }

  const isExpanded = expandedIds.has(node.id)
  return (
    <li>
      <button
        type="button"
        onClick={() => onToggle(node.id)}
        aria-expanded={isExpanded}
        className="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-white"
      >
        {node.label}
        <span aria-hidden="true">{isExpanded ? '▾' : '▸'}</span>
      </button>
      {isExpanded && (
        <ul className="ml-3 space-y-1 border-l border-border-light pl-2">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} expandedIds={expandedIds} onToggle={onToggle} />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function DocsSidebar({ tree, activePath }) {
  const [expandedIds, setExpandedIds] = useState(
    () => new Set(collectAncestorIds(tree, activePath) ?? []),
  )

  useEffect(() => {
    const ancestors = collectAncestorIds(tree, activePath)
    if (!ancestors || ancestors.length === 0) return
    setExpandedIds((prev) => {
      const next = new Set(prev)
      for (const id of ancestors) next.add(id)
      return next
    })
  }, [tree, activePath])

  function toggle(id) {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  return (
    <aside className="w-64 shrink-0 border-r border-border-subtle bg-surface-light-gray p-4">
      <nav>
        <ul className="space-y-1">
          {tree.map((node) => (
            <TreeNode key={node.id} node={node} expandedIds={expandedIds} onToggle={toggle} />
          ))}
        </ul>
      </nav>
    </aside>
  )
}

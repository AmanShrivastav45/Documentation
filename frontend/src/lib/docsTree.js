export function docPathToRoute(path) {
  return '/docs/' + path.replace(/\.mdx$/, '')
}

export function routeToDocPath(pathname) {
  return pathname.startsWith('/docs/') ? pathname.slice('/docs/'.length) + '.mdx' : null
}

export function collectAncestorIds(nodes, targetPath, trail = []) {
  for (const node of nodes) {
    if (node.path === targetPath) {
      return trail
    }
    if (node.children) {
      const found = collectAncestorIds(node.children, targetPath, [...trail, node.id])
      if (found) return found
    }
  }
  return null
}

export function findNodeLabel(nodes, targetPath) {
  for (const node of nodes) {
    if (node.path === targetPath) {
      return node.label
    }
    if (node.children) {
      const found = findNodeLabel(node.children, targetPath)
      if (found) return found
    }
  }
  return null
}

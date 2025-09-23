export function parseLegalProvisionLink(provision) {
  const parts = provision.trim().split(' ')
  return {
    instrumentId: parts[0],
    articleId: parts.slice(1).join(''),
  }
}

export function generateLegalProvisionLink(provision) {
  const { instrumentId, articleId } = parseLegalProvisionLink(provision)
  return `/domestic-instrument/${instrumentId}#${articleId}`
}

export function getProvisionClass(content, defaultClass) {
  return content.length > 45 ? 'result-value-small' : defaultClass
}

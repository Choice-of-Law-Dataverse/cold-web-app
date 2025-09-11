// server/api/check-pdf-exists.ts
export default defineEventHandler(async (event) => {
  const { url } = getQuery(event)

  if (!url || typeof url !== 'string') {
    return { exists: false }
  }

  try {
    const res = await fetch(url, { method: 'HEAD' })
    return { exists: res.ok }
  } catch (e) {
    return { exists: false }
  }
})

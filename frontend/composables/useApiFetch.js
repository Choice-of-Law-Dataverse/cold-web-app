import { ref } from 'vue'

export function useApiFetch() {
    const loading = ref(true)
    const error = ref(null)
    const data = ref(null)

    const fetchData = async ({ table, id }) => {
        loading.value = true
        error.value = null

        const config = useRuntimeConfig()
        const jsonPayload = { table, id }

        try {
            const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
                method: 'POST',
                headers: {
                    authorization: `Bearer ${config.public.FASTAPI}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jsonPayload),
            })

            if (!response.ok) throw new Error(`Failed to fetch ${table}`)

            data.value = await response.json()
            return data.value
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'An error occurred'
            throw err
        } finally {
            loading.value = false
        }
    }

    return {
        loading,
        error,
        data,
        fetchData,
    }
} 
import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api, apiError } from '../api'

const AppContext = createContext(null)
export const useApp = () => useContext(AppContext)

export function AppProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('supersede-theme') || 'light')
  const [packs, setPacks] = useState([])
  const [activePack, setActivePack] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [backendOnline, setBackendOnline] = useState(false)

  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem('supersede-theme', theme) }, [theme])
  const refreshPacks = async () => {
    setLoading(true); setError('')
    try { const [health, packsResponse] = await Promise.all([api.health(), api.packs()]); setBackendOnline(health.data.status === 'ok'); setPacks(packsResponse.data) }
    catch (err) { setBackendOnline(false); setError(apiError(err)) }
    finally { setLoading(false) }
  }
  const loadPack = async (id) => {
    setLoading(true); setError('')
    try { const { data } = await api.pack(id); setActivePack({ pack_id: id, ...data }); return data }
    catch (err) { setError(apiError(err)); throw err }
    finally { setLoading(false) }
  }
  useEffect(() => { refreshPacks() }, [])
  const value = useMemo(() => ({ theme, setTheme, packs, setPacks, activePack, setActivePack, loading, error, setError, backendOnline, refreshPacks, loadPack }), [theme, packs, activePack, loading, error, backendOnline])
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

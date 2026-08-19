import { useState, useEffect } from 'react'
import { getWeather } from '../api'
import AppShell from '../components/AppShell'
import { Cloud, RefreshCw, Wind } from 'lucide-react'

export default function Weather() {
    const [cities, setCities] = useState([])
    const [stale, setStale] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(true)

    async function load() {
        setLoading(true)
        try {
            const res = await getWeather()
            setCities(res.data.cities)
            setStale(res.data.stale)
            setError(res.data.error || '')
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load weather')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        load()
        const interval = setInterval(load, 300000)  // matches backend TTL
        return () => clearInterval(interval)
    }, [])

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Weather</h1>
                    <p className="page-subtitle">
                        {stale ? 'Showing last known conditions (refresh delayed)' : 'Updated every 5 minutes'}
                    </p>
                </div>
                <button className="btn btn-secondary" onClick={load}>
                    <RefreshCw size={16} /> Refresh
                </button>
            </div>

            {error && !cities.length && <div className="alert alert-error">{error}</div>}

            {loading && !cities.length ? (
                <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
            ) : (
                <div className="dash-grid">
                    {cities.map(c => (
                        <div key={c.city} className="card">
                            <p className="card-title">{c.city}</p>
                            <div className="balance-line">
                                <span className="balance-amount">{c.temperature_c}°C</span>
                            </div>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                <Cloud size={14} /> {c.condition}
                            </p>
                            <p style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem' }}>
                                <Wind size={13} /> {c.windspeed_kmh} km/h
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </AppShell>
    )
}
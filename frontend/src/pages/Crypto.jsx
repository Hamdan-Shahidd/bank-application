import { useState, useEffect } from 'react'
import { getCryptoPrices } from '../api'
import AppShell from '../components/AppShell'
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react'

export default function Crypto() {
    const [prices, setPrices] = useState([])
    const [stale, setStale] = useState(false)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(true)

    async function load() {
        setLoading(true)
        try {
            const res = await getCryptoPrices()
            setPrices(res.data.prices)
            setStale(res.data.stale)
            setError(res.data.error || '')
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load prices')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        load()
        const interval = setInterval(load, 30000)  // matches backend TTL
        return () => clearInterval(interval)
    }, [])

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Crypto Prices</h1>
                    <p className="page-subtitle">
                        {stale ? 'Showing last known prices (refresh delayed)' : 'Updated every 30 seconds'}
                    </p>
                </div>
                <button className="btn btn-secondary" onClick={load}>
                    <RefreshCw size={16} /> Refresh
                </button>
            </div>

            {error && !prices.length && <div className="alert alert-error">{error}</div>}

            {loading && !prices.length ? (
                <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
            ) : (
                <div className="dash-grid">
                    {prices.map(p => (
                        <div key={p.symbol} className="card">
                            <p className="card-title">{p.symbol}</p>
                            <div className="balance-line">
                                <span className="balance-amount">${p.price_usd.toLocaleString()}</span>
                            </div>
                            <p className={p.change_pct_today >= 0 ? 'history-amount--in' : 'history-amount--out'}>
                                {p.change_pct_today >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                {' '}{p.change_pct_today >= 0 ? '+' : ''}{p.change_pct_today}% today
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </AppShell>
    )
}
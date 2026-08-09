import { useState, useEffect } from 'react'
import { getMe, getHistory } from '../api'
import AppShell from '../components/AppShell'
import { ArrowDownToLine, ArrowUpFromLine, ArrowLeftRight, ArrowDownLeft, ArrowUpRight } from 'lucide-react'

function buildWeekChart(history) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const today = new Date()
    const buckets = []

    for (let i = 6; i >= 0; i--) {
        const d = new Date(today)
        d.setDate(today.getDate() - i)
        buckets.push({ label: days[d.getDay()], dateStr: d.toISOString().slice(0, 10), total: 0 })
    }

    history.forEach(tx => {
        const txDate = (tx.created_at || '').slice(0, 10)
        const bucket = buckets.find(b => b.dateStr === txDate)
        if (bucket) bucket.total += tx.amount
    })

    const max = Math.max(...buckets.map(b => b.total), 1)
    return buckets.map(b => ({ ...b, heightPct: Math.max((b.total / max) * 100, 3) }))
}

export default function Dashboard() {
    const [user, setUser] = useState(null)
    const [history, setHistory] = useState([])
    const [error, setError] = useState('')

    useEffect(() => {
        getMe().then(res => setUser(res.data)).catch(() => setError('Failed to load account'))
        getHistory().then(res => setHistory(res.data)).catch(() => {})
    }, [])

    if (!user) {
        return <AppShell><p style={{ color: 'var(--text-secondary)' }}>Loading...</p></AppShell>
    }

    const chart = buildWeekChart(history)
    const maxTotal = Math.max(...chart.map(c => c.total))

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Overview</h1>
                    <p className="page-subtitle">Welcome back, {user.username}. Here's your account.</p>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="card">
                <p className="balance-label">Total Balance</p>
                <div className="balance-line">
                    <span className="balance-amount">{user.balance_display}</span>
                </div>
                <p className="balance-account">Account · {user.account_number}</p>
                <div className="balance-actions">
                    <a href="/deposit" className="btn btn-primary"><ArrowDownToLine size={16} /> Deposit</a>
                    <a href="/withdraw" className="btn btn-secondary"><ArrowUpFromLine size={16} /> Withdraw</a>
                    <a href="/transfer" className="btn btn-secondary"><ArrowLeftRight size={16} /> Transfer</a>
                </div>
            </div>

            <div className="dash-grid">
                <div className="card">
                    <p className="card-title">Activity — Last 7 Days</p>
                    <div className="chart-bars">
                        {chart.map((c, i) => (
                            <div key={i} className="chart-bar-col">
                                <div
                                    className={`chart-bar ${c.total === maxTotal && maxTotal > 0 ? 'highlight' : ''}`}
                                    style={{ height: `${c.heightPct}%` }}
                                    title={`PKR ${(c.total / 100).toFixed(2)}`}
                                />
                                <span className="chart-bar-label">{c.label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="card">
                    <p className="card-title">Recent Transactions</p>
                    {history.length === 0 ? (
                        <div className="empty-state">No transactions yet.</div>
                    ) : (
                        <div className="history-list">
                            {history.slice(0, 5).map(tx => {
                                const isIncoming = tx.recipient_id === user.user_id
                                return (
                                    <div key={tx.id} className="history-row">
                                        <div className={`history-icon ${isIncoming ? 'history-icon--in' : 'history-icon--out'}`}>
                                            {isIncoming ? <ArrowDownLeft size={15} /> : <ArrowUpRight size={15} />}
                                        </div>
                                        <div className="history-body">
                                            <p className="history-kind">{tx.kind}</p>
                                            <p className="history-date">{tx.created_at?.slice(0, 10)}</p>
                                        </div>
                                        <p className={`history-amount ${isIncoming ? 'history-amount--in' : 'history-amount--out'}`}>
                                            {isIncoming ? '+' : '−'} PKR {(tx.amount / 100).toFixed(2)}
                                        </p>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </div>
        </AppShell>
    )
}
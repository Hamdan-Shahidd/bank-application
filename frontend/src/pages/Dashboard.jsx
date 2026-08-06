import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getMe, getHistory } from '../api'

export default function Dashboard() {
    const [user, setUser] = useState(null)
    const [history, setHistory] = useState([])
    const [error, setError] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        getMe().then(res => setUser(res.data)).catch(() => setError('Failed to load account'))
        getHistory().then(res => setHistory(res.data)).catch(() => {})
    }, [])

    function logout() {
        localStorage.removeItem('token')
        navigate('/login')
    }

    if (!user) return <div className="ledger-page"><p>Loading...</p></div>

    return (
        <div className="ledger-page">
            <div className="ledger-card ledger-card--wide">
                <div className="ledger-topbar">
                    <div>
                        <p className="ledger-wordmark">Ledger</p>
                        <span className="ledger-account-no">Acct. {user.account_number}</span>
                    </div>
                    <button className="ledger-button ledger-button--ghost" onClick={logout}>
                        Log out
                    </button>
                </div>

                {error && <div className="ledger-error">{error}</div>}

                <p className="ledger-balance-label">Hello, {user.username} — your balance</p>
                <p className="ledger-balance">{user.balance_display}</p>

                <ul className="ledger-nav">
                    <li><Link to="/deposit">Deposit</Link></li>
                    <li><Link to="/withdraw">Withdraw</Link></li>
                    <li><Link to="/transfer">Transfer</Link></li>
                    <li><Link to="/assistant">Ask the assistant</Link></li>
                </ul>

                <p className="ledger-balance-label">Recent entries</p>
                {history.length === 0 && <p className="ledger-footer-text">Nothing recorded yet.</p>}
                {history.map(tx => (
                    <div key={tx.id} className="ledger-history-row">
                        <span>{tx.kind} · {tx.created_at?.slice(0, 10)}</span>
                        <span className={`ledger-history-amount ${tx.recipient_id === user.user_id ? 'ledger-history-amount--in' : 'ledger-history-amount--out'}`}>
                            {tx.recipient_id === user.user_id ? '+' : '−'} PKR {(tx.amount / 100).toFixed(2)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    )
}
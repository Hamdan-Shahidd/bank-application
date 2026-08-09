import { useState, useEffect } from 'react'
import { getMe, withdraw } from '../api'
import AppShell from '../components/AppShell'
import { ArrowUpFromLine } from 'lucide-react'

export default function Withdraw() {
    const [balance, setBalance] = useState(null)
    const [amount, setAmount] = useState('')
    const [done, setDone] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        getMe().then(res => setBalance(res.data.balance_display)).catch(() => {})
    }, [])

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        const parsed = parseInt(amount)
        if (!parsed || parsed <= 0) {
            setError('Enter a whole number greater than 0')
            return
        }
        try {
            await withdraw(parsed)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Withdrawal failed')
        }
    }

    if (done) {
        return (
            <AppShell>
                <div className="card success-panel" style={{ maxWidth: 420 }}>
                    <svg className="success-check" viewBox="0 0 52 52">
                        <circle cx="26" cy="26" r="24" />
                        <path d="M14 27l7 7 16-16" />
                    </svg>
                    <p className="success-title">Withdrawal successful</p>
                    <p className="success-detail">Your balance has been updated.</p>
                    <a href="/dashboard" className="btn btn-secondary">Back to overview</a>
                </div>
            </AppShell>
        )
    }

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Withdrawal</h1>
                    <p className="page-subtitle">Take money out of your account.</p>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="card" style={{ maxWidth: 420 }}>
                {balance && (
                    <div className="review-row" style={{ marginBottom: '0.75rem' }}>
                        <span className="review-row-label">Available Balance</span>
                        <span className="review-row-value">{balance}</span>
                    </div>
                )}
                <form onSubmit={handleSubmit}>
                    <div className="field">
                        <label htmlFor="amount">Amount</label>
                        <input id="amount" type="number" min="1" placeholder="0.00" value={amount} onChange={e => setAmount(e.target.value)} required />
                    </div>
                    <button type="submit" className="btn btn-primary btn-full">
                        <ArrowUpFromLine size={16} /> Confirm Withdrawal
                    </button>
                </form>
            </div>
        </AppShell>
    )
}
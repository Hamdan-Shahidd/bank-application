import { useState, useEffect } from 'react'
import { getMe, transfer } from '../api'
import AppShell from '../components/AppShell'
import { ArrowLeftRight } from 'lucide-react'

export default function Transfer() {
    const [user, setUser] = useState(null)
    const [account, setAccount] = useState('')
    const [amount, setAmount] = useState('')
    const [done, setDone] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        getMe().then(res => setUser(res.data)).catch(() => {})
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
            await transfer(account, parsed)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
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
                    <p className="success-title">Transfer complete</p>
                    <p className="success-detail">Your money is on its way.</p>
                    <a href="/dashboard" className="btn btn-secondary">Back to overview</a>
                </div>
            </AppShell>
        )
    }

    const parsedAmount = parseInt(amount) || 0
    const balanceAfter = user ? (user.balance - parsedAmount * 100) / 100 : null

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Move Money</h1>
                    <p className="page-subtitle">Securely transfer funds to another account.</p>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="dash-grid" style={{ gridTemplateColumns: '1.3fr 1fr' }}>
                <div className="card">
                    <p className="card-title">Transfer Details</p>
                    <form onSubmit={handleSubmit}>
                        <div className="field">
                            <label htmlFor="account">Recipient account number</label>
                            <input id="account" value={account} onChange={e => setAccount(e.target.value)} required />
                        </div>
                        <div className="field">
                            <label htmlFor="amount">Amount</label>
                            <input id="amount" type="number" min="1" value={amount} onChange={e => setAmount(e.target.value)} required />
                            <div className="field-quick-amounts">
                                <button type="button" className="chip-btn" onClick={() => setAmount('100')}>PKR 100</button>
                                <button type="button" className="chip-btn" onClick={() => setAmount('500')}>PKR 500</button>
                                <button type="button" className="chip-btn" onClick={() => setAmount('1000')}>PKR 1,000</button>
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary btn-full">
                            <ArrowLeftRight size={16} /> Confirm Transfer
                        </button>
                    </form>
                </div>

                <div className="card">
                    <p className="card-title">Transfer Summary</p>
                    <div className="review-row">
                        <span className="review-row-label">From</span>
                        <span className="review-row-value">{user?.account_number || '—'}</span>
                    </div>
                    <div className="review-row">
                        <span className="review-row-label">To</span>
                        <span className="review-row-value">{account || '—'}</span>
                    </div>
                    <div className="review-row">
                        <span className="review-row-label">Amount</span>
                        <span className="review-row-value">{parsedAmount > 0 ? `PKR ${parsedAmount.toFixed(2)}` : '—'}</span>
                    </div>
                    <div className="review-row">
                        <span className="review-row-label">Balance after transfer</span>
                        <span className="review-row-value">{balanceAfter !== null ? `PKR ${balanceAfter.toFixed(2)}` : '—'}</span>
                    </div>
                </div>
            </div>
        </AppShell>
    )
}
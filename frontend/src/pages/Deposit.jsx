import { useState } from 'react'
import { deposit } from '../api'
import AppShell from '../components/AppShell'
import { ArrowDownToLine } from 'lucide-react'

export default function Deposit() {
    const [amount, setAmount] = useState('')
    const [done, setDone] = useState(false)
    const [error, setError] = useState('')

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        const parsed = parseInt(amount)
        if (!parsed || parsed <= 0) {
            setError('Enter a whole number greater than 0')
            return
        }
        try {
            await deposit(parsed)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Deposit failed')
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
                    <p className="success-title">Deposit successful</p>
                    <p className="success-detail">Your balance has been updated.</p>
                    <a href="/dashboard" className="btn btn-secondary">Back to overview</a>
                </div>
            </AppShell>
        )
    }

    const parsedAmount = parseInt(amount) || 0

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Make a Deposit</h1>
                    <p className="page-subtitle">Add funds to your account.</p>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="card" style={{ maxWidth: 420 }}>
                <form onSubmit={handleSubmit}>
                    <div className="field">
                        <label htmlFor="amount">Deposit Amount (PKR)</label>
                        <input id="amount" type="number" min="1" placeholder="0.00" value={amount} onChange={e => setAmount(e.target.value)} required />
                        <div className="field-quick-amounts">
                            <button type="button" className="chip-btn" onClick={() => setAmount('100')}>PKR 100</button>
                            <button type="button" className="chip-btn" onClick={() => setAmount('500')}>PKR 500</button>
                            <button type="button" className="chip-btn" onClick={() => setAmount('1000')}>PKR 1,000</button>
                        </div>
                    </div>

                    {parsedAmount > 0 && (
                        <div className="review-row">
                            <span className="review-row-label">Amount to deposit</span>
                            <span className="review-row-value">PKR {parsedAmount.toFixed(2)}</span>
                        </div>
                    )}

                    <div style={{ marginTop: '1rem' }}>
                        <button type="submit" className="btn btn-primary btn-full">
                            <ArrowDownToLine size={16} /> Deposit
                        </button>
                    </div>
                </form>
            </div>
        </AppShell>
    )
}
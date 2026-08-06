import { useState } from 'react'
import { withdraw } from '../api'

export default function Withdraw() {
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
            await withdraw(parsed)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Withdrawal failed')
        }
    }

    if (done) {
        return (
            <div className="ledger-page">
                <div className="ledger-card" style={{ textAlign: 'center' }}>
                    <h1 className="ledger-title">Recorded</h1>
                    <div className="stamp-wrap">
                        <div className="stamp-badge">Withdrawal<br />Complete</div>
                    </div>
                    <a className="ledger-link" href="/dashboard">Back to ledger</a>
                </div>
            </div>
        )
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <h1 className="ledger-title">Withdraw</h1>
                {error && <div className="ledger-error">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="ledger-field">
                        <label htmlFor="amount">Amount</label>
                        <input id="amount" type="number" min="1" value={amount} onChange={e => setAmount(e.target.value)} required />
                    </div>
                    <button type="submit" className="ledger-button ledger-button--full">Withdraw</button>
                </form>
                <p className="ledger-footer-text"><a className="ledger-link" href="/dashboard">Cancel</a></p>
            </div>
        </div>
    )
}
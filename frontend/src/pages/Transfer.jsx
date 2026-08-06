import { useState } from 'react'
import { transfer } from '../api'

export default function Transfer() {
    const [account, setAccount] = useState('')
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
            await transfer(account, parsed)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    if (done) {
        return (
            <div className="ledger-page">
                <div className="ledger-card" style={{ textAlign: 'center' }}>
                    <h1 className="ledger-title">Recorded</h1>
                    <div className="stamp-wrap">
                        <div className="stamp-badge">Transfer<br />Complete</div>
                    </div>
                    <a className="ledger-link" href="/dashboard">Back to ledger</a>
                </div>
            </div>
        )
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <h1 className="ledger-title">Transfer</h1>
                {error && <div className="ledger-error">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="ledger-field">
                        <label htmlFor="account">Recipient account number</label>
                        <input id="account" value={account} onChange={e => setAccount(e.target.value)} required />
                    </div>
                    <div className="ledger-field">
                        <label htmlFor="amount">Amount</label>
                        <input id="amount" type="number" min="1" value={amount} onChange={e => setAmount(e.target.value)} required />
                    </div>
                    <button type="submit" className="ledger-button ledger-button--full">Send</button>
                </form>
                <p className="ledger-footer-text"><a className="ledger-link" href="/dashboard">Cancel</a></p>
            </div>
        </div>
    )
}
import { useState } from 'react'
import { sendMessage, confirmTransfer } from '../api'

export default function Assistant() {
    const [input, setInput] = useState('')
    const [reply, setReply] = useState('')
    const [proposal, setProposal] = useState(null)
    const [details, setDetails] = useState(null)
    const [done, setDone] = useState(false)
    const [error, setError] = useState('')

    async function handleSend(e) {
        e.preventDefault()
        setError('')
        setReply('')
        setProposal(null)
        setDetails(null)

        try {
            const res = await sendMessage(input)
            const { kind, text, proposal: p, details: d } = res.data

            if (kind === 'proposal' || kind === 'propose_transfer') setProposal(p)
            else if (kind === 'account_details' || kind === 'get_account_details') setDetails(d)
            else setReply(text)

            setInput('')
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong')
        }
    }

    async function handleConfirm() {
        try {
            await confirmTransfer(proposal.recipient_account, proposal.amount)
            setProposal(null)
            setDone(true)
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <p className="ledger-wordmark">Ledger</p>
                <h1 className="ledger-title">Ask the assistant</h1>

                {error && <div className="ledger-error">{error}</div>}

                {done ? (
                    <div style={{ textAlign: 'center' }}>
                        <div className="stamp-wrap">
                            <div className="stamp-badge">Transfer<br />Complete</div>
                        </div>
                        <button className="ledger-button ledger-button--ghost" onClick={() => setDone(false)}>
                            Ask something else
                        </button>
                    </div>
                ) : (
                    <>
                        <form onSubmit={handleSend}>
                            <div className="ledger-field">
                                <label htmlFor="msg">Message</label>
                                <input
                                    id="msg"
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    placeholder="e.g. send 500 to 1234567890"
                                    required
                                />
                            </div>
                            <button type="submit" className="ledger-button ledger-button--full">Send</button>
                        </form>

                        {reply && <div className="ledger-success">{reply}</div>}

                        {details && (
                            <div className="ledger-success">
                                <strong>{details.username}</strong><br />
                                Acct. {details.account_number}<br />
                                Balance: PKR {(details.balance / 100).toFixed(2)}
                            </div>
                        )}

                        {proposal && (
                            <div className="ledger-error" style={{ background: 'var(--stamp-tint)', color: 'var(--stamp-dark)', borderLeftColor: 'var(--stamp)' }}>
                                Send {proposal.amount} to account {proposal.recipient_account}?
                                <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                                    <button className="ledger-button" onClick={handleConfirm}>Confirm</button>
                                    <button className="ledger-button ledger-button--ghost" onClick={() => setProposal(null)}>Cancel</button>
                                </div>
                            </div>
                        )}
                    </>
                )}

                <p className="ledger-footer-text"><a className="ledger-link" href="/dashboard">Back to ledger</a></p>
            </div>
        </div>
    )
}
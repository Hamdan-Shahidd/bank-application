import { useState, useRef, useEffect } from 'react'
import { sendMessage, confirmTransfer } from '../api'

export default function Assistant() {
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState([])
    const [error, setError] = useState('')
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    async function handleSend(e) {
        e.preventDefault()
        setError('')

        const question = input
        setInput('')

        const userMsg = { id: Date.now(), role: 'user', text: question }
        setMessages(prev => [...prev, userMsg])

        try {
            const res = await sendMessage(question)
            const { kind, text, proposal, details } = res.data

            const assistantMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                kind: kind === 'proposal' || kind === 'propose_transfer' ? 'proposal' : kind,
                text,
                proposal,
                details,
                confirmed: false,
            }
            setMessages(prev => [...prev, assistantMsg])
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong')
        }
    }

    async function handleConfirm(msgId, proposal) {
        try {
            await confirmTransfer(proposal.recipient_account, proposal.amount)
            setMessages(prev =>
                prev.map(m => m.id === msgId ? { ...m, confirmed: true } : m)
            )
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    function handleCancel(msgId) {
        setMessages(prev =>
            prev.map(m => m.id === msgId ? { ...m, cancelled: true } : m)
        )
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <p className="ledger-wordmark">Ledger</p>
                <h1 className="ledger-title">Ask the assistant</h1>

                {error && <div className="ledger-error">{error}</div>}

                <div className="ledger-chat">
                    {messages.length === 0 && (
                        <p className="ledger-chat-empty">
                            Ask about your balance, transactions, HBL policies, or send money.
                        </p>
                    )}

                    {messages.map(msg => (
                        <div
                            key={msg.id}
                            className={`chat-entry chat-entry--${msg.role}`}
                        >
                            {msg.role === 'user' ? (
                                <>
                                    <p className="chat-label">You asked</p>
                                    <p className="chat-text">{msg.text}</p>
                                </>
                            ) : (
                                <>
                                    <p className="chat-label">Ledger</p>

                                    {msg.kind === 'text' && (
                                        <p className="chat-text">{msg.text}</p>
                                    )}

                                    {(msg.kind === 'account_details' || msg.kind === 'get_account_details') && msg.details && (
                                        <p className="chat-text">
                                            <strong>{msg.details.username}</strong><br />
                                            Acct. {msg.details.account_number}<br />
                                            Balance: PKR {(msg.details.balance / 100).toFixed(2)}
                                        </p>
                                    )}

                                    {msg.kind === 'proposal' && msg.proposal && !msg.confirmed && !msg.cancelled && (
                                        <div className="chat-proposal">
                                            Send {msg.proposal.amount} to account {msg.proposal.recipient_account}?
                                            <div className="chat-proposal-actions">
                                                <button
                                                    className="ledger-button"
                                                    onClick={() => handleConfirm(msg.id, msg.proposal)}
                                                >
                                                    Confirm
                                                </button>
                                                <button
                                                    className="ledger-button ledger-button--ghost"
                                                    onClick={() => handleCancel(msg.id)}
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {msg.confirmed && (
                                        <div className="chat-stamp-inline">
                                            <div className="stamp-badge">Transfer<br />Complete</div>
                                        </div>
                                    )}

                                    {msg.cancelled && (
                                        <p className="chat-text" style={{ color: 'var(--ink-faint)' }}>Cancelled.</p>
                                    )}
                                </>
                            )}
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>

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

                <p className="ledger-footer-text"><a className="ledger-link" href="/dashboard">Back to ledger</a></p>
            </div>
        </div>
    )
}
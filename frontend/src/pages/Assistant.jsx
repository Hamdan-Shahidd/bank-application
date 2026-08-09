import { useState, useRef, useEffect } from 'react'
import { sendMessage, confirmTransfer } from '../api'
import AppShell from '../components/AppShell'
import { Send, Bot } from 'lucide-react'

const PROMPTS = [
    'What is my current balance?',
    'Show me my recent transactions',
    'Send 100 to an account',
]

export default function Assistant() {
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState([])
    const [error, setError] = useState('')
    const [sending, setSending] = useState(false)
    const bottomRef = useRef(null)
    const textareaRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    async function send(question) {
        if (!question.trim() || sending) return
        setError('')
        setInput('')
        if (textareaRef.current) textareaRef.current.style.height = 'auto'

        setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: question }])
        setSending(true)

        try {
            const res = await sendMessage(question)
            const { kind, text, proposal, details } = res.data
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: 'assistant',
                kind: kind === 'proposal' || kind === 'propose_transfer' ? 'proposal' : kind,
                text, proposal, details,
            }])
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong')
        } finally {
            setSending(false)
        }
    }

    function autoResize(e) {
        const el = e.target
        el.style.height = 'auto'
        el.style.height = Math.min(el.scrollHeight, 110) + 'px'
        setInput(el.value)
    }

    function handleSubmit(e) {
        e.preventDefault()
        send(input)
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            send(input)
        }
    }

    async function handleConfirm(msgId, proposal) {
        try {
            await confirmTransfer(proposal.recipient_account, proposal.amount)
            setMessages(prev => prev.map(m => m.id === msgId ? { ...m, confirmed: true } : m))
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    function handleCancel(msgId) {
        setMessages(prev => prev.map(m => m.id === msgId ? { ...m, cancelled: true } : m))
    }

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Apex Assistant</h1>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="card chat-shell">
                <div className="chat-messages">
                    {messages.length === 0 && (
                        <div className="chat-empty">
                            <div className="chat-empty-icon"><Bot size={22} /></div>
                            <h3>How can I help with your finances?</h3>
                            <p>Ask about balances, transactions, or move money.</p>
                            <div className="chat-prompt-stack">
                                {PROMPTS.map(p => (
                                    <button key={p} className="chat-prompt-chip" onClick={() => send(p)}>{p}</button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map(msg => (
                        <div key={msg.id} className={`chat-row chat-row--${msg.role}`}>
                            <div className={`chat-avatar chat-avatar--${msg.role}`}>
                                {msg.role === 'user' ? 'Y' : <Bot size={14} />}
                            </div>
                            <div className="chat-bubble">
                                {msg.role === 'user' && (
                                    <div className="chat-bubble-text">{msg.text}</div>
                                )}

                                {msg.role === 'assistant' && msg.kind === 'text' && (
                                    <div className="chat-bubble-text">{msg.text}</div>
                                )}

                                {msg.role === 'assistant' && (msg.kind === 'account_details' || msg.kind === 'get_account_details') && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.username}<br />
                                        Acct. {msg.details.account_number}<br />
                                        Balance: PKR {(msg.details.balance / 100).toFixed(2)}
                                    </div>
                                )}

                                {msg.role === 'assistant' && msg.kind === 'proposal' && msg.proposal && !msg.confirmed && !msg.cancelled && (
                                    <div className="chat-proposal">
                                        <div className="chat-proposal-title">Review Transfer</div>
                                        Send PKR {msg.proposal.amount} to account {msg.proposal.recipient_account}?
                                        <div className="chat-proposal-actions">
                                            <button className="btn btn-primary" onClick={() => handleConfirm(msg.id, msg.proposal)}>Confirm</button>
                                            <button className="btn btn-secondary" onClick={() => handleCancel(msg.id)}>Cancel</button>
                                        </div>
                                    </div>
                                )}

                                {msg.confirmed && (
                                    <svg className="success-check" style={{ width: 30, height: 30, margin: '0.4rem 0 0' }} viewBox="0 0 52 52">
                                        <circle cx="26" cy="26" r="24" />
                                        <path d="M14 27l7 7 16-16" />
                                    </svg>
                                )}
                                {msg.cancelled && <p className="chat-cancelled">Cancelled.</p>}
                            </div>
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="chat-input-bar">
                        <textarea ref={textareaRef} value={input} onChange={autoResize} onKeyDown={handleKeyDown} rows={1} placeholder="Ask Apex AI..." />
                        <button type="submit" className="chat-send-btn" disabled={!input.trim() || sending}>
                            <Send size={15} />
                        </button>
                    </div>
                </form>
                <p className="chat-disclaimer">AI can make mistakes. Consider verifying important financial info.</p>
            </div>
        </AppShell>
    )
}
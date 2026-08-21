import { useState, useRef, useEffect } from 'react'
import { sendMessage, sendPeopleQuery, confirmTransfer, confirmDeposit, confirmWithdraw, refineEmail, sendEmail } from '../api'
import AppShell from '../components/AppShell'
import { Send, Bot, Mail, Send as SendIcon, Wand2, Globe, ExternalLink } from 'lucide-react'
import api from '../api'
const PROMPTS = [
    'What is my current balance?',
    'Show me my recent transactions',
    'Send 100 to an account',
]

export default function Assistant() {
    const [peopleDebugMode, setPeopleDebugMode] = useState(false)
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
            const res = peopleDebugMode ? await sendPeopleQuery(question) : await sendMessage(question)
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

    async function handleConfirm(msgId, proposal) {
        try {
            await confirmTransfer(proposal.recipient_account, proposal.amount)
            setMessages(prev => prev.map(m => m.id === msgId ? { ...m, confirmed: true } : m))
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    async function handleConfirmDeposit(msgId, proposal) {
        try {
            await confirmDeposit(proposal.amount)
            setMessages(prev => prev.map(m => m.id === msgId ? { ...m, confirmed: true } : m))
        } catch (err) {
            setError(err.response?.data?.detail || 'Deposit failed')
        }
    }

    async function handleConfirmWithdraw(msgId, proposal) {
        try {
            await confirmWithdraw(proposal.amount)
            setMessages(prev => prev.map(m => m.id === msgId ? { ...m, confirmed: true } : m))
        } catch (err) {
            setError(err.response?.data?.detail || 'Withdrawal failed')
        }
    }

    function handleCancel(msgId) {
        setMessages(prev => prev.map(m => m.id === msgId ? { ...m, cancelled: true } : m))
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

    function updateDraft(msgId, patch) {
        setMessages(prev => prev.map(m =>
            m.id === msgId
                ? { ...m, details: { ...m.details, ...patch } }
                : m
        ))
    }

    async function handleRefine(msgId, details, instruction) {
        if (!instruction.trim()) return
        updateDraft(msgId, { refining: true })
        try {
            const res = await refineEmail(details.subject, details.body, instruction)
            updateDraft(msgId, {
                subject: res.data.subject,
                body: res.data.body,
                refineInput: '',
                refining: false,
            })
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not refine the draft')
            updateDraft(msgId, { refining: false })
        }
    }

    async function handleSendEmail(msgId, details) {
        updateDraft(msgId, { sending: true })
        try {
            const res = await sendEmail(details.recipient, details.subject, details.body)
            if (res.data.sent) {
                setMessages(prev => prev.map(m =>
                    m.id === msgId ? { ...m, confirmed: true } : m
                ))
            } else {
                setError(res.data.error || 'Email failed to send')
                updateDraft(msgId, { sending: false })
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Email failed to send')
            updateDraft(msgId, { sending: false })
        }
    }

    async function handleConnectGoogle() {
    try {
        const res = await api.get('/auth/google/connect-url')
        window.location.href = res.data.url
    } catch (err) {
        console.error('Google connect error:', err)   // <-- add this line
        setError('Could not start Google connection')
    }
}

    return (
        <AppShell>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Apex Assistant</h1>

                    <button className="btn btn-secondary" onClick={handleConnectGoogle}>
                        Connect Google (Email &amp; Calendar)
                    </button>

                    {/* TEMP: RAG debug toggle — remove when done testing */}
                    <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                        <input type="checkbox" checked={peopleDebugMode} onChange={e => setPeopleDebugMode(e.target.checked)} />
                        People RAG debug mode
                    </label>
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

                                {/* User message */}
                                {msg.role === 'user' && (
                                    <div className="chat-bubble-text">{msg.text}</div>
                                )}

                                {/* Plain text response */}
                                {msg.role === 'assistant' && msg.kind === 'text' && (
                                    <div className="chat-bubble-text">{msg.text}</div>
                                )}

                                {/* Account details */}
                                {msg.role === 'assistant' && (msg.kind === 'account_details' || msg.kind === 'get_account_details') && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.username}<br />
                                        Acct. {msg.details.account_number}<br />
                                        Balance: PKR {(msg.details.balance / 100).toFixed(2)}
                                    </div>
                                )}


                                {msg.role === 'assistant' && msg.kind === 'calendar_event_deleted' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.deleted ? <p>Event deleted from your calendar.</p> : <p>{msg.details.error}</p>}
                                    </div>
                                )}

                                {msg.role === 'assistant' && msg.kind === 'calendar_event_updated' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.updated ? <p>Event updated.</p> : <p>{msg.details.error}</p>}
                                    </div>
                                )}

                                {/* Crypto prices */}
                                {msg.role === 'assistant' && msg.kind === 'crypto_prices' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.stale && (
                                            <p style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
                                                (showing last known prices)
                                            </p>
                                        )}
                                        {msg.details.prices?.map(p => (
                                            <div key={p.symbol}>
                                                {p.symbol}: ${p.price_usd.toLocaleString()}
                                                {' '}({p.change_pct_today >= 0 ? '+' : ''}{p.change_pct_today}%)
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Weather */}
                                {msg.role === 'assistant' && msg.kind === 'weather_info' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.stale && (
                                            <p style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
                                                (showing last known conditions)
                                            </p>
                                        )}
                                        {msg.details.cities?.map(c => (
                                            <div key={c.city}>
                                                {c.city}: {c.temperature_c}°C, {c.condition} ({c.windspeed_kmh} km/h wind)
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Transfer proposal */}
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

                                {/* Deposit proposal */}
                                {msg.role === 'assistant' && msg.kind === 'proposal_deposit' && msg.proposal && !msg.confirmed && !msg.cancelled && (
                                    <div className="chat-proposal">
                                        <div className="chat-proposal-title">Review Deposit</div>
                                        Deposit PKR {msg.proposal.amount}?
                                        <div className="chat-proposal-actions">
                                            <button className="btn btn-primary" onClick={() => handleConfirmDeposit(msg.id, msg.proposal)}>Confirm</button>
                                            <button className="btn btn-secondary" onClick={() => handleCancel(msg.id)}>Cancel</button>
                                        </div>
                                    </div>
                                )}

                                {/* Withdrawal proposal */}
                                {msg.role === 'assistant' && msg.kind === 'proposal_withdrawal' && msg.proposal && !msg.confirmed && !msg.cancelled && (
                                    <div className="chat-proposal">
                                        <div className="chat-proposal-title">Review Withdrawal</div>
                                        Withdraw PKR {msg.proposal.amount}?
                                        <div className="chat-proposal-actions">
                                            <button className="btn btn-primary" onClick={() => handleConfirmWithdraw(msg.id, msg.proposal)}>Confirm</button>
                                            <button className="btn btn-secondary" onClick={() => handleCancel(msg.id)}>Cancel</button>
                                        </div>
                                    </div>
                                )}

                                
                                {msg.role === 'assistant' && msg.kind === 'generated_image' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.error ? (
                                            <p>{msg.details.error}</p>
                                        ) : (
                                            <>
                                                <img
                                                    src={`data:image/png;base64,${msg.details.image_b64}`}
                                                    alt={msg.details.prompt}
                                                    style={{ width: '100%', maxWidth: 380, borderRadius: 'var(--radius-md)' }}
                                                />
                                                <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', marginTop: '0.4rem' }}>
                                                    {msg.details.prompt}{msg.details.cached && ' (cached)'}
                                                </p>
                                            </>
                                        )}
                                    </div>
                                )}


                                {msg.role === 'assistant' && msg.kind === 'calendar_event_added' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.added
                                            ? <p>Added to your calendar.</p>
                                            : <p>{msg.details.error}</p>}
                                    </div>
                                )}


                                {msg.role === 'assistant' && msg.kind === 'web_search' && msg.details && (
                                    <div className="chat-details">
                                        {msg.details.error ? (
                                            <p>{msg.details.error}</p>
                                        ) : (
                                            <>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem',
                                                            fontSize: '0.8rem', color: 'var(--text-tertiary)',
                                                            marginBottom: '0.5rem' }}>
                                                    <Globe size={13} />
                                                    Web results for "{msg.details.query}"
                                                    {msg.details.cached && ' (cached)'}
                                                </div>

                                                {msg.details.answer && (
                                                    <p style={{ marginBottom: '0.75rem' }}>{msg.details.answer}</p>
                                                )}

                                                {msg.details.results?.length > 0 && (
                                                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.5rem' }}>
                                                        <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)',
                                                                    marginBottom: '0.35rem' }}>
                                                            Sources
                                                        </p>
                                                        {msg.details.results.map((r, i) => (
                                                            <div key={r.url} style={{ marginBottom: '0.4rem' }}>
                                                                <a href={r.url} target="_blank" rel="noopener noreferrer"
                                                                className="link"
                                                                style={{ fontSize: '0.85rem', display: 'inline-flex',
                                                                            alignItems: 'center', gap: '0.25rem' }}>
                                                                    {i + 1}. {r.title} <ExternalLink size={11} />
                                                                </a>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Email draft */}
                                {msg.role === 'assistant' && msg.kind === 'email_draft' && msg.details && !msg.confirmed && !msg.cancelled && (
                                    <div className="chat-proposal">
                                        <div className="chat-proposal-title">
                                            <Mail size={14} /> Review Email
                                        </div>

                                        <div className="field">
                                            <label>To</label>
                                            <input
                                                value={msg.details.recipient || ''}
                                                onChange={e => updateDraft(msg.id, { recipient: e.target.value })}
                                            />
                                        </div>

                                        <div className="field">
                                            <label>Subject</label>
                                            <input
                                                value={msg.details.subject || ''}
                                                onChange={e => updateDraft(msg.id, { subject: e.target.value })}
                                            />
                                        </div>

                                        <div className="field">
                                            <label>Body</label>
                                            <textarea
                                                rows={20}
                                                value={msg.details.body || ''}
                                                onChange={e => updateDraft(msg.id, { body: e.target.value })}
                                            />
                                        </div>

                                        {/* Refinement loop */}
                                        <div className="field">
                                            <label>Ask for a change</label>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <input
                                                    placeholder="e.g. make it shorter, more formal"
                                                    value={msg.details.refineInput || ''}
                                                    onChange={e => updateDraft(msg.id, { refineInput: e.target.value })}
                                                    onKeyDown={e => {
                                                        if (e.key === 'Enter') {
                                                            e.preventDefault()
                                                            handleRefine(msg.id, msg.details, msg.details.refineInput || '')
                                                        }
                                                    }}
                                                />
                                                <button
                                                    className="btn btn-secondary"
                                                    disabled={msg.details.refining}
                                                    onClick={() => handleRefine(msg.id, msg.details, msg.details.refineInput || '')}
                                                >
                                                    <Wand2 size={14} /> {msg.details.refining ? '...' : 'Refine'}
                                                </button>

                                            </div>
                                            <div className="field-quick-amounts">
                                                {['Make it shorter', 'More formal', 'More friendly', 'Add more detail'].map(q => (
                                                    <button key={q} type="button" className="chip-btn"
                                                        onClick={() => handleRefine(msg.id, msg.details, q)}>
                                                        {q}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="chat-proposal-actions">
                                            <button
                                                className="btn btn-primary"
                                                disabled={msg.details.sending}
                                                onClick={() => handleSendEmail(msg.id, msg.details)}
                                            >
                                                <SendIcon size={14} /> {msg.details.sending ? 'Sending...' : 'Send Email'}
                                            </button>
                                            <button className="btn btn-secondary" onClick={() => handleCancel(msg.id)}>
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Confirmed / cancelled states */}
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
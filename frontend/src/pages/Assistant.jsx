import { useState } from 'react'
import { sendMessage, confirmTransfer } from '../api'

export default function Assistant() {
    const [input, setInput] = useState('')
    const [reply, setReply] = useState('')
    const [proposal, setProposal] = useState(null)
    const [details, setDetails] = useState(null)
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

            if (kind === 'proposal') setProposal(p)
            else if (kind === 'account_details') setDetails(d)
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
            setReply('Transfer complete')
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    return (
        <div>
            <h1>Assistant</h1>

            <form onSubmit={handleSend}>
                <input
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="e.g. send 500 to 1234567890"
                    required
                />
                <button type="submit">Send</button>
            </form>

            {error && <p style={{color: 'red'}}>{error}</p>}
            {reply && <p>{reply}</p>}

            {details && (
                <div>
                    <p><strong>Name:</strong> {details.username}</p>
                    <p><strong>Account:</strong> {details.account_number}</p>
                    <p><strong>Balance:</strong> {details.balance}</p>
                </div>
            )}

            {proposal && (
                <div>
                    <p>Send {proposal.amount} to account {proposal.recipient_account}?</p>
                    <button onClick={handleConfirm}>Confirm</button>
                    <button onClick={() => setProposal(null)}>Cancel</button>
                </div>
            )}
        </div>
    )
}
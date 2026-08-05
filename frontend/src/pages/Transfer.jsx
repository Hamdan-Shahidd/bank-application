import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { transfer } from '../api'

export default function Transfer() {
    const [account, setAccount] = useState('')
    const [amount, setAmount] = useState('')
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

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
            setMessage('Transfer complete')
            setTimeout(() => navigate('/dashboard'), 1500)
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed')
        }
    }

    return (
        <div>
            <h1>Transfer</h1>
            {message && <p style={{color: 'green'}}>{message}</p>}
            {error && <p style={{color: 'red'}}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <input
                    placeholder="Recipient account number"
                    value={account}
                    onChange={e => setAccount(e.target.value)}
                    required
                />
                <input
                    type="number"
                    placeholder="Amount"
                    value={amount}
                    onChange={e => setAmount(e.target.value)}
                    min="1"
                    required
                />
                <button type="submit">Send</button>
            </form>
        </div>
    )
}
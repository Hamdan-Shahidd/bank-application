import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { withdraw } from '../api'

export default function Withdraw() {
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
            await withdraw(parsed)
            setMessage(`${parsed} withdrawn successfully`)
            setTimeout(() => navigate('/dashboard'), 1500)
        } catch (err) {
            setError(err.response?.data?.detail || 'Withdrawal failed')
        }
    }

    return (
        <div>
            <h1>Withdraw</h1>
            {message && <p style={{color: 'green'}}>{message}</p>}
            {error && <p style={{color: 'red'}}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <input
                    type="number"
                    placeholder="Amount"
                    value={amount}
                    onChange={e => setAmount(e.target.value)}
                    min="1"
                    required
                />
                <button type="submit">Withdraw</button>
            </form>
        </div>
    )
}
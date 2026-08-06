import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { signup } from '../api'

export default function Signup() {
    const [form, setForm] = useState({ username: '', gmail: '', password: '' })
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const navigate = useNavigate()

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        try {
            const res = await signup(form.username, form.gmail, form.password)
            setSuccess(`Account created. Your account number is ${res.data.account_number}`)
            setTimeout(() => navigate('/login'), 2500)
        } catch (err) {
            setError(err.response?.data?.detail || 'Signup failed')
        }
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <p className="ledger-wordmark">Ledger</p>
                <h1 className="ledger-title">Sign up</h1>

                {error && <div className="ledger-error">{error}</div>}
                {success && <div className="ledger-success">{success}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="ledger-field">
                        <label htmlFor="username">Username</label>
                        <input id="username" name="username" value={form.username} onChange={handleChange} required />
                    </div>
                    <div className="ledger-field">
                        <label htmlFor="gmail">Email</label>
                        <input id="gmail" name="gmail" type="email" value={form.gmail} onChange={handleChange} required />
                    </div>
                    <div className="ledger-field">
                        <label htmlFor="password">Password</label>
                        <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required />
                    </div>
                    <button type="submit" className="ledger-button ledger-button--full">
                        Create account
                    </button>
                </form>

                <p className="ledger-footer-text">
                    Have an account? <Link className="ledger-link" to="/login">Log in</Link>
                </p>
            </div>
        </div>
    )
}
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
    const [gmail, setGmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        try {
            const res = await login(gmail, password)
            localStorage.setItem('token', res.data.access_token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed')
        }
    }

    return (
        <div className="ledger-page">
            <div className="ledger-card">
                <p className="ledger-wordmark">Ledger</p>
                <h1 className="ledger-title">Log in</h1>

                {error && <div className="ledger-error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="ledger-field">
                        <label htmlFor="gmail">Email</label>
                        <input
                            id="gmail"
                            type="email"
                            value={gmail}
                            onChange={e => setGmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="ledger-field">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="ledger-button ledger-button--full">
                        Open the ledger
                    </button>
                </form>

                <p className="ledger-footer-text">
                    No account? <Link className="ledger-link" to="/signup">Start one</Link>
                </p>
            </div>
        </div>
    )
}
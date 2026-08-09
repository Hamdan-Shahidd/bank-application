import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api'
import { Mail, Lock, Eye, EyeOff, ShieldCheck, Landmark } from 'lucide-react'

export default function Login() {
    const [gmail, setGmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
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
        <div className="auth-page">
            <div className="auth-form-panel">
                <div className="auth-form-card">
                    <div className="auth-brand">
                        <Landmark size={18} /> Apex Finance
                    </div>
                    <h1 className="auth-title">Welcome back.</h1>
                    <p className="auth-subtitle">Sign in to securely access your account.</p>

                    {error && <div className="alert alert-error">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="field">
                            <label htmlFor="gmail">Email or Username</label>
                            <div className="field-input-wrap">
                                <Mail size={16} className="field-icon" />
                                <input
                                    id="gmail" type="email" className="has-icon-left"
                                    placeholder="john.doe@example.com"
                                    value={gmail} onChange={e => setGmail(e.target.value)} required
                                />
                            </div>
                        </div>

                        <div className="field">
                            <label htmlFor="password">Password</label>
                            <div className="field-input-wrap">
                                <Lock size={16} className="field-icon" />
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    className="has-icon-left has-icon-right"
                                    value={password} onChange={e => setPassword(e.target.value)} required
                                />
                                <button type="button" className="field-toggle-btn" onClick={() => setShowPassword(!showPassword)}>
                                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>
                        </div>

                        <button type="submit" className="btn btn-primary btn-full">Sign In →</button>
                    </form>

                    <p className="footer-text">
                        Don't have an account? <Link className="link" to="/signup">Create an account</Link>
                    </p>
                    <p className="encryption-note">256-bit Bank Grade Encryption</p>
                </div>
            </div>

            <div className="auth-visual">
                <div className="auth-decor"></div>
                <div className="auth-badge">
                    <div className="auth-badge-icon"><ShieldCheck size={16} /></div>
                    <div>
                        <h4>Bank Grade Security</h4>
                        <p>Your financial data is protected with strong encryption.</p>
                    </div>
                </div>
            </div>
        </div>
    )
}
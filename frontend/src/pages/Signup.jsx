import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { signup } from '../api'
import { User, Mail, Lock, ShieldCheck, Landmark } from 'lucide-react'

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
        <div className="auth-page">
            <div className="auth-form-panel">
                <div className="auth-form-card">
                    <div className="auth-brand">
                        <Landmark size={18} /> Apex Finance
                    </div>
                    <h1 className="auth-title">Create your account.</h1>
                    <p className="auth-subtitle">Enter your details to get started.</p>

                    {error && <div className="alert alert-error">{error}</div>}
                    {success && <div className="alert alert-success">{success}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="field">
                            <label htmlFor="username">Username</label>
                            <div className="field-input-wrap">
                                <User size={16} className="field-icon" />
                                <input id="username" name="username" className="has-icon-left" value={form.username} onChange={handleChange} required />
                            </div>
                        </div>
                        <div className="field">
                            <label htmlFor="gmail">Email Address</label>
                            <div className="field-input-wrap">
                                <Mail size={16} className="field-icon" />
                                <input id="gmail" name="gmail" type="email" className="has-icon-left" value={form.gmail} onChange={handleChange} required />
                            </div>
                        </div>
                        <div className="field">
                            <label htmlFor="password">Password</label>
                            <div className="field-input-wrap">
                                <Lock size={16} className="field-icon" />
                                <input id="password" name="password" type="password" className="has-icon-left" value={form.password} onChange={handleChange} required />
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary btn-full">Continue →</button>
                    </form>

                    <p className="footer-text">
                        Already have an account? <Link className="link" to="/login">Sign In</Link>
                    </p>
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
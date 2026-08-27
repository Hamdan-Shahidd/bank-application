import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { requestSignupCode, verifySignupCode } from '../api'

export default function Signup() {
    const [step, setStep] = useState(1)
    const [form, setForm] = useState({ username: '', gmail: '', password: '', code: '' })
    const [error, setError] = useState('')
    const [info, setInfo] = useState('')
    const navigate = useNavigate()

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    async function handleRequestCode(e) {
        e.preventDefault()
        setError(''); setInfo('')
        try {
            const res = await api.post('/signup/request-code', { gmail: form.gmail })
            if (res.data.success) {
                setInfo('Check your email for a 6-digit code.')
                setStep(2)
            } else {
                setError(res.data.error)
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not send code')
        }
    }

    async function handleVerifyAndCreate(e) {
        e.preventDefault()
        setError('')
        try {
            const res = await api.post('/signup/verify-code', form)
            localStorage.setItem('token', res.data.access_token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Verification failed')
        }
    }


    async function handleRequestCode(e) {
        e.preventDefault()
        setError(''); setInfo('')
        try {
            const res = await requestSignupCode(form.gmail)
            if (res.data.success) {
                setInfo('Check your email for a 6-digit code.')
                setStep(2)
            } else {
                setError(res.data.error)
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not send code')
        }
    }

    async function handleVerifyAndCreate(e) {
        e.preventDefault()
        setError('')
        try {
            const res = await verifySignupCode(form.username, form.gmail, form.password, form.code)
            localStorage.setItem('token', res.data.access_token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Verification failed')
        }
    }
    
    return (
        <div className="auth-page">
            <div className="auth-form-panel">
                <div className="auth-form-card">
                    <h1 className="auth-title">Create your account.</h1>

                    <button type="button" className="btn btn-secondary btn-full"
                        onClick={() => { window.location.href = '/auth/google/login' }}>
                        Continue with Google
                    </button>


                    {error && <div className="alert alert-error">{error}</div>}
                    {info && <div className="alert alert-success">{info}</div>}

                    {step === 1 && (
                        <form onSubmit={handleRequestCode}>
                            <div className="field">
                                <label>Username</label>
                                <input name="username" value={form.username} onChange={handleChange} required />
                            </div>
                            <div className="field">
                                <label>Email Address</label>
                                <input name="gmail" type="email" value={form.gmail} onChange={handleChange} required />
                            </div>
                            <div className="field">
                                <label>Password</label>
                                <input name="password" type="password" value={form.password} onChange={handleChange} required />
                            </div>
                            <button type="submit" className="btn btn-primary btn-full">Send Verification Code</button>
                        </form>
                    )}

                    {step === 2 && (
                        <form onSubmit={handleVerifyAndCreate}>
                            <p>We sent a code to {form.gmail}.</p>
                            <div className="field">
                                <label>Verification Code</label>
                                <input name="code" value={form.code} onChange={handleChange}
                                       maxLength={6} required autoFocus />
                            </div>
                            <button type="submit" className="btn btn-primary btn-full">Verify & Create Account</button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    )
}
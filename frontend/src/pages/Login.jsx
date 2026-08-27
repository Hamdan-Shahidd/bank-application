import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { login, requestSignupCode, verifySignupCode } from '../api'
import { Mail, Lock, User, KeyRound, Eye, EyeOff, ShieldCheck, Landmark } from 'lucide-react'

const OAUTH_ERRORS = {
    invalid_state: 'That sign-in link expired. Please try again.',
    oauth_failed: 'Google sign-in failed. Please try again.',
}

export default function Login() {
    const [mode, setMode] = useState('signin')   // 'signin' | 'signup'
    const [step, setStep] = useState(1)          // signup only: 1 = details, 2 = code
    const [form, setForm] = useState({ username: '', gmail: '', password: '', code: '' })
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState('')
    const [info, setInfo] = useState('')
    const [busy, setBusy] = useState(false)
    const navigate = useNavigate()
    const [params] = useSearchParams()

    // Surface ?error= from the OAuth callback (api/routes/oauth.py).
    useEffect(() => {
        const e = params.get('error')
        if (e) setError(OAUTH_ERRORS[e] || 'Sign-in failed. Please try again.')
    }, [params])

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    function switchMode(next) {
        setMode(next)
        setStep(1)
        setError('')
        setInfo('')
    }

    async function handleSignIn(e) {
        e.preventDefault()
        setError(''); setBusy(true)
        try {
            const res = await login(form.gmail, form.password)
            localStorage.setItem('token', res.data.access_token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed')
        } finally {
            setBusy(false)
        }
    }

    async function handleRequestCode(e) {
        e.preventDefault()
        setError(''); setInfo(''); setBusy(true)
        try {
            const res = await requestSignupCode(form.gmail)
            if (res.data.success) {
                setInfo(`We sent a 6-digit code to ${form.gmail}.`)
                setStep(2)
            } else {
                setError(res.data.error)
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Could not send code')
        } finally {
            setBusy(false)
        }
    }

    async function handleVerifyAndCreate(e) {
        e.preventDefault()
        setError(''); setBusy(true)
        try {
            const res = await verifySignupCode(form.username, form.gmail, form.password, form.code)
            localStorage.setItem('token', res.data.access_token)
            navigate('/dashboard')
        } catch (err) {
            setError(err.response?.data?.detail || 'Verification failed')
        } finally {
            setBusy(false)
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-form-panel">
                <div className="auth-form-card">
                    <div className="auth-brand">
                        <Landmark size={18} /> Apex Finance
                    </div>

                    <h1 className="auth-title">
                        {mode === 'signin' ? 'Welcome back.' : 'Create your account.'}
                    </h1>
                    <p className="auth-subtitle">
                        {mode === 'signin'
                            ? 'Sign in to securely access your account.'
                            : 'Set up secure access in under a minute.'}
                    </p>

                    <div className="auth-tabs">
                        <button type="button"
                            className={`auth-tab${mode === 'signin' ? ' active' : ''}`}
                            onClick={() => switchMode('signin')}>
                            Sign in
                        </button>
                        <button type="button"
                            className={`auth-tab${mode === 'signup' ? ' active' : ''}`}
                            onClick={() => switchMode('signup')}>
                            Create account
                        </button>
                    </div>

                    <button type="button" className="btn btn-secondary btn-full"
                        onClick={() => { window.location.href = '/auth/google/login' }}>
                        Continue with Google
                    </button>

                    <div className="auth-divider"><span>or</span></div>

                    {error && <div className="alert alert-error">{error}</div>}
                    {info && <div className="alert alert-success">{info}</div>}

                    {/* ---------- SIGN IN ---------- */}
                    {mode === 'signin' && (
                        <form onSubmit={handleSignIn}>
                            <div className="field">
                                <label htmlFor="gmail">Email Address</label>
                                <div className="field-input-wrap">
                                    <Mail size={16} className="field-icon" />
                                    <input
                                        id="gmail" name="gmail" type="email" className="has-icon-left"
                                        placeholder="john.doe@example.com"
                                        value={form.gmail} onChange={handleChange} required
                                    />
                                </div>
                            </div>

                            <div className="field">
                                <label htmlFor="password">Password</label>
                                <div className="field-input-wrap">
                                    <Lock size={16} className="field-icon" />
                                    <input
                                        id="password" name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        className="has-icon-left has-icon-right"
                                        value={form.password} onChange={handleChange} required
                                    />
                                    <button type="button" className="field-toggle-btn"
                                            onClick={() => setShowPassword(!showPassword)}>
                                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-full" disabled={busy}>
                                {busy ? 'Signing in…' : 'Sign In →'}
                            </button>
                        </form>
                    )}

                    {/* ---------- SIGN UP, STEP 1 ---------- */}
                    {mode === 'signup' && step === 1 && (
                        <form onSubmit={handleRequestCode}>
                            <div className="field">
                                <label htmlFor="username">Username</label>
                                <div className="field-input-wrap">
                                    <User size={16} className="field-icon" />
                                    <input id="username" name="username" className="has-icon-left"
                                           value={form.username} onChange={handleChange} required />
                                </div>
                            </div>

                            <div className="field">
                                <label htmlFor="signup-gmail">Email Address</label>
                                <div className="field-input-wrap">
                                    <Mail size={16} className="field-icon" />
                                    <input id="signup-gmail" name="gmail" type="email" className="has-icon-left"
                                           placeholder="john.doe@example.com"
                                           value={form.gmail} onChange={handleChange} required />
                                </div>
                            </div>

                            <div className="field">
                                <label htmlFor="signup-password">Password</label>
                                <div className="field-input-wrap">
                                    <Lock size={16} className="field-icon" />
                                    <input
                                        id="signup-password" name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        className="has-icon-left has-icon-right"
                                        value={form.password} onChange={handleChange} required
                                    />
                                    <button type="button" className="field-toggle-btn"
                                            onClick={() => setShowPassword(!showPassword)}>
                                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-full" disabled={busy}>
                                {busy ? 'Sending…' : 'Send Verification Code'}
                            </button>
                        </form>
                    )}

                    {/* ---------- SIGN UP, STEP 2 ---------- */}
                    {mode === 'signup' && step === 2 && (
                        <form onSubmit={handleVerifyAndCreate}>
                            <div className="field">
                                <label htmlFor="code">Verification Code</label>
                                <div className="field-input-wrap">
                                    <KeyRound size={16} className="field-icon" />
                                    <input id="code" name="code" className="has-icon-left"
                                           value={form.code} onChange={handleChange}
                                           maxLength={6} inputMode="numeric" required autoFocus />
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-full" disabled={busy}>
                                {busy ? 'Verifying…' : 'Verify & Create Account'}
                            </button>

                            <p className="footer-text">
                                Wrong address?{' '}
                                <button type="button" className="link-button"
                                        onClick={() => { setStep(1); setInfo(''); setError('') }}>
                                    Use a different email
                                </button>
                            </p>
                        </form>
                    )}

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
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
            setTimeout(() => navigate('/login'), 3000)
        } catch (err) {
            setError(err.response?.data?.detail || 'Signup failed')
        }
    }

    return (
        <div>
            <h1>Sign up</h1>
            {error && <p style={{color: 'red'}}>{error}</p>}
            {success && <p style={{color: 'green'}}>{success}</p>}
            <form onSubmit={handleSubmit}>
                <input name="username" placeholder="Username" onChange={handleChange} required />
                <input name="gmail" type="email" placeholder="Email" onChange={handleChange} required />
                <input name="password" type="password" placeholder="Password" onChange={handleChange} required />
                <button type="submit">Create account</button>
            </form>
            <p>Have an account? <Link to="/login">Log in</Link></p>
        </div>
    )
}
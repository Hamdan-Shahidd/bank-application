import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getMe } from '../api'

export default function Dashboard() {
    const [user, setUser] = useState(null)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        getMe()
            .then(res => setUser(res.data))
            .catch(() => setError('Failed to load account'))
    }, [])

    function logout() {
        localStorage.removeItem('token')
        navigate('/login')
    }

    if (!user) return <p>Loading...</p>

    return (
        <div>
            <h1>Hello, {user.username}</h1>
            <p>Account: {user.account_number}</p>
            <p>Balance: {user.balance}</p>
            {error && <p style={{color: 'red'}}>{error}</p>}
            <nav>
                <Link to="/deposit">Deposit</Link>
                <Link to="/transfer">Transfer</Link>
                <Link to="/assistant">Assistant</Link>
            </nav>
            <button onClick={logout}>Log out</button>
        </div>
    )
}
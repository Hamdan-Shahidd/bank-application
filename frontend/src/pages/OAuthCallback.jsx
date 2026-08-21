import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

export default function OAuthCallback() {
    const [params] = useSearchParams()
    const navigate = useNavigate()

    useEffect(() => {
        const token = params.get('token')
        const error = params.get('error')
        if (token) {
            localStorage.setItem('token', token)
            navigate('/dashboard')
        } else {
            navigate(`/login?error=${error || 'oauth_failed'}`)
        }
    }, [])

    return <p style={{ padding: '2rem' }}>Signing you in...</p>
}
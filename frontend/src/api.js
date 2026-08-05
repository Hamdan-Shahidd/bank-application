import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
})

// Attach token to every request automatically
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// If any request gets 401, clear token and redirect to login
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export const signup = (username, gmail, password) =>
    api.post('/signup', { username, gmail, password })

export const login = (gmail, password) =>
    api.post('/login', { gmail, password })

export const getMe = () =>
    api.get('/me')

export const deposit = (amount) =>
    api.post('/deposit', { amount })

export const transfer = (recipient_account, amount) =>
    api.post('/transfer', { recipient_account, amount })

export const sendMessage = (message) =>
    api.post('/assistant', { message })

export const confirmTransfer = (recipient_account, amount) =>
    api.post('/assistant/confirm', { recipient_account, amount })
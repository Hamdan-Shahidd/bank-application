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

export const withdraw = (amount) =>
    api.post('/withdraw', { amount })

export const getHistory = () => 
    api.get('/history')

export const confirmDeposit = (amount) =>
    api.post('/assistant/confirm_deposit', { amount })

export const confirmWithdraw = (amount) =>
    api.post('/assistant/confirm_withdraw', { amount })

// Added for the people's information RAG system.
export const sendPeopleQuery = (message) =>
    api.post('/debug/people-query', { message })

// Added for the crypto coin prices (Five)
export const getCryptoPrices = () =>
    api.get('/market/crypto')

// Added for the weather api
export const getWeather = () =>
    api.get('/weather/cities')

// Added for the email generation one's
export const refineEmail = (subject, body, instruction) =>
    api.post('/email/refine', { subject, body, instruction })

export const sendEmail = (recipient, subject, body) =>
    api.post('/email/send', { recipient, subject, body })

export const requestSignupCode = (gmail) =>
    api.post('/signup/request-code', { gmail })

export const verifySignupCode = (username, gmail, password, code) =>
    api.post('/signup/verify-code', { username, gmail, password, code })

export default api
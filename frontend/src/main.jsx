import './styles/shared.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Deposit from './pages/Deposit'
import Transfer from './pages/Transfer'
import Assistant from './pages/Assistant'
import Withdraw from './pages/Withdraw'
import Crypto from './pages/Crypto'
import Weather from './pages/Weather'
import OAuthCallback from './pages/OAuthCallback'



function PrivateRoute({ children }) {
    const token = localStorage.getItem('token')
    return token ? children : <Navigate to="/login" />
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <BrowserRouter>
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={
                <PrivateRoute><Dashboard /></PrivateRoute>
            } />
            <Route path="/deposit" element={
                <PrivateRoute><Deposit /></PrivateRoute>
            } />
            <Route path="/transfer" element={
                <PrivateRoute><Transfer /></PrivateRoute>
            } />
            <Route path="/withdraw" element={
                <PrivateRoute><Withdraw /></PrivateRoute>
            } />
            <Route path="/assistant" element={
                <PrivateRoute><Assistant /></PrivateRoute>
            } />

            <Route path="/crypto" element={
                <PrivateRoute><Crypto /></PrivateRoute>
            } />

            <Route path="/weather" element={
                <PrivateRoute><Weather /></PrivateRoute>
            } />

            <Route path="/oauth-callback" element={<OAuthCallback />} />
            
            <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
    </BrowserRouter>
)
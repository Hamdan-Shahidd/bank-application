import { useState, useEffect } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
    LayoutDashboard,
    ArrowDownToLine,
    ArrowUpFromLine,
    ArrowLeftRight,
    Bot,
    LogOut,
    Landmark,
} from 'lucide-react'
import { getMe } from '../api'

export default function AppShell({ children }) {
    const navigate = useNavigate()
    const [user, setUser] = useState(null)

    useEffect(() => {
        getMe().then(res => setUser(res.data)).catch(() => {})
    }, [])

    function logout() {
        localStorage.removeItem('token')
        navigate('/login')
    }

    const initials = user?.username ? user.username.slice(0, 2).toUpperCase() : '..'

    return (
        <div className="app-shell">
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <div className="sidebar-brand-mark"><Landmark size={16} /></div>
                    Apex
                </div>

                <nav className="sidebar-nav">
                    <NavLink to="/dashboard" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                        <LayoutDashboard size={18} /> Home
                    </NavLink>
                    <NavLink to="/deposit" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                        <ArrowDownToLine size={18} /> Deposit
                    </NavLink>
                    <NavLink to="/withdraw" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                        <ArrowUpFromLine size={18} /> Withdrawal
                    </NavLink>
                    <NavLink to="/transfer" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                        <ArrowLeftRight size={18} /> Transfer
                    </NavLink>
                    <NavLink to="/assistant" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                        <Bot size={18} /> AI Assistant
                    </NavLink>
                </nav>

                <div className="sidebar-footer">
                    {user && (
                        <div className="sidebar-user">
                            <div className="sidebar-user-avatar">{initials}</div>
                            <div>
                                <div className="sidebar-user-name">{user.username}</div>
                                <div className="sidebar-user-sub">{user.account_number}</div>
                            </div>
                        </div>
                    )}
                    <button className="sidebar-logout" onClick={logout}>
                        <LogOut size={18} /> Sign Out
                    </button>
                </div>
            </aside>

            <main className="page-content">{children}</main>
        </div>
    )
}
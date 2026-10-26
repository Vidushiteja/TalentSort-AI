import {Routes,Route,Navigate} from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Upload from './pages/Upload'
import Candidates from './pages/Candidates'
import History from './pages/History'
import Settings from './pages/Settings'
export default function App(){return <Routes><Route element={<Layout/>}><Route path="/" element={<Dashboard/>}/><Route path="/jobs" element={<Jobs/>}/><Route path="/upload" element={<Upload/>}/><Route path="/candidates" element={<Candidates/>}/><Route path="/history" element={<History/>}/><Route path="/settings" element={<Settings/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Route></Routes>}

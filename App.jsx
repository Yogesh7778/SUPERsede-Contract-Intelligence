import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components'
import { Analysis, Compare, Dashboard, Evidence, PackDetail, Packs, Settings, Upload } from './pages'

export default function App() { return <Layout><Routes><Route path="/" element={<Dashboard/>}/><Route path="/packs" element={<Packs/>}/><Route path="/packs/:id" element={<PackDetail/>}/><Route path="/upload" element={<Upload/>}/><Route path="/compare" element={<Compare/>}/><Route path="/analysis" element={<Analysis/>}/><Route path="/evidence" element={<Evidence/>}/><Route path="/settings" element={<Settings/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></Layout> }

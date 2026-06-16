import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Dashboard } from './features/dashboard/Dashboard'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-surface-900">
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App

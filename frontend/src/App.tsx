import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import Layout from './components/Layout.tsx'
import ChatPage from './pages/ChatPage.tsx'
import CopilotPage from './pages/CopilotPage.tsx'
import NotFoundPage from './pages/NotFoundPage.tsx'
import SearchPage from './pages/SearchPage.tsx'
import { ListSkeleton } from './components/States'

const DashboardPage = lazy(() => import('./pages/DashboardPage.tsx'))

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/search" replace />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="copilot" element={<CopilotPage />} />
        <Route
          path="dashboard"
          element={
            <Suspense fallback={<ListSkeleton />}>
              <DashboardPage />
            </Suspense>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

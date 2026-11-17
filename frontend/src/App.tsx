import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router'
import Layout from './components/Layout.tsx'
import PublicLayout from './components/PublicLayout.tsx'
import RequireAuth from './components/RequireAuth.tsx'
import { ListSkeleton } from './components/States'
import AuthPage from './pages/AuthPage.tsx'
import ChatPage from './pages/ChatPage.tsx'
import CopilotPage from './pages/CopilotPage.tsx'
import LandingPage from './pages/LandingPage.tsx'
import NotFoundPage from './pages/NotFoundPage.tsx'
import SearchPage from './pages/SearchPage.tsx'

const DashboardPage = lazy(() => import('./pages/DashboardPage.tsx'))

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="login" element={<AuthPage key="login" mode="login" />} />
        <Route path="signup" element={<AuthPage key="signup" mode="signup" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
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
      </Route>
    </Routes>
  )
}

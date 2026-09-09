import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/shared/ProtectedRoute';
import Navbar from './components/shared/Navbar';

// Eagerly loaded (tiny + always needed on first paint)
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Lazy-loaded pages → code-split into separate chunks
const LandingPage   = lazy(() => import('./pages/LandingPage'));
const AnalysisPage  = lazy(() => import('./pages/AnalysisPage'));
const SettingsPage  = lazy(() => import('./pages/SettingsPage'));
const ProjectsPage  = lazy(() => import('./pages/ProjectsPage'));

/** Minimal skeleton shown during lazy-chunk loading */
function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}


function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes — no navbar */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes — with navbar */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <div className="min-h-screen">
                  <Navbar />
                  <Suspense fallback={<PageLoader />}>
                    <Routes>
                      <Route path="/" element={<LandingPage />} />
                      <Route path="/projects" element={<ProjectsPage />} />
                      <Route path="/projects/:id" element={<AnalysisPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                    </Routes>
                  </Suspense>
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1e293b',
              color: '#f1f5f9',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '12px',
              fontSize: '14px',
            },
            success: { iconTheme: { primary: '#22c55e', secondary: '#0f172a' } },
            error: { iconTheme: { primary: '#ef4444', secondary: '#0f172a' } },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

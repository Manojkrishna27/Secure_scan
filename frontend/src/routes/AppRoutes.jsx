import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import { Loader2 } from "lucide-react";

import { DashboardLayout } from "@/layouts/DashboardLayout";
import { MainLayout } from "@/layouts/MainLayout";
import ProtectedRoute from "@/routes/ProtectedRoute";
import { CardSkeleton } from "@/components/ui/skeleton";

const LandingPage = lazy(() => import("@/pages/Landing/LandingPage"));
const LoginPage = lazy(() => import("@/pages/Auth/LoginPage"));
const RegisterPage = lazy(() => import("@/pages/Auth/RegisterPage"));
const DashboardPage = lazy(() => import("@/pages/Dashboard/DashboardPage"));
const MonitoringPage = lazy(() => import("@/pages/Dashboard/MonitoringPage"));
const ScanHistoryPage = lazy(() => import("@/pages/Dashboard/ScanHistoryPage"));
const ScanDetailsPage = lazy(() => import("@/pages/Dashboard/ScanDetailsPage"));
const ReportsPage = lazy(() => import("@/pages/Dashboard/ReportsPage"));
const SettingsPage = lazy(() => import("@/pages/Dashboard/SettingsPage"));
const AdminLayout = lazy(() => import("@/pages/Admin/AdminLayout"));
const AdminDashboard = lazy(() => import("@/pages/Admin/AdminDashboard"));
const AdminAnalytics = lazy(() => import("@/pages/Admin/AdminAnalytics"));
const AdminUsers = lazy(() => import("@/pages/Admin/AdminUsers"));
const AdminAuditLogs = lazy(() => import("@/pages/Admin/AdminAuditLogs"));
const NotFoundPage = lazy(() => import("@/pages/NotFound"));

function PageLoader() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-primary" aria-label="Loading" />
    </div>
  );
}

function LazyPage({ children }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route
          index
          element={
            <LazyPage>
              <LandingPage />
            </LazyPage>
          }
        />
      </Route>

      <Route
        path="login"
        element={
          <LazyPage>
            <LoginPage />
          </LazyPage>
        }
      />
      <Route
        path="register"
        element={
          <LazyPage>
            <RegisterPage />
          </LazyPage>
        }
      />

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route
          path="dashboard"
          element={
            <LazyPage>
              <DashboardPage />
            </LazyPage>
          }
        />
        <Route
          path="monitoring"
          element={
            <LazyPage>
              <MonitoringPage />
            </LazyPage>
          }
        />
        <Route
          path="scans"
          element={
            <LazyPage>
              <ScanHistoryPage />
            </LazyPage>
          }
        />
        <Route
          path="scan/:id"
          element={
            <LazyPage>
              <ScanDetailsPage />
            </LazyPage>
          }
        />
        <Route
          path="reports"
          element={
            <LazyPage>
              <ReportsPage />
            </LazyPage>
          }
        />
        <Route
          path="settings"
          element={
            <LazyPage>
              <SettingsPage />
            </LazyPage>
          }
        />
        <Route
          path="admin"
          element={
            <ProtectedRoute adminOnly>
              <LazyPage>
                <AdminLayout />
              </LazyPage>
            </ProtectedRoute>
          }
        >
          <Route
            index
            element={
              <Suspense fallback={<CardSkeleton lines={4} />}>
                <AdminDashboard />
              </Suspense>
            }
          />
          <Route
            path="analytics"
            element={
              <Suspense fallback={<CardSkeleton lines={4} />}>
                <AdminAnalytics />
              </Suspense>
            }
          />
          <Route
            path="users"
            element={
              <Suspense fallback={<CardSkeleton lines={4} />}>
                <AdminUsers />
              </Suspense>
            }
          />
          <Route
            path="logs"
            element={
              <Suspense fallback={<CardSkeleton lines={4} />}>
                <AdminAuditLogs />
              </Suspense>
            }
          />
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <LazyPage>
            <NotFoundPage />
          </LazyPage>
        }
      />
    </Routes>
  );
}

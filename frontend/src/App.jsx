import AppRoutes from "./routes/AppRoutes.jsx";
import { ToastProvider } from "./context/ToastContext.jsx";

export default function App() {
  return (
    <ToastProvider>
      <AppRoutes />
    </ToastProvider>
  );
}

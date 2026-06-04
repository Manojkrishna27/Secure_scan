import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  clearAuthStorage,
  fetchCurrentUser,
  getStoredToken,
  getStoredUser,
  loginUser,
  logoutUser,
  registerUser,
  setAuthStorage,
} from "@/services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [token, setToken] = useState(() => getStoredToken());
  const [loading, setLoading] = useState(true);

  const isAuthenticated = Boolean(token && user);

  const bootstrap = useCallback(async () => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setLoading(false);
      return;
    }
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      setToken(storedToken);
    } catch {
      clearAuthStorage();
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = async (email, password) => {
    const data = await loginUser({ email, password });
    setAuthStorage(data.access_token, data.user);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (fullName, email, password) => {
    return registerUser({
      full_name: fullName,
      email,
      password,
    });
  };

  const logout = async () => {
    try {
      if (token) {
        await logoutUser();
      }
    } catch {
      /* clear local state even if API fails */
    } finally {
      clearAuthStorage();
      setToken(null);
      setUser(null);
    }
  };

  const refreshUser = async () => {
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
    const storedToken = getStoredToken();
    if (storedToken) {
      setAuthStorage(storedToken, currentUser);
    }
    return currentUser;
  };

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, token, loading, isAuthenticated]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

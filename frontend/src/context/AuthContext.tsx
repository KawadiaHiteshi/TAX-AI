import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../services/api";

interface User {
  id: number;
  email: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("taxai_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authAPI.me()
        .then((res) => setUser(res.data))
        .catch(() => logout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authAPI.login(email, password);
    const { access_token, user: u } = res.data;
    localStorage.setItem("taxai_token", access_token);
    setToken(access_token);
    setUser(u);
  };

  const register = async (email: string, fullName: string, password: string) => {
    const res = await authAPI.register({ email, full_name: fullName, password });
    const { access_token, user: u } = res.data;
    localStorage.setItem("taxai_token", access_token);
    setToken(access_token);
    setUser(u);
  };

  const logout = () => {
    localStorage.removeItem("taxai_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

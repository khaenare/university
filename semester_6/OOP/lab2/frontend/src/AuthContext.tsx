import { ReactNode, createContext, useContext, useMemo, useState } from 'react';
import { clearSession, loadSession, login as apiLogin, type Session } from './api';

interface AuthContextValue {
  session: Session | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => loadSession());
  const value = useMemo<AuthContextValue>(() => ({
    session,
    async login(username, password) {
      setSession(await apiLogin(username, password));
    },
    logout() {
      clearSession();
      setSession(null);
    }
  }), [session]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}

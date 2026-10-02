import React from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { login as loginApi, me as meApi } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("eadrp_token");
    if (!token) {
      setReady(true);
      return;
    }
    meApi()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("eadrp_token");
        setUser(null);
      })
      .finally(() => setReady(true));
  }, []);

  async function login(email, password) {
    const data = await loginApi(email, password);
    localStorage.setItem("eadrp_token", data.access_token);
    const currentUser = await meApi();
    setUser(currentUser);
    return currentUser;
  }

  function logout() {
    localStorage.removeItem("eadrp_token");
    setUser(null);
  }

  const value = useMemo(() => ({ user, ready, login, logout }), [user, ready]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

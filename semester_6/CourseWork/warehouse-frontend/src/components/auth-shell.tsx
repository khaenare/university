"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FormEvent, ReactNode, useEffect, useState } from "react";

import { AuthUser, getCurrentUser, login, logout, UserRole } from "@/lib/api";

const ACCESS_TOKEN_KEY = "warehouse.accessToken";
const REFRESH_TOKEN_KEY = "warehouse.refreshToken";

type NavigationItem = {
  href: string;
  label: string;
  roles: UserRole[];
};

type NavigationGroup = {
  title: string;
  items: NavigationItem[];
};

const NAVIGATION_GROUPS: NavigationGroup[] = [
  {
    title: "Overview",
    items: [
      { href: "/", label: "Dashboard", roles: ["ADMIN", "MANAGER"] },
      { href: "/stock", label: "Stock Balance", roles: ["ADMIN", "MANAGER"] },
    ],
  },
  {
    title: "Operations",
    items: [
      { href: "/receipts", label: "Receipts", roles: ["ADMIN", "MANAGER"] },
      { href: "/writeoffs", label: "Write-Offs", roles: ["ADMIN", "MANAGER"] },
      { href: "/production-orders", label: "Production Orders", roles: ["ADMIN", "MANAGER"] },
    ],
  },
  {
    title: "Production",
    items: [{ href: "/production-recipes", label: "Production Recipes", roles: ["ADMIN"] }],
  },
  {
    title: "Directories",
    items: [
      { href: "/products", label: "Products", roles: ["ADMIN"] },
      { href: "/suppliers", label: "Suppliers", roles: ["ADMIN"] },
    ],
  },
  {
    title: "Reports",
    items: [
      { href: "/reports", label: "Reports Overview", roles: ["ADMIN", "MANAGER"] },
      { href: "/reports/stock-valuation", label: "Stock Valuation", roles: ["ADMIN", "MANAGER"] },
      { href: "/reports/production-cost", label: "Production Cost", roles: ["ADMIN", "MANAGER"] },
      { href: "/reports/movements", label: "Inventory Movements", roles: ["ADMIN", "MANAGER"] },
    ],
  },
];

const NAVIGATION_ITEMS = NAVIGATION_GROUPS.flatMap((group) => group.items);

export function AuthShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [openGroups, setOpenGroups] = useState<string[]>(["Overview", "Operations", "Reports"]);
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    function onUnauthorized() {
      setUser(null);
      setIsCheckingSession(false);
      setError("Session expired. Please sign in again.");
    }

    window.addEventListener("warehouse:unauthorized", onUnauthorized);

    const timer = setTimeout(() => {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);

      if (!token) {
        setIsCheckingSession(false);
        return;
      }

      void getCurrentUser(token)
        .then((currentUser) => {
          setUser(currentUser);
        })
        .catch(() => {
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
        })
        .finally(() => {
          setIsCheckingSession(false);
        });
    }, 0);

    return () => {
      window.removeEventListener("warehouse:unauthorized", onUnauthorized);
      clearTimeout(timer);
    };
  }, []);

  async function onLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");

    try {
      setIsSubmitting(true);
      setError(null);

      const session = await login({ email, password });
      localStorage.setItem(ACCESS_TOKEN_KEY, session.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, session.refreshToken);
      setUser(session.user);
      setError(null);
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "Failed to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onLogout() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);

    if (refreshToken) {
      await logout(refreshToken).catch(() => undefined);
    }
  }

  if (isCheckingSession) {
    return <main className="auth-page">Checking session...</main>;
  }

  if (!user) {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div>
            <div className="eyebrow">Warehouse access</div>
            <h1 className="hero-title">Sign in to continue</h1>
            <p className="hero-description">Use the seeded demo users for admin or manager workflows.</p>
          </div>

          <form onSubmit={onLogin} className="form-grid">
            <input name="email" type="email" placeholder="admin@localhost" required defaultValue="admin@localhost" />
            <input name="password" type="password" placeholder="Password" required defaultValue="admin12345" />
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="demo-users">
            <span>Admin: admin@localhost / admin12345</span>
            <span>Manager: manager@localhost / manager12345</span>
          </div>

          {error ? <p className="error-message">{error}</p> : null}
        </section>
      </main>
    );
  }

  const currentNavigationItem = NAVIGATION_ITEMS.find((item) => item.href === pathname);
  const isForbidden = currentNavigationItem ? !currentNavigationItem.roles.includes(user.role) : false;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-kicker">Monitor</div>
        <h1 className="sidebar-title">Warehouse</h1>
        <nav className="sidebar-nav">
          {NAVIGATION_GROUPS.map((group) => {
            const visibleItems = group.items.filter((item) => item.roles.includes(user.role));
            if (visibleItems.length === 0) {
              return null;
            }

            const isOpen = openGroups.includes(group.title);

            return (
              <div className="nav-group" key={group.title}>
                <button
                  className="nav-group-trigger"
                  type="button"
                  onClick={() => setOpenGroups((current) => current.includes(group.title)
                    ? current.filter((title) => title !== group.title)
                    : [...current, group.title])}
                >
                  <span>{group.title}</span>
                  <span>{isOpen ? "−" : "+"}</span>
                </button>
                {isOpen ? (
                  <div className="nav-group-items">
                    {visibleItems.map((item) => (
                      <Link className={`sidebar-link ${pathname === item.href ? "active" : ""}`} href={item.href} key={item.href}>
                        {item.label}
                      </Link>
                    ))}
                  </div>
                ) : null}
              </div>
            );
          })}
        </nav>
      </aside>
      <div className="app-main">
        <header className="topbar">
          <div className="signed-in">
            Signed in as
            <strong>{user.email}</strong>
            <span className="role-badge">{user.role}</span>
          </div>
          <button className="logout-button" type="button" onClick={onLogout}>
            Log out
          </button>
        </header>
        {isForbidden ? (
          <main className="page-container">
            <section className="hero-card">
              <div>
                <div className="eyebrow">Access denied</div>
                <h1 className="hero-title">Not authorized</h1>
                <p className="hero-description">Your role does not have permission to open this section.</p>
              </div>
            </section>
          </main>
        ) : children}
      </div>
    </div>
  );
}

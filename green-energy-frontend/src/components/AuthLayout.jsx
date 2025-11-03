// src/components/AuthLayout.jsx
export default function AuthLayout({ title, children }) {
  return (
    <div className="auth-root">
      <div className="auth-card">
        <header className="auth-header">
          <h1 className="auth-header-title">{title}</h1>
        </header>

        <main className="auth-body">{children}</main>
      </div>
    </div>
  );
}

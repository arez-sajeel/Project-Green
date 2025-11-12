export default function Sidebar() {
    return (
      <aside className="w-64 bg-gray-800 text-white min-h-screen p-6">
        <h1 className="text-2xl font-bold mb-6">Green Optimiser</h1>
        <nav className="flex flex-col space-y-4">
          <a href="/" className="hover:text-green-400">Dashboard</a>
          <a href="/properties" className="hover:text-green-400">Properties</a>
          <a href="/reports" className="hover:text-green-400">Reports</a>
          <a href="/settings" className="hover:text-green-400">Settings</a>
        </nav>
      </aside>
    );
  }
  
export default function Header() {
    return (
      <header className="flex justify-between items-center bg-white shadow px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-700">Property Manager Dashboard</h2>
        <button className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600">
          Logout
        </button>
      </header>
    );
  }
  
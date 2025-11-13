export default function StatsCard({ title, value }) {
    return (
      <div className="bg-white rounded-2xl shadow p-6 text-center hover:shadow-lg transition">
        <h3 className="text-gray-600 text-lg">{title}</h3>
        <p className="text-3xl font-bold text-green-500 mt-2">{value}</p>
      </div>
    );
  }
  
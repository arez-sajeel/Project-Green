import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import StatsCard from "../components/StatsCard";

export default function Dashboard() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard title="Total Properties" value="12" />
          <StatsCard title="Total Energy Usage" value="4,320 kWh" />
          <StatsCard title="Top Saver" value="Property #7" />
        </main>
      </div>
    </div>
  );
}

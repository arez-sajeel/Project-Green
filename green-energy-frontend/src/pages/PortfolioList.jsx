// src/pages/PortofolioList.jsx
import { useEffect, useState} from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";

export default function PortfolioList() {
  const [properties, setProperties] = useState([]);
  const [search, sortSearch] = useState("");
  const [sortBy, setSortBy] = useState(name);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() =>{
    fetchPoperties();
  }, [page, sortBy, search]);
  async function fetchPrperties(){
    setLoading(true);
    try{
      const res = await axios.get("/api/properties", {
        params:{page, sort_by : sortBy, search},
      });
      setProperties(res.data.results);
      setTotalPages(res.data.total_pages);
    } catch(err){
      console.errror("Error Fetching Properties:", err );
    } finally{
      setLoading(false);
    }
  }

  function handleAddProperty(){
    nav("/add-property");
  }

  return(
    <div className = "p-8 font-sans max-w-5x1 mx-auto">
      <div className = "flex justify-between items-center mb-6">
        <h1 className = "text-2x1 font-semibold">Portfolio Properties</h1>
        <button
          onclock={handleAddProperty}
          className = "bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
          >
            + Add Property
          </button>
      </div>

      {/* Search + Sort */}
      <div className="flex gap-4 mb-4">
        <input
          type = "text"
          placeholder = "Search by name or address..."
          className = "border p-2 rounded w-full"
          value = {search}
          onChange={(e) => setSortBy(e.target.value)}
          />
          <select
            className = "border p-2 rounded w-full"
            value = {search}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value = "name">Name</option>
            <option value = "location">Location</option>
            <option value = "created_at">Date Added</option>
          </select>
      </div>

      {/* Table */}
      {loading ? (
        <p>Loading properties...</p>
      ) : properties.length === 0 ? (
        <p className = "text-gray-500">No properties found</p>
      ) : (
          <table className="w-full border-collapse border border-gray-200">
          <thead className="bg-gray-100">
            <tr>
              <th className="border p-2 text-left">Name</th>
              <th className="border p-2 text-left">Address</th>
              <th className="border p-2 text-left">Units</th>
              <th className="border p-2 text-left">Created</th>
            </tr>
          </thead>
          <tbody>
            {properties.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="border p-2">{p.name}</td>
                <td className="border p-2">{p.address}</td>
                <td className="border p-2">{p.units}</td>
                <td className="border p-2">{new Date(p.created_at).toLocaleDateString()}

        </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      

      {/* Pagination */}
      <div className="flex justify-center gap-2 mt-6">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="border px-3 py-1 rounded disabled:opacity-50"
        >
          Prev
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          className="border px-3 py-1 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
    


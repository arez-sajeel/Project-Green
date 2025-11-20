import { useEffect, useState} from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import AuthLayout from "../components/AuthLayout";

export default function TariffOption(){
    const [tariffs, setTariffs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedTariff, setSelectedTariff] = useState(null);

    useEffect(() => {
        async function fetchTariffs() {
            try{
                const response = await axios.get("/api/tariffs");
                
                setTariffs(response.data);
            } catch (err){
                console.error("Error fetching tariffs:", err);
                setError("Failed to load tariff options. Please try again later.");
            } finally {
                setLoading(false);
            }
        }
        fetchTariffs();
    }, []);

    function handleSelect(tariff) {
        setSelectedTariff(tariff);
        console.log("Selected Tariff:", tariff);
    }
    async function handleConfirm(){
        console.log("Confirmed tariff:", selectedTariff);

        try{
            await axios.post("/api/user/teriff", {tariffId: selectedTariff.id});
            alert('You have selected: ${selectedTariff.name}');  
        } catch (err) {
            console.error("Error Confirming tariff:", err);
            alert("Failed to save your selection");
        }
    }

    if (loading){
        return (
            <AuthLayout title="Choose Your Tariff Plan">
                <p>Loading tariffs...</p>
            </AuthLayout>
        );
    }

    if (error){
        return(
            <AuthLayout title="Choose Your Tariff Plan">
                <p className="text-red-600">{error}</p>
            </AuthLayout>
        );
    }

    return(
        <AuthLayout title="Choose Your Tariff Plan">
            <div className="space-y-4">
                {tarrofs.map((tariff) => (
                    <div
                        key={tariff.id}
                        onClick={() => handleSelect(tariff)}
                        className = {'cursor-pointer border rounded-2xl p-4 transition-all hover:shadow-lg ${tariff.is_renewable ? "border-green-500 bg-green-50" : "border-gray-200 bg-white"} ${selectedTariff?.id === tariff.id ? "ring-2 ring-blue-400" : ""}`}'}
                    >
                     <h3 className="text-lg font-semibold flex items-center justify-between">
              {tariff.name}
              {tariff.is_renewable && (
                <span className="text-green-600 text-sm font-medium">🌱 Renewable</span>
              )}
            </h3>
            <p className="text-gray-600 text-sm mt-1">{tariff.description}</p>
            <p className="text-gray-800 mt-2 font-medium">
              Rate: {tariff.rate_per_kwh?.toFixed(2)} £/kWh
            </p>     
            </div>
            ))}
            {selectedTariff && (
          <div className="mt-6 p-4 border-t border-gray-200">
            <p className="text-gray-800">
              <strong>Selected Tariff:</strong> {selectedTariff.name}
            </p>
            <button
              onClick={handleConfirm}
              className="auth-button-primary mt-4"
            >
              Confirm Selection
            </button>
          </div>
        )}

        <div className="auth-footer">
          <span>Want to register instead?</span>
          <Link to="/register">Go to Register</Link>
        </div>
      </div>
        </AuthLayout>
    );
}
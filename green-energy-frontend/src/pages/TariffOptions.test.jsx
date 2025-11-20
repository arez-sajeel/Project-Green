// **Unit Tests for TariffOption.jsx These tests validate UI behaviour, form interactions,
//backend service calls, and visual error handling.
//

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TariffOption from "./TariffOption";
import { BrowserRouter } from "react-router-dom";
import axios from "axios";

jest.mock("axios");

//--- Helper wrapper for Router context ---
const renderWithRouter = (ui) =>
  render(<BrowserRouter>{ui}</BrowserRouter>);
//--- Mock Data Fixtures ---
const mockTariffs = [
  {
    id: 1,
    name: "Standard Tariff",
    description: "Simple flat rate",
    rate_per_kwh: 0.15,
    is_renewable: false,
  },
  {
    id: 2,
    name: "Green Energy",
    description: "Eco-friendly tariff",
    rate_per_kwh: 0.18,
    is_renewable: true,
  },
];

describe("TariffOption Component", () => {

  // --- Test 1: Component loads and fetches data --- #
  test("renders tariffs after successful API fetch (Happy Path)", async () => {
    axios.get.mockResolvedValueOnce({ data: mockTariffs });

    renderWithRouter(<TariffOption />);

    // Loading phase
    expect(screen.getByText(/Loading tariffs/i)).toBeInTheDocument();

    // Wait for the UI to render fetched tariffs
    expect(await screen.findByText("Standard Tariff")).toBeInTheDocument();
    expect(await screen.findByText("Green Energy")).toBeInTheDocument();
  });

  // --- Test 2: Error in loading ---
  test("shows error message if API fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("Network failure"));

    renderWithRouter(<TariffOption />);

    expect(await screen.findByText(/Failed to load tariff options/i)).toBeInTheDocument();
  });

// --- Test 3: Selection click updates internal state ---
  test("selecting a tariff marks it as selected", async () => {
    axios.get.mockResolvedValueOnce({ data: mockTariffs });

    renderWithRouter(<TariffOption />);

    const greenCard = await screen.findByText("Green Energy");

    fireEvent.click(greenCard);

    // Confirm selection text displays
    expect(
      screen.getByText(/Selected Tariff: Green Energy/i)
    ).toBeInTheDocument();
  });

  // --- Test 4: Confirm button sends correct API request ---
  test("confirm button sends POST request with selected tariff", async () => {
    axios.get.mockResolvedValueOnce({ data: mockTariffs });
    axios.post.mockResolvedValueOnce({ status: 200 });

    renderWithRouter(<TariffOption />);

    const greenCard = await screen.findByText("Green Energy");
    fireEvent.click(greenCard);

    const confirmButton = screen.getByRole("button", { name: /Confirm Selection/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        "/api/user/teriff",
        { tariffId: 2 }
      );
    });
  });

  // --- Test 5: POST failure triggers user-friendly alert --- #
  test("failed POST request shows alert", async () => {
    axios.get.mockResolvedValueOnce({ data: mockTariffs });
    axios.post.mockRejectedValueOnce(new Error("Save failed"));

    //Mock window alert
    window.alert = jest.fn();

    renderWithRouter(<TariffOption />);

    fireEvent.click(await screen.findByText("Standard Tariff"));

    const confirmButton = screen.getByRole("button", { name: /Confirm Selection/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith("Failed to save your selection");
    });
  });

  //--- Test 6: No confirm button unless a tariff is selected --- #
  test("confirm button is only visible after selection", async () => {
    axios.get.mockResolvedValueOnce({ data: mockTariffs });

    renderWithRouter(<TariffOption />);

    expect(screen.queryByRole("button", { name: /Confirm Selection/i })).not.toBeInTheDocument();

    // Select a tariff
    fireEvent.click(await screen.findByText("Standard Tariff"));

    expect(screen.getByRole("button", { name: /Confirm Selection/i })).toBeInTheDocument();
  });
});
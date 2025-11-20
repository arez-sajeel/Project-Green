/**
 * Unit tests for PortfolioList.jsx
 *   - Mock axios
 *   - Test data rendering
 *   - Loading + empty states
 *   - Pagination UI
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PortfolioList from "./PortfolioList";
import axios from "axios";
import { BrowserRouter } from "react-router-dom";

jest.mock("axios");

const renderWithRouter = (ui) =>
  render(<BrowserRouter>{ui}</BrowserRouter>);

// --- Mock Data Fixtures ---
const mockProperties = {
  results: [
    {
      id: 1,
      name: "The Old Post Office",
      address: "10 Baker Street",
      units: 12,
      created_at: "2024-01-10T12:00:00Z",
    },
    {
      id: 2,
      name: "Greenwood House",
      address: "15 Green Lane",
      units: 8,
      created_at: "2024-01-05T12:00:00Z",
    },
  ],
  total_pages: 3,
};

describe("PortfolioList Component", () => {
  // --- Test 1: Renders properties on API load ---
  test("renders property data when API succeeds", async () => {
    axios.get.mockResolvedValueOnce({ data: mockProperties });

    renderWithRouter(<PortfolioList />);

    // Should show loading state first
    expect(screen.getByText(/Loading properties/i)).toBeInTheDocument();

    // Should render returned data
    expect(await screen.findByText("The Old Post Office")).toBeInTheDocument();
    expect(screen.getByText("Greenwood House")).toBeInTheDocument();
  });

  // --- Test 2: No properties returned ---
  test("displays message if no properties exist", async () => {
    axios.get.mockResolvedValueOnce({ data: { results: [], total_pages: 1 } });

    renderWithRouter(<PortfolioList />);

    expect(await screen.findByText(/No properties found/i)).toBeInTheDocument();
  });

  // --- Test 3: API failure handling ---
  test("displays no crash if API fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("Backend down"));

    renderWithRouter(<PortfolioList />);

    // UI shouldn't crash – shows loading first then emptiness
    await waitFor(() => {
      expect(screen.getByText(/No properties found/i)).toBeInTheDocument();
    });
  });

  // --- Test 4: Pagination works ---
  test("clicking Next loads next page", async () => {
    // First page
    axios.get.mockResolvedValueOnce({ data: mockProperties });

    // Page 2 result
    axios.get.mockResolvedValueOnce({
      data: {
        results: [
          {
            id: 3,
            name: "New Town Court",
            address: "22 Market Road",
            units: 6,
            created_at: "2024-01-15T12:00:00Z",
          },
        ],
        total_pages: 3,
      },
    });

    renderWithRouter(<PortfolioList />);

    // Wait for page 1 to render
    expect(await screen.findByText("The Old Post Office")).toBeInTheDocument();

    // Click Next
    const next = screen.getByText("Next");
    fireEvent.click(next);

    // Page 2 should now display new data
    expect(await screen.findByText("New Town Court")).toBeInTheDocument();
  });
});
/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PropertyManagerDashboard from "../pages/PropertyManagerDashboard";
import * as propertyService from "../services/propertyService";

jest.mock("../services/propertyService");

describe("PropertyManagerDashboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("loads existing properties on mount", async () => {
    propertyService.fetchUserContext.mockResolvedValue({
      properties: [
        { property_id: "1234", shortcode: "P1", name: "Flat 1", energy_usage: "12 kWh" },
      ],
    });

    render(<PropertyManagerDashboard />);

    expect(await screen.findByText("Flat 1")).toBeInTheDocument();
  });

  test("validates empty Property ID", async () => {
    propertyService.fetchUserContext.mockResolvedValue({ properties: [] });

    render(<PropertyManagerDashboard />);

    const propertyIdField = screen.getByLabelText("Property ID", { selector: "input" });

    fireEvent.blur(propertyIdField);

    expect(await screen.findByText("Property ID is required")).toBeInTheDocument();
  });

  test("validates short Property ID", async () => {
    propertyService.fetchUserContext.mockResolvedValue({ properties: [] });

    render(<PropertyManagerDashboard />);

    const propertyIdField = screen.getByLabelText("Property ID", { selector: "input" });

    fireEvent.change(propertyIdField, { target: { value: "12" } });
    fireEvent.blur(propertyIdField);

    expect(await screen.findByText(/Too short/)).toBeInTheDocument();
  });

  test("validates provider code must be alphanumeric", async () => {
    propertyService.fetchUserContext.mockResolvedValue({ properties: [] });

    render(<PropertyManagerDashboard />);

    const providerField = screen.getByLabelText("Provider Code", { selector: "input" });

    fireEvent.change(providerField, { target: { value: "!!??" } });
    fireEvent.blur(providerField);

    expect(await screen.findByText("Provider code must be alphanumeric")).toBeInTheDocument();
  });

  test("submits form and adds property to list", async () => {
    propertyService.fetchUserContext.mockResolvedValue({ properties: [] });

    propertyService.addProperty.mockResolvedValue({
      property_id: "9999",
      name: "New Prop",
      shortcode: "NP",
      energy_usage: "0 kWh",
    });

    render(<PropertyManagerDashboard />);

    fireEvent.change(screen.getByLabelText("Property ID"), {
      target: { value: "9999" },
    });

    fireEvent.change(screen.getByLabelText("Provider Code"), {
      target: { value: "AB12" },
    });

    fireEvent.click(screen.getByText("Submit"));

    expect(propertyService.addProperty).toHaveBeenCalledWith("9999", "AB12");

    expect(await screen.findByText("New Prop")).toBeInTheDocument();
  });
});

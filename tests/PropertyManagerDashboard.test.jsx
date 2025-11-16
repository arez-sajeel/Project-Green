jest.mock("../src/services/authService", () => ({
    getToken: jest.fn(() => "fake-token")
  }));
  
  jest.mock("../src/services/propertyService", () => ({
    getProperties: jest.fn().mockResolvedValue([]),
    addProperty: jest.fn().mockResolvedValue({ success: true })
  }));
  
import { render, screen, fireEvent } from "@testing-library/react";
import PropertyManagerDashboard from "../src/pages/PropertyManagerDashboard";

  
test("renders Add new property form", () => {
  render(<PropertyManagerDashboard />);
  expect(screen.getByText("Add a new property")).toBeInTheDocument();
});

test("validates empty fields", () => {
  render(<PropertyManagerDashboard />);
  
  const button = screen.getByText("Submit");
  fireEvent.click(button);

  expect(screen.getByText("Property ID is required")).toBeInTheDocument();
});

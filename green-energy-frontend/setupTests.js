// Mock Vite environment variables for Jest
global.importMeta = {
  env: {
    VITE_API_BASE_URL: "http://localhost:8000"
  }
};

// Jest does not support import.meta, so we create a shim
Object.defineProperty(global, "import.meta", {
  value: global.importMeta
});

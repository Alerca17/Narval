import { defineConfig, devices } from '@playwright/test';

// Configuración E2E de Playwright para el Semáforo Virtual de Narval (escritorio y móvil)
export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'Escritorio Chrome', use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } } },
    { name: 'Vista Móvil', use: { ...devices['Pixel 7'], viewport: { width: 375, height: 812 } } },
  ],
});

import { test, expect } from '@playwright/test';

/**
 * Especificación E2E para el Semáforo Virtual de Narval (CP-M7-02, CP-M7-03, CP-M7-04).
 * Requiere el frontend activo (`npm run dev`) en http://localhost:5173 y los navegadores de Playwright instalados.
 */
test.describe('Narval Semáforo Virtual — Flujos E2E', () => {
  test('carga la vista principal, navega por las pestañas y muestra métricas y estado del dispositivo', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toContainText(/Narval|Semáforo|Calidad del agua/i);

    // Navegación a la vista de Métricas
    await page.getByRole('button', { name: /Métricas/i }).first().click();
    await expect(page.locator('body')).toContainText(/Métricas|Variación Temporal|Gráficos/i);

    // Navegación a la vista de Alertas
    await page.getByRole('button', { name: /Alertas/i }).first().click();
    await expect(page.locator('body')).toContainText(/Alertas/i);

    // Navegación a la vista de Dispositivo
    await page.getByRole('button', { name: /Dispositivo/i }).first().click();
    await expect(page.locator('body')).toContainText(/Dispositivo|ESP32/i);
  });
});

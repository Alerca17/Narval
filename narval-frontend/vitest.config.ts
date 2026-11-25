import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'lcov'],
      reportsDirectory: './coverage',
      include: [
        'src/services/**/*.ts',
        'src/hooks/**/*.ts',
        'src/presentation/ChartsView.tsx',
        'src/presentation/AIPanel.tsx',
        'src/App.tsx',
      ],
    },
  },
});

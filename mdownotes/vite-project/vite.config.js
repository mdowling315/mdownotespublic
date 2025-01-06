import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  mode: "development",
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        // Customize the name of the entry JavaScript file
        entryFileNames: 'assets/bundle.js', // Change this to your desired name

        // Customize the name of the CSS file
        assetFileNames: (assetInfo) => {
        if (assetInfo.name.endsWith('.css')) {
          return 'assets/style.css'; // Custom name for CSS file
        }
        return 'assets/[name].[hash][extname]'; // Default for other assets
      },
      },
    },
  },
})

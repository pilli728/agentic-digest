import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import apiServer from './api-server.integration.mjs';

export default defineConfig({
  integrations: [tailwind(), apiServer()],
  output: 'static',
});

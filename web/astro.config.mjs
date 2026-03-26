import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import apiServer from './api-server.integration.mjs';

export default defineConfig({
  site: 'https://agenticedge.com',
  integrations: [tailwind(), sitemap(), apiServer()],
  output: 'static',
});

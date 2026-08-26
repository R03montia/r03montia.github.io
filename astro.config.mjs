import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://r03montia.github.io',
  integrations: [sitemap()],
});

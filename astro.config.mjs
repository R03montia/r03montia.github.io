import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://r03montia.github.io',
  integrations: [
    sitemap({
      filter: (page) =>
        !page.includes('/inside/') &&
        !page.includes('/inside-gate') &&
        !page.includes('/inside-denied'),
    }),
  ],
});

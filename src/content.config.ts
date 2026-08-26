import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    // 里版文章标记:true 时只出现在 /inside/ 路径族,不出现在表版列表
    night: z.boolean().default(false),
  }),
});

export const collections = { blog };

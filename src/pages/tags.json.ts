import { getCollection } from 'astro:content';

// 表版标签清单（供站内搜索的 #标签直达 用）：[{ tag, count }]，按文章数倒序。
export async function GET() {
  const posts = await getCollection('blog', (p) => !p.data.night && !p.data.draft);
  const counts = new Map<string, number>();
  for (const post of posts) {
    for (const tag of post.data.tags) counts.set(tag, (counts.get(tag) ?? 0) + 1);
  }
  const tags = [...counts.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag, 'zh-CN'));
  return new Response(JSON.stringify(tags), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
}

import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { sortPosts } from '../utils/posts';

export async function GET(context) {
  const posts = sortPosts(await getCollection('blog'));
  return rss({
    title: 'R03montia',
    description: 'R03montia 的个人站点。',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `/blog/${post.id}/`,
    })),
  });
}

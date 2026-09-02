import type { CollectionEntry } from 'astro:content';

export interface PostLike {
  data: { date: Date };
}

export type BlogPost = CollectionEntry<'blog'>;

export function sortPosts<T extends PostLike>(posts: T[]): T[] {
  return [...posts].sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export function readingTime(text: string): number {
  const cjkChars = (text.match(/[一-鿿]/g) ?? []).length;
  const latinWords = (text.replace(/[一-鿿]/g, ' ').match(/[A-Za-z0-9]+/g) ?? []).length;
  const minutes = Math.ceil(cjkChars / 400 + latinWords / 200);
  return Math.max(1, minutes);
}

export function sortListedPosts(posts: BlogPost[]): BlogPost[] {
  return sortPosts(posts).sort((a, b) => {
    if (a.data.pinned !== b.data.pinned) return a.data.pinned ? -1 : 1;
    return 0;
  });
}

export function getRelatedPosts(current: BlogPost, candidates: BlogPost[], limit = 3): BlogPost[] {
  return candidates
    .filter((post) => post.id !== current.id)
    .map((post) => ({
      post,
      score: post.data.tags.filter((tag) => current.data.tags.includes(tag)).length,
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => (
      b.score - a.score
      || b.post.data.date.getTime() - a.post.data.date.getTime()
      || a.post.data.title.localeCompare(b.post.data.title, 'zh-Hans-CN')
    ))
    .slice(0, limit)
    .map((item) => item.post);
}

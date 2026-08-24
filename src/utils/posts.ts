export interface PostLike {
  data: { date: Date };
}

export function sortPosts<T extends PostLike>(posts: T[]): T[] {
  return [...posts].sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export function readingTime(text: string): number {
  const cjkChars = (text.match(/[一-鿿]/g) ?? []).length;
  const latinWords = (text.replace(/[一-鿿]/g, ' ').match(/[A-Za-z0-9]+/g) ?? []).length;
  const minutes = Math.ceil(cjkChars / 400 + latinWords / 200);
  return Math.max(1, minutes);
}

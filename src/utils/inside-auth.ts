export const INSIDE_AUTH_STORAGE_KEY = 'inside:authorized:v1';

/** 客户端只保存校验用哈希；测试密码不在前端源码里明文出现。 */
export const INSIDE_AUTH_TOKEN =
  '2d5f0919e9eb8a7f2b8567cf7ac360e9d6e1f4b8ef15f90d467276cf268f3596';

export const isInsideDeviceAuthorized = (): boolean => {
  try {
    return localStorage.getItem(INSIDE_AUTH_STORAGE_KEY) === INSIDE_AUTH_TOKEN;
  } catch {
    return false;
  }
};

export const getSafeInsideNext = (raw: string | null): string => {
  try {
    const url = new URL(raw || '/inside/', window.location.origin);
    if (url.origin !== window.location.origin) return '/inside/';
    if (url.pathname === '/inside') return '/inside/';
    if (!url.pathname.startsWith('/inside/')) return '/inside/';
    return url.pathname + url.search + url.hash;
  } catch {
    return '/inside/';
  }
};

export const getInsideGateUrl = (next = '/inside/'): string =>
  `/inside-gate/?next=${encodeURIComponent(next)}`;

export const digestInsidePassword = async (password: string): Promise<string> => {
  const bytes = new TextEncoder().encode(`inside-v1:${password}`);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
};

export const verifyInsidePassword = async (password: string): Promise<boolean> => {
  const digest = await digestInsidePassword(password.trim());
  if (digest.length !== INSIDE_AUTH_TOKEN.length) return false;

  let difference = 0;
  for (let index = 0; index < digest.length; index += 1) {
    difference |= digest.charCodeAt(index) ^ INSIDE_AUTH_TOKEN.charCodeAt(index);
  }
  return difference === 0;
};

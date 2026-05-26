export async function api(method: string, path: string, data?: any, token?: string) {
  const opts: any = { method, headers: { "Content-Type": "application/json" } };
  if (token) opts.headers.Authorization = `Bearer ${token}`;
  if (data) opts.body = JSON.stringify(data);
  const r = await fetch("/api" + path, opts);
  return r.json();
}

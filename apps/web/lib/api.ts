// apps/web/lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_BASE as string;

export type CategoryOption = { id: string; label: string };
export type TimePoint = {
  categoryId: string;
  snapshotTs: string;           // 백엔드 응답 그대로
  concurrentUserCount: number;
  openLiveCount?: number | null;
};
export type StreamCard = {
  rank: number;
  categoryId: string;
  liveTitle?: string | null;
  channelName?: string | null;
  stream_url?: string | null;
  thumb_url?: string | null;
  channelImageUrl?: string | null;
  liveImageUrl?: string | null;
  concurrentUserCount?: number | null;
};

async function get<T>(path: string) {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return (await res.json()) as T;
}

export const Api = {
  categories: () => get<CategoryOption[]>(`/categories`),
  timeseries: (ids: string[], days = 7, stepMinutes = 30) => {
    const to = new Date();
    const from = new Date(to.getTime() - days * 24 * 60 * 60 * 1000);
    const qs = new URLSearchParams({
      categoryIds: ids.join(","),
      date_from: from.toISOString(),
      date_to: to.toISOString(),
      step_minutes: String(stepMinutes),
    });
    return get<TimePoint[]>(`/timeseries?${qs.toString()}`);
  },
  topStreams: (categoryId: string, limit = 2) =>
    get<StreamCard[]>(`/top-streams?categoryId=${encodeURIComponent(categoryId)}&limit=${limit}`),
};

if (!BASE) {
  console.error("NEXT_PUBLIC_API_BASE is empty");
}
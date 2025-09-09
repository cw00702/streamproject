// apps/web/components/TopStreamsCard.tsx
"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { StreamCard } from "../lib/api";
import Image from "next/image";

export function TopStreamsPanel({ loading, categoryLabel, rows }: { loading: boolean; categoryLabel?: string; rows: StreamCard[] }) {
  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle>STREAM NOW{categoryLabel ? ` — ${categoryLabel}` : ""}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && (
          <>
            <Skeleton className="h-6 w-2/3" />
            <Skeleton className="h-36 w-full" />
            <Skeleton className="h-36 w-full" />
          </>
        )}
        {!loading && rows.length === 0 && <p className="text-sm text-muted-foreground">그래프 위에 마우스를 올리면 해당 카테고리 상위 방송을 보여줍니다.</p>}
        {!loading &&
          rows.map((r) => (
            <div key={r.rank} className="border rounded-lg p-3">
              <div className="flex items-center justify-between">
                <b className="truncate">{r.liveTitle ?? "(제목 없음)"}</b>
                <span className="text-sm opacity-70">#{r.rank}</span>
              </div>
              <div className="text-sm text-muted-foreground">{r.channelName}</div>
              {r.thumb_url && (
                <div className="relative w-full h-40 mt-2">
                  <Image
                    src={(r.thumb_url)!}
                    alt={r.liveTitle ?? ""}
                    fill               // 부모 div를 기준으로 가득 채움
                    className="object-cover rounded-md"
                    sizes="(max-width: 768px) 100vw, 33vw"
                  />
                </div>
              )}
              {r.stream_url && (
                <a href={r.stream_url} target="_blank" className="text-primary text-sm underline mt-2 inline-block">
                  GO LIVE
                </a>
              )}
            </div>
          ))}
      </CardContent>
    </Card>
  );
}

// 고정 크기(16:9) 타일 그리드
export function StreamGrid({
  rows,
  title = "STREAM NOW — 선택한 카테고리",
  loading = false,
}: {
  rows: StreamCard[];
  title?: string;
  loading?: boolean;
}) {
  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="w-full rounded-lg" style={{ aspectRatio: "16/9" }} />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        )}

        {!loading && rows.length === 0 && (
          <p className="text-sm text-muted-foreground">선택한 카테고리의 라이브가 없어요.</p>
        )}

        {!loading && rows.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {rows.map((r, i) => (
              <a
                key={(r as any).id ?? r.stream_url ?? `${r.channelName}-${i}`}
                href={r.stream_url ?? "#"}
                target="_blank"
                rel="noreferrer"
                className="group block"
                title={r.liveTitle ?? ""}
              >
                {/* 16:9 고정 비율 */}
                <div className="relative w-full overflow-hidden rounded-lg bg-muted">
                  <div className="pt-[56.25%]" />
                  {r.thumb_url && (
                    <Image
                      src={r.thumb_url}
                      alt={r.liveTitle ?? ""}
                      fill
                      className="absolute inset-0 w-full h-full object-cover transition-transform duration-200 group-hover:scale-[1.03]"
                      sizes="(max-width: 768px) 50vw, (max-width: 1280px) 25vw, 20vw"
                      priority={i < 4}
                    />
                  )}

                  {/* 좌상단 LIVE */}
                  <div className="absolute left-2 top-2 text-[11px] px-1.5 py-0.5 rounded bg-red-600 text-white">
                    생방송
                  </div>

                  {/* 우상단 랭크(있으면) */}
                  {typeof r.rank === "number" && (
                    <div className="absolute right-2 top-2 text-[11px] px-1.5 py-0.5 rounded bg-black/55 text-white">
                      #{r.rank}
                    </div>
                  )}
                </div>

                {/* 제목 / 채널 */}
                <div className="mt-2 text-sm font-medium leading-tight line-clamp-1">
                  {r.liveTitle ?? "(제목 없음)"}
                </div>
                <div className="text-xs text-muted-foreground line-clamp-1">
                  {r.channelName ?? ""}
                </div>
              </a>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

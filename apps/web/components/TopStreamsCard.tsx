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
        <CardTitle>스트림 상세{categoryLabel ? ` — ${categoryLabel}` : ""}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
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
              {(r.secure_url || r.liveImageUrl) && (
                <div className="relative w-full h-40 mt-2">
                  <Image
                    src={(r.secure_url || r.liveImageUrl)!}
                    alt={r.liveTitle ?? ""}
                    fill               // 부모 div를 기준으로 가득 채움
                    className="object-cover rounded-md"
                    sizes="(max-width: 768px) 100vw, 33vw"
                  />
                </div>
              )}
              {r.stream_url && (
                <a href={r.stream_url} target="_blank" className="text-primary text-sm underline mt-2 inline-block">
                  방송 보기 →
                </a>
              )}
            </div>
          ))}
      </CardContent>
    </Card>
  );
}

"use client";

import dynamic from "next/dynamic";
import type { EChartsOption, LineSeriesOption } from "echarts"; // ← LineSeriesOption 추가
import { useMemo } from "react";
import type { TimePoint } from "../lib/api"; // ← alias 잡으면 이렇게

const EChartsReact = dynamic(() => import("echarts-for-react"), { ssr: false });

type Props = {
  data: TimePoint[];
  idToLabel: Record<string, string>;
  mode: "overlay" | "single";
  selectedIds: string[];
  onHoverCategory?: (categoryId: string | null) => void;
};

export default function TimeseriesChart({ data, idToLabel, mode, selectedIds, onHoverCategory }: Props) {
  const option: EChartsOption = useMemo(() => {
    // 1) 카테고리별로 묶기
    const byCat: Record<string, TimePoint[]> = {};
    for (const r of data) (byCat[r.categoryId] ??= []).push(r);

    // 2) 라인 시리즈로 "명시적" 타이핑
    const series: LineSeriesOption[] = (mode === "single" && selectedIds[0] ? [selectedIds[0]] : selectedIds).map((cid) => {
      const arr = (byCat[cid] || []).slice().sort((a, b) => +new Date(a.snapshotTs) - +new Date(b.snapshotTs));

      // [time, value, categoryId] 튜플 타입을 명시
      const points: [number, number, string][] = arr.map((p) => [
        new Date(p.snapshotTs).getTime(),
        p.concurrentUserCount,
        p.categoryId,
      ]);

      const s: LineSeriesOption = {
        id: cid,
        name: idToLabel[cid] || cid,
        type: "line",            // ← 'line' 리터럴 유지
        showSymbol: false,
        smooth: true,
        data: points,
        // (선택) encode로 차원 의미를 알려주면 디버깅에 도움
        encode: { x: 0, y: 1 },
      };
      return s;
    });

    const opt: EChartsOption = {
      tooltip: {
        trigger: "axis",
        order: "valueDesc",
        valueFormatter: (v) => (typeof v === "number" ? v.toLocaleString() : String(v)),
      },
      grid: { left: 40, right: 16, top: 24, bottom: 30 },
      xAxis: { type: "time" },
      yAxis: { type: "value", name: "동시 시청자", min: 0, boundaryGap: [0, "5%"] },
      legend: { top: 0 },
      series,
    };
    return opt;
  }, [data, idToLabel, mode, selectedIds]);

  const onEvents = {
    mouseover: (params: any) => {
      const cd = params?.data?.[2] as string | undefined; // 우리의 세 번째 차원(categoryId)
      onHoverCategory?.(cd ?? null);
    },
    globalout: () => onHoverCategory?.(null),
  };

  return <EChartsReact option={option} style={{ height: 520 }} onEvents={onEvents} />;
}

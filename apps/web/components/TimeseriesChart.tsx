"use client";

import dynamic from "next/dynamic";
import type { EChartsOption, LineSeriesOption } from "echarts";
import { useMemo } from "react";
import type { TimePoint } from "../lib/api";

const EChartsReact = dynamic(() => import("echarts-for-react"), { ssr: false });

type Props = {
  data: TimePoint[];
  idToLabel: Record<string, string>;
  mode: "overlay" | "single";
  selectedIds: string[];
  onHoverCategory?: (categoryId: string | null) => void;
};

// ECharts mouseover에서 우리가 쓰는 데이터 최소 형태만 타입으로 명시
type HoverParam = { data?: [number, number, string] };

export default function TimeseriesChart({ data, idToLabel, mode, selectedIds, onHoverCategory }: Props) {
  const option: EChartsOption = useMemo(() => {
    const byCat: Record<string, TimePoint[]> = {};
    for (const r of data) (byCat[r.categoryId] ??= []).push(r);

    const series: LineSeriesOption[] = (mode === "single" && selectedIds[0] ? [selectedIds[0]] : selectedIds).map((cid) => {
      const arr = (byCat[cid] || []).slice().sort((a, b) => +new Date(a.snapshotTs) - +new Date(b.snapshotTs));

      const points: [number, number, string][] = arr.map((p) => [
        new Date(p.snapshotTs).getTime(),
        p.concurrentUserCount,
        p.categoryId,
      ]);

      return {
        id: cid,
        name: idToLabel[cid] || cid,
        type: "line",
        showSymbol: false,
        smooth: true,
        data: points,
        encode: { x: 0, y: 1 },
      };
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

  // any 대신 우리가 사용하는 최소 형태로 타입 지정
  const onEvents: Record<string, (p: HoverParam) => void> = {
    mouseover: (params) => {
      const cd = params.data?.[2] ?? null;
      onHoverCategory?.(cd);
    },
    globalout: () => onHoverCategory?.(null),
  };

  return <EChartsReact option={option} style={{ height: 520 }} onEvents={onEvents} />;
}

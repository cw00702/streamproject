// apps/web/app/page.tsx
"use client";

import { useEffect, useMemo, useState } from "react";
import { Api, CategoryOption, StreamCard, TimePoint } from "../lib/api";
import TimeseriesChart from "../components/TimeseriesChart";
import { TopStreamsPanel } from "../components/TopStreamsCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";

export default function Page() {
  const [cats, setCats] = useState<CategoryOption[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [days, setDays] = useState<number>(7);
  const [mode, setMode] = useState<"overlay" | "single">("overlay");
  const [series, setSeries] = useState<TimePoint[]>([]);
  const [hoverCat, setHoverCat] = useState<string | null>(null);
  const [hoverRows, setHoverRows] = useState<StreamCard[]>([]);
  const [hoverLoading, setHoverLoading] = useState(false);

  // 1) 카테고리 로드
  useEffect(() => {
    Api.categories().then((r) => {
      setCats(r);
      // 최초 선택: 상위 3~5개 정도 자동 선택(원하면 비워둬도 OK)
      setSelected(r.slice(0, 5).map((x) => x.id));
    });
  }, []);

  const idToLabel = useMemo(() => Object.fromEntries(cats.map((c) => [c.id, c.label])), [cats]);

  // 2) 시계열 로드
  async function reloadSeries() {
    if (selected.length === 0) {
      setSeries([]);
      return;
    }
    const rows = await Api.timeseries(selected, days, 30);
    setSeries(rows);
  }
  useEffect(() => {
    reloadSeries();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected.join(","), days]);

  // 3) 호버시 Top 스트림
  useEffect(() => {
    let ignore = false;
    (async () => {
      if (!hoverCat) {
        setHoverRows([]);
        return;
      }
      setHoverLoading(true);
      try {
        const rows = await Api.topStreams(hoverCat, 2);
        if (!ignore) setHoverRows(rows);
      } finally {
        if (!ignore) setHoverLoading(false);
      }
    })();
    return () => {
      ignore = true;
    };
  }, [hoverCat]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">StreamSpot — 카테고리 시청자 추이</h1>

      <Card>
        <CardHeader>
          <CardTitle>옵션</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-6">
            <div>
              <div className="text-sm font-medium mb-2">카테고리 선택</div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-48 overflow-auto pr-2 border rounded-md p-2">
                {cats.map((c) => {
                  const checked = selected.includes(c.id);
                  return (
                    <label key={c.id} className="flex items-center gap-2">
                      <Checkbox
                        checked={checked}
                        onCheckedChange={(v) =>
                          setSelected((prev) => (v ? Array.from(new Set([...prev, c.id])) : prev.filter((x) => x !== c.id)))
                        }
                      />
                      <span className="truncate">{c.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">표시 기간</div>
              <div className="flex gap-2">
                {[1, 3, 7, 14].map((d) => (
                  <Button key={d} variant={d === days ? "default" : "secondary"} onClick={() => setDays(d)}>
                    {d === 1 ? "24시간" : `최근 ${d}일`}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">보기</div>
              <RadioGroup value={mode} onValueChange={(v: any) => setMode(v)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem id="overlay" value="overlay" />
                  <Label htmlFor="overlay">겹쳐보기</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem id="single" value="single" />
                  <Label htmlFor="single">개별(첫 항목)</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="self-end">
              <Button onClick={reloadSeries}>새로고침</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr] gap-4">
        <Card>
          <CardContent className="pt-4">
            <TimeseriesChart
              data={series}
              idToLabel={idToLabel}
              mode={mode}
              selectedIds={selected}
              onHoverCategory={(cid) => setHoverCat(cid)}
            />
          </CardContent>
        </Card>

        <TopStreamsPanel loading={hoverLoading} categoryLabel={hoverCat ? idToLabel[hoverCat] : undefined} rows={hoverRows} />
      </div>
    </div>
  );
}

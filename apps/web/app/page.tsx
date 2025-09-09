// apps/web/app/page.tsx
"use client";

import { useEffect, useMemo, useState, useRef } from "react";
import { Api, CategoryOption, StreamCard, TimePoint } from "../lib/api";
import TimeseriesChart from "../components/TimeseriesChart";
import { TopStreamsPanel, StreamGrid  } from "../components/TopStreamsCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";


export default function Page() {
  const [cats, setCats] = useState<CategoryOption[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [days, setDays] = useState<number>(7);
  const [mode, setMode] = useState<"overlay" | "single">("overlay");
  const [series, setSeries] = useState<TimePoint[]>([]);
  const [activeCat, setActiveCat] = useState<string | null>(null);
  const [panelRows, setPanelRows] = useState<StreamCard[]>([]);
  const [panelLoading, setPanelLoading] = useState(false);
  const sliderRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const startX = useRef(0);
  const scrollLeft = useRef(0);
  const activePointerId = useRef<number | null>(null);
  const DRAG_THRESHOLD = 3;
  const pressedOnContainer = useRef(false);
  const [gridRows, setGridRows] = useState<StreamCard[]>([]);
  const [gridLoading, setGridLoading] = useState(false);
  const PER_CATEGORY = 2; // 카테고리당 몇 개 보여줄지
  const endDrag = (e?: PointerEvent) => {
    const el = sliderRef.current;
    if (!el) return;
    if (activePointerId.current !== null && el.hasPointerCapture?.(activePointerId.current)) {
      try { el.releasePointerCapture(activePointerId.current); } catch {}
    }
    activePointerId.current = null;
    isDragging.current = false;
    pressedOnContainer.current = false; // ★ 추가
    el.classList.remove("cursor-grabbing");
    el.classList.add("cursor-grab");
  };

  const onPointerDown = (e: React.PointerEvent) => {
    const el = sliderRef.current;
    if (!el) return;

    const target = e.target as HTMLElement;
    if (target.closest("button,[role='button'],a")) return;

    pressedOnContainer.current = true; // ★ 추가

    isDragging.current = false;
    startX.current = e.clientX - el.offsetLeft;
    scrollLeft.current = el.scrollLeft;
    el.classList.add("cursor-grab");
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const el = sliderRef.current;
    if (!el) return;

    // 컨테이너가 pointerdown을 받지 않았으면 드래그 시작 금지
    if (!pressedOnContainer.current) return; // ★ 추가

    if (isDragging.current && (e as any).buttons === 0) {
      endDrag(e.nativeEvent as PointerEvent);
      return;
    }

    const x = e.clientX - el.offsetLeft;
    const dx = x - startX.current;

    if (!isDragging.current) {
      if (Math.abs(dx) < DRAG_THRESHOLD) return;
      isDragging.current = true;
      activePointerId.current = e.pointerId;
      try { el.setPointerCapture(e.pointerId); } catch {}
      el.classList.remove("cursor-grab");
      el.classList.add("cursor-grabbing");
    }

    el.scrollLeft = scrollLeft.current - dx * 1.5;
    e.preventDefault();
  };

  const onPointerUp = (e: React.PointerEvent) => { endDrag(e.nativeEvent as PointerEvent); };

  const onPointerCancel = (e: React.PointerEvent) => {
    endDrag(e.nativeEvent as PointerEvent);
  };

  const onPointerLeave = (e: React.PointerEvent) => {
    // 포인터를 캡처한 상태면 leave가 와도 계속 이벤트를 받지만,
    // 혹시 캡처가 안 걸린 케이스 방어
    endDrag(e.nativeEvent as PointerEvent);
  };

  const toggleSelected = (id: string) => {
    setSelected(prev => {
      let next: string[];
      if (mode === "single") {
        next = [id];
      } else {
        next = prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id];
      }

      // 클릭 즉시 포커스 카테고리 갱신
      // - 추가된 경우: 그 id로 포커스
      // - 제거된 경우: 남은 첫 항목 or null
      setActiveCat(next.includes(id) ? id : (next[0] ?? null));
      return next;
    });
  };

// 전역에서도 한 번 더 안전망: 창 밖에서 놓는 경우 등
  useEffect(() => {
    const h = () => endDrag();
    window.addEventListener("pointerup", h);
    window.addEventListener("blur", h);
    return () => {
      window.removeEventListener("pointerup", h);
      window.removeEventListener("blur", h);
    };
  }, []);


  // 1) 카테고리 로드
  useEffect(() => {
    Api.categories().then((r) => {
      setCats(r);
      // 최초 선택: 상위 1개 정도 자동 선택(원하면 비워둬도 OK)
      const first = r[0]?.id ?? null;
      setSelected(first ? [first] : []);
      setActiveCat(first); 
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

  useEffect(() => {
  let ignore = false;

  (async () => {
    if (!activeCat) {
      setPanelRows([]);
      return;
    }
    setPanelLoading(true);
    try {
      const rows = await Api.topStreams(activeCat, 2);
      if (!ignore) setPanelRows(rows);
    } finally {
      if (!ignore) setPanelLoading(false);
    }
  })();

  return () => { ignore = true; };
  }, [activeCat]);

  useEffect(() => {
  let ignore = false;
  (async () => {
    if (selected.length === 0) {
      setGridRows([]);
      return;
    }
    setGridLoading(true);
    try {
      const lists = await Promise.all(selected.map(cid => Api.topStreams(cid, PER_CATEGORY)));
      if (ignore) return;

      // 단순 합치기 (필요시 중복 제거 로직 추가 가능)
      setGridRows(lists.flat());
    } finally {
      if (!ignore) setGridLoading(false);
    }
  })();
  return () => { ignore = true; };
}, [selected.join(",")]);

  return (
    <div className="space-y-6">
      <h1 className="text-5xl subpixel-antialiased">Category Dashboard</h1>

      <Card >
        <CardHeader>
          <CardTitle>Select Category</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <div 
              ref={sliderRef}
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
              onPointerCancel={onPointerCancel}
              onPointerLeave={onPointerLeave}
              className="flex space-x-4 overflow-x-auto no-scrollbar select-none cursor-grab touch-pan-y snap-x snap-mandatory scroll-smooth"
            >
              {cats.map((c) => {
                const isSelected = selected.includes(c.id);
                return (
                  <div
                    key={c.id}
                    className="flex-none snap-start w-90 h-100 relative m-4"
                  >
                    <button
                      onPointerDown={(e) => {
                      e.stopPropagation(); // 컨테이너 드래그 진입 차단
                      e.nativeEvent?.stopImmediatePropagation?.();
                      }}
                      onClick={() => toggleSelected(c.id)}
                      aria-pressed={isSelected}
                      className={`
                        w-70 h-95 overflow-hidden rounded-xl
                        shadow-md hover:shadow-xl
                        transition-shadow transition-transform duration-200 ease-out
                        ${isSelected
                          ? "ring-2 ring-blue-400/70 drop-shadow-[0_0_14px_rgba(59,130,246,1)]"
                            : "ring-1 hover:ring-2 hover:ring-blue-300/60 hover:drop-shadow-[0_0_10px_rgba(59,130,246,0.25)]"
                        }
                        hover:scale-105 active:scale-95
                      `}
                    >
                      <img
                        src={c.post_url}
                        alt={c.label}
                        draggable={false}
                        decoding="async"
                        className="object-cover w-full h-full rounded-xl will-change-transform"
                      />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4">
        <Card>
          <CardContent className="pt-4">
            <TimeseriesChart
              data={series}
              idToLabel={idToLabel}
              mode={mode}
              selectedIds={selected}
            />
          </CardContent>
        </Card>
      </div>
          <div className="flex flex-wrap items-center gap-10">
            <div>
              <div className="[font-family:Presentation] font-black text-xl m-3">표시 기간</div>
              <div className="[font-family:Presentation] flex gap-2">
                {[1, 3, 7, 14].map((d) => (
                  <Button key={d} variant={d === days ? "default" : "secondary"} onClick={() => setDays(d)}>
                    {d === 1 ? "24시간" : `최근 ${d}일`}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <div className="[font-family:Presentation] font-black text-xl m-2">보기</div>
              <RadioGroup value={mode} onValueChange={(v:"overlay" | "single") => setMode(v)}>
                <div className="[font-family:Presentation] flex items-center space-x-2">
                  <RadioGroupItem id="overlay" value="overlay" />
                  <Label htmlFor="overlay">겹쳐보기</Label>
                </div>
                <div className="[font-family:Presentation] flex items-center space-x-2">
                  <RadioGroupItem id="single" value="single" />
                  <Label htmlFor="single">개별(첫 항목)</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="self-end [font-family:Presentation]">
              <Button onClick={reloadSeries}>새로고침</Button>
            </div>
          </div>

      <StreamGrid rows={gridRows} loading={gridLoading} title="STREAM NOW" />
    </div>
  );
}

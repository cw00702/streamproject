// apps/web/app/layout.tsx
import "@/app/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "StreamSpot", description: "Chzzk categories dashboard" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <div className="max-w-7xl mx-auto p-4">{children}</div>
      </body>
    </html>
  );
}

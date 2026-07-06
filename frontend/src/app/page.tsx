import { Chat } from "@/components/chat";

export default function Home() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-[oklch(0.95_0.03_240)] via-[oklch(0.9_0.05_250)] to-[oklch(0.84_0.07_255)] p-0 sm:p-4">
      {/* Formas suaves de fondo (decorativas, calmas, sin distraer) */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 -left-24 h-[30rem] w-[30rem] rounded-full bg-jg-brand/20 blur-[72px]" />
        <div className="absolute top-1/4 -right-28 h-[34rem] w-[34rem] rounded-full bg-[oklch(0.72_0.12_230)]/25 blur-[80px]" />
        <div className="absolute -bottom-40 left-1/4 h-[28rem] w-[28rem] rounded-full bg-[oklch(0.85_0.09_200)]/25 blur-[80px]" />
      </div>

      <div className="relative z-10 w-full sm:w-auto">
        <Chat />
      </div>
    </main>
  );
}

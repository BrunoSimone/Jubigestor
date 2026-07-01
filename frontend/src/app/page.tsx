import { Chat } from "@/components/chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-2xl">
        <h1 className="mb-2 text-center text-3xl font-bold text-gray-900">
          Jubigestor
        </h1>
        <p className="mb-6 text-center text-gray-600">
          Tu asistente para trámites jubilatorios argentinos
        </p>
        <Chat />
        <p className="mt-4 text-center text-sm text-gray-500">
          Información orientativa. No reemplaza el asesoramiento oficial de
          ANSES.
        </p>
      </div>
    </main>
  );
}

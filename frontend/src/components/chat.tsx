"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Markdown } from "@/components/markdown";

interface Source {
  title: string;
  url: string;
  published_at: string | null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000";

function formatDate(iso: string | null): string {
  if (!iso) return "sin fecha";
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("es-AR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "¡Hola! Soy Jubigestor. Puedo ayudarte con trámites de jubilación, pensiones, PAMI y más. ¿En qué te puedo ayudar?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const viewportRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje. El elemento que scrollea es el Viewport
  // interno del ScrollArea (no su Root), por eso usamos viewportRef. El rAF
  // espera a que el layout (incluidas las fuentes) termine antes de medir.
  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const id = requestAnimationFrame(() => {
      viewport.scrollTop = viewport.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [messages, isLoading]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!res.ok || !res.body) throw new Error(`Error: ${res.status}`);

      // Stream NDJSON: 1 línea de fuentes + N líneas de texto + cierre.
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let pendingSources: Source[] = [];
      let started = false;

      const appendChunk = (chunk: string) =>
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, content: m.content + chunk } : m
          )
        );

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() ?? ""; // la última línea puede venir incompleta

        for (const line of lines) {
          if (!line.trim()) continue;
          const evt = JSON.parse(line);

          if (evt.type === "sources") {
            pendingSources = evt.sources ?? [];
          } else if (evt.type === "text") {
            if (!started) {
              started = true;
              setMessages((prev) => [
                ...prev,
                {
                  role: "assistant",
                  content: evt.chunk,
                  sources: pendingSources,
                },
              ]);
            } else {
              appendChunk(evt.chunk);
            }
          } else if (evt.type === "error") {
            if (!started) {
              started = true;
              setMessages((prev) => [
                ...prev,
                { role: "assistant", content: evt.message },
              ]);
            } else {
              appendChunk(`\n\n${evt.message}`);
            }
          }
        }
      }

      if (!started) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "No pude generar una respuesta. Probá de nuevo.",
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Disculpá, hubo un error al procesar tu consulta. Intentá de nuevo.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card className="flex h-[500px] flex-col p-4">
      <ScrollArea className="mb-4 min-h-0 flex-1 pr-4" viewportRef={viewportRef}>
        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex flex-col ${
                msg.role === "user" ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === "user"
                    ? "whitespace-pre-wrap bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
                role="log"
                aria-live={msg.role === "assistant" ? "polite" : undefined}
              >
                {msg.role === "assistant" ? (
                  <Markdown content={msg.content} />
                ) : (
                  msg.content
                )}
              </div>

              {msg.role === "assistant" &&
                msg.sources &&
                msg.sources.length > 0 && (
                  <div className="mt-2 max-w-[80%] space-y-2 rounded-lg border border-gray-200 bg-white p-3 text-sm">
                    <p className="font-medium text-gray-700">
                      Fuentes oficiales
                    </p>
                    {msg.sources.map((s, j) => (
                      <div key={j} className="text-gray-600">
                        <span aria-hidden="true">📄 </span>
                        {s.title}
                        <div className="text-xs text-gray-500">
                          Última actualización: {formatDate(s.published_at)}
                          {" · "}
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-700 underline"
                          >
                            Ver en la página oficial
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
            </div>
          ))}
          {isLoading && messages[messages.length - 1]?.role === "user" && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-gray-100 px-4 py-2 text-gray-500">
                Pensando...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribí tu consulta sobre jubilaciones..."
          disabled={isLoading}
          aria-label="Tu consulta"
        />
        <Button type="submit" disabled={isLoading || !input.trim()}>
          Enviar
        </Button>
      </form>
    </Card>
  );
}

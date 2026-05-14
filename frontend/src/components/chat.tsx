"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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

      if (!res.ok) throw new Error(`Error: ${res.status}`);

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
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
      <ScrollArea className="mb-4 flex-1 pr-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
                role="log"
                aria-live={msg.role === "assistant" ? "polite" : undefined}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
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

"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
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
  variant?: "error" | "warn";
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000";

const GREETING: Message = {
  role: "assistant",
  content:
    "¡Hola! Soy JubiGestor. Estoy para ayudarte con tu jubilación, pensión o PAMI. Contame, ¿qué necesitás saber?",
};

// Tappable starter questions (shown only on a fresh conversation): they cut the
// biggest friction for this audience — typing.
const SUGGESTED = [
  "¿Qué requisitos necesito para jubilarme?",
  "¿Cómo inicio el trámite de jubilación?",
  "¿Qué documentos necesito para la solicitud?",
];

// Text sizes cycled by the button. `scale` scales the html root font-size;
// `label` says what the NEXT click will do (clear for low digital literacy).
const FONT_STEPS = [
  { scale: 1, label: "Agrandar el texto" },
  { scale: 1.15, label: "Más grande todavía" },
  { scale: 1.3, label: "Volver al tamaño normal" },
];

// Minimal shape of the Web Speech API we use (types are not in the DOM lib).
type SpeechResultEvent = { results: ArrayLike<ArrayLike<{ transcript: string }>> };
type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((e: SpeechResultEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
};

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

function MicIcon() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="9" y="2" width="6" height="12" rx="3" />
      <path d="M5 10v1a7 7 0 0 0 14 0v-1" />
      <line x1="12" y1="19" x2="12" y2="22" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="mt-0.5 shrink-0"
    >
      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </svg>
  );
}

function NewChatIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
      <path d="M3 3v5h5" />
    </svg>
  );
}

// JubiGestor avatar ("Don Gestor"): a friendly retiree with reading glasses,
// grey hair and a smile. Designed in Claude Design; legible from 128px to ~24px.
// The SVG already includes its own brand circle, so it doesn't need .jg-avatar.
function JubiAvatar({ className = "h-10 w-10" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      role="img"
      aria-label="Avatar de JubiGestor"
      className={`shrink-0 ${className}`}
    >
      <circle cx="50" cy="50" r="50" fill="oklch(0.45 0.11 255)" />
      <circle
        cx="50"
        cy="50"
        r="50"
        fill="none"
        stroke="oklch(1 0 0 / 0.18)"
        strokeWidth="2"
      />
      <path
        d="M18 50 A32 32 0 0 1 82 50 L82 52 A32 20 0 0 0 18 52 Z"
        fill="oklch(0.82 0.008 250)"
      />
      <circle cx="50" cy="53" r="31" fill="oklch(0.9 0.04 65)" />
      <circle cx="33" cy="60" r="6.5" fill="oklch(0.78 0.07 30)" opacity="0.55" />
      <circle cx="67" cy="60" r="6.5" fill="oklch(0.78 0.07 30)" opacity="0.55" />
      <path
        d="M31 40 Q39 36 47 40"
        fill="none"
        stroke="oklch(0.5 0.02 250)"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <path
        d="M53 40 Q61 36 69 40"
        fill="none"
        stroke="oklch(0.5 0.02 250)"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <g fill="oklch(1 0 0 / 0.35)" stroke="oklch(0.3 0.06 255)" strokeWidth="3.2">
        <circle cx="39" cy="49" r="9.5" />
        <circle cx="61" cy="49" r="9.5" />
      </g>
      <path
        d="M48.5 47 Q50 44.5 51.5 47"
        fill="none"
        stroke="oklch(0.3 0.06 255)"
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <line
        x1="29.5"
        y1="47"
        x2="22"
        y2="44"
        stroke="oklch(0.3 0.06 255)"
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <line
        x1="70.5"
        y1="47"
        x2="78"
        y2="44"
        stroke="oklch(0.3 0.06 255)"
        strokeWidth="3.2"
        strokeLinecap="round"
      />
      <circle cx="39" cy="49.5" r="3.1" fill="oklch(0.28 0.02 250)" />
      <circle cx="61" cy="49.5" r="3.1" fill="oklch(0.28 0.02 250)" />
      <path
        d="M40 66 Q50 74 60 66"
        fill="none"
        stroke="oklch(0.4 0.05 30)"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [fontStep, setFontStep] = useState(0);
  const [listening, setListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const viewportRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  // Typewriter: stream chunks go into `queueRef` and are revealed at a steady
  // pace (decouples the irregular network arrival from smooth on-screen drawing).
  const queueRef = useRef("");
  const timerRef = useRef<number | null>(null);
  const netDoneRef = useRef(false);

  const scheduleDrain = () => {
    if (timerRef.current != null) return;
    const tick = () => {
      const q = queueRef.current;
      if (q.length > 0) {
        // Reveal proportionally: faster if a backlog built up, gentle if caught up.
        const take = Math.max(1, Math.ceil(q.length / 20));
        queueRef.current = q.slice(take);
        const piece = q.slice(0, take);
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, content: m.content + piece } : m
          )
        );
      }
      if (queueRef.current.length > 0 || !netDoneRef.current) {
        timerRef.current = window.setTimeout(tick, 30);
      } else {
        timerRef.current = null;
        setIsLoading(false);
      }
    };
    timerRef.current = window.setTimeout(tick, 30);
  };

  // Clean up the timer if the component unmounts mid-stream.
  useEffect(() => {
    return () => {
      if (timerRef.current != null) window.clearTimeout(timerRef.current);
    };
  }, []);

  // Restore the saved conversation on mount (survives refresh).
  useEffect(() => {
    try {
      const saved = localStorage.getItem("jg-messages");
      if (saved) {
        const parsed = JSON.parse(saved) as Message[];
        if (Array.isArray(parsed) && parsed.length > 0) setMessages(parsed);
      }
    } catch {
      /* ignore malformed storage */
    }
  }, []);

  // Persist completed turns (skip mid-stream writes).
  useEffect(() => {
    if (isLoading) return;
    try {
      localStorage.setItem("jg-messages", JSON.stringify(messages));
    } catch {
      /* storage may be full or blocked; not critical */
    }
  }, [messages, isLoading]);

  // Set up voice dictation (Web Speech API) if the browser supports it.
  useEffect(() => {
    const w = window as typeof window & {
      SpeechRecognition?: new () => SpeechRecognitionLike;
      webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    };
    const SR = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!SR) return;

    const rec = new SR();
    rec.lang = "es-AR";
    rec.interimResults = true;
    rec.continuous = false;
    rec.onresult = (e: SpeechResultEvent) => {
      let transcript = "";
      for (let i = 0; i < e.results.length; i++) {
        transcript += e.results[i][0].transcript;
      }
      setInput(transcript);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);

    recognitionRef.current = rec;
    setVoiceSupported(true);
    return () => {
      try {
        rec.abort();
      } catch {
        /* nothing to abort */
      }
    };
  }, []);

  // Text size: scales the <html> font-size and is persisted.
  useEffect(() => {
    const saved = Number(localStorage.getItem("jg-font-step"));
    if (!Number.isNaN(saved) && saved >= 0 && saved < FONT_STEPS.length) {
      setFontStep(saved);
    }
  }, []);
  useEffect(() => {
    document.documentElement.style.fontSize = `${FONT_STEPS[fontStep].scale * 100}%`;
    localStorage.setItem("jg-font-step", String(fontStep));
  }, [fontStep]);

  // Auto-scroll to the latest content. The scrolling element is the ScrollArea's
  // inner Viewport; the rAF waits for layout to settle before measuring.
  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const id = requestAnimationFrame(() => {
      viewport.scrollTop = viewport.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [messages, isLoading]);

  function toggleMic() {
    const rec = recognitionRef.current;
    if (!rec) return;
    if (listening) {
      rec.stop();
      setListening(false);
    } else {
      setInput("");
      try {
        rec.start();
        setListening(true);
      } catch {
        /* start() throws if already running; ignore */
      }
    }
  }

  function resetConversation() {
    if (timerRef.current != null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    queueRef.current = "";
    netDoneRef.current = true;
    setIsLoading(false);
    setInput("");
    setMessages([GREETING]);
    try {
      localStorage.removeItem("jg-messages");
    } catch {
      /* ignore */
    }
  }

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    if (listening) recognitionRef.current?.stop();
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setIsLoading(true);
    queueRef.current = "";
    netDoneRef.current = false;

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });

      if (res.status === 429) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            variant: "warn",
            content:
              "Recibimos muchas consultas juntas. Esperá unos segundos y volvé a preguntar; tu consulta no se pierde.",
          },
        ]);
        setIsLoading(false);
        return;
      }

      if (!res.ok || !res.body) throw new Error(`Error: ${res.status}`);

      // NDJSON stream: 1 sources line + N text lines + a closing line.
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let pendingSources: Source[] = [];
      let started = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() ?? ""; // the last line may be incomplete

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
                { role: "assistant", content: "", sources: pendingSources },
              ]);
            }
            queueRef.current += evt.chunk; // the typewriter reveals it smoothly
            scheduleDrain();
          } else if (evt.type === "error") {
            if (!started) {
              started = true;
              setMessages((prev) => [
                ...prev,
                { role: "assistant", variant: "error", content: evt.message },
              ]);
            } else {
              queueRef.current += `\n\n${evt.message}`;
              scheduleDrain();
            }
          }
        }
      }

      netDoneRef.current = true;
      if (!started) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            variant: "error",
            content: "No pude generar una respuesta. Probá de nuevo.",
          },
        ]);
        setIsLoading(false);
      } else {
        scheduleDrain(); // ensures it finishes revealing, then lowers isLoading
      }
    } catch {
      netDoneRef.current = true;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          variant: "error",
          content: "Disculpá, algo salió mal. No es culpa tuya. Probá de nuevo.",
        },
      ]);
      setIsLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  const lastIndex = messages.length - 1;
  const showThinking = isLoading && messages[lastIndex]?.role === "user";
  const showSuggestions = messages.length === 1 && !isLoading;

  function bubbleClasses(variant?: "error" | "warn") {
    if (variant === "error")
      return "border border-jg-error-border bg-jg-error text-jg-error-ink";
    if (variant === "warn")
      return "border border-jg-warn-border bg-jg-warn text-jg-warn-ink";
    return "border border-jg-border bg-jg-surface text-jg-ink";
  }

  return (
    <div className="flex h-[100dvh] w-full flex-col overflow-hidden bg-jg-surface sm:h-[85vh] sm:max-h-[880px] sm:max-w-4xl sm:rounded-2xl sm:shadow-[0_4px_24px_rgba(0,0,0,0.08)]">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-jg-border bg-jg-surface px-4 py-3 sm:gap-4 sm:px-6 sm:py-4">
        <JubiAvatar className="h-11 w-11 sm:h-13 sm:w-13" />
        <div className="min-w-0 flex-1">
          <div className="text-xl font-bold text-jg-ink sm:text-2xl">
            JubiGestor
          </div>
          <div className="text-base text-jg-muted sm:text-lg">
            Te ayudo a entender tus trámites de ANSES, paso a paso
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {messages.length > 1 && (
            <button
              type="button"
              onClick={resetConversation}
              aria-label="Empezar una consulta nueva"
              title="Empezar una consulta nueva"
              className="flex size-11 items-center justify-center rounded-full border-2 border-jg-border-strong bg-jg-surface text-jg-brand hover:bg-black/5 focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-jg-brand"
            >
              <NewChatIcon />
            </button>
          )}
          <button
            type="button"
            onClick={() => setFontStep((s) => (s + 1) % FONT_STEPS.length)}
            aria-label={FONT_STEPS[fontStep].label}
            title={FONT_STEPS[fontStep].label}
            className="flex size-11 items-center justify-center rounded-full border-2 border-jg-border-strong bg-jg-surface text-jg-brand hover:bg-black/5 focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-jg-brand"
          >
            <span aria-hidden="true" className="leading-none">
              <span className="text-sm font-bold">A</span>
              <span className="text-lg font-bold">A</span>
            </span>
          </button>
        </div>
      </header>

      {/* Always-visible disclaimer strip */}
      <div className="bg-jg-disclaimer px-4 py-2 text-center text-sm text-jg-disclaimer-ink sm:px-6 sm:py-2.5 sm:text-base">
        Información orientativa. No reemplaza el asesoramiento oficial de ANSES.
      </div>

      {/* Conversation */}
      <ScrollArea
        className="min-h-0 flex-1 px-4 py-5 sm:px-6 sm:py-7"
        viewportRef={viewportRef}
      >
        <div className="flex flex-col gap-5 text-lg leading-relaxed sm:gap-6 sm:text-[1.1875rem]">
          {messages.map((msg, i) => {
            if (msg.role === "user") {
              return (
                <div key={i} className="flex justify-end">
                  <div className="max-w-[85%] rounded-[16px_16px_4px_16px] bg-jg-user px-4 py-3 whitespace-pre-wrap text-white sm:max-w-[82%] sm:px-5 sm:py-4">
                    {msg.content}
                  </div>
                </div>
              );
            }

            const streaming = isLoading && i === lastIndex;
            return (
              <div
                key={i}
                className="flex items-start gap-2.5 jg-msg-in sm:gap-3"
              >
                <JubiAvatar />
                <div className="flex min-w-0 max-w-[85%] flex-col gap-3 sm:max-w-[82%]">
                  <div
                    className={`rounded-[16px_16px_16px_4px] px-4 py-3 sm:px-5 sm:py-4 ${bubbleClasses(msg.variant)}`}
                    role="log"
                    aria-live="polite"
                  >
                    {msg.variant ? (
                      // Error/warn: icon + text, so meaning is not conveyed by color alone.
                      <div className="flex items-start gap-2">
                        <AlertIcon />
                        <div className="min-w-0">
                          <Markdown content={msg.content} />
                        </div>
                      </div>
                    ) : (
                      <>
                        <Markdown content={msg.content} />
                        {streaming && (
                          <span className="jg-caret" aria-hidden="true" />
                        )}
                      </>
                    )}
                  </div>

                  {!streaming && msg.sources && msg.sources.length > 0 && (
                    <div className="jg-sources-in flex flex-col gap-3.5 rounded-xl border border-jg-sources-border bg-jg-sources px-4 py-4 sm:px-5">
                      <div className="text-base font-bold tracking-wide text-jg-sources-label uppercase">
                        Fuentes oficiales
                      </div>
                      {msg.sources.map((s, j) => (
                        <div key={j} className="flex flex-col gap-1">
                          <div className="text-lg font-bold text-jg-ink">
                            <span aria-hidden="true">📄 </span>
                            {s.title}
                          </div>
                          <div className="text-base text-jg-muted">
                            Última actualización: {formatDate(s.published_at)}
                          </div>
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg font-bold text-jg-link underline underline-offset-[3px]"
                          >
                            Ver en la página oficial →
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {showSuggestions && (
            <div className="flex flex-col gap-2.5">
              <p className="text-base text-jg-muted">
                Podés empezar tocando una de estas preguntas:
              </p>
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => sendMessage(q)}
                  className="rounded-xl border-2 border-jg-border-strong bg-jg-surface px-4 py-3 text-left text-lg text-jg-ink hover:bg-jg-sources focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-jg-brand"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {showThinking && (
            <div className="flex items-start gap-2.5 jg-msg-in sm:gap-3">
              <JubiAvatar />
              <div
                className="flex items-center gap-3 rounded-[16px_16px_16px_4px] border border-jg-border bg-jg-surface px-4 py-3 text-jg-muted sm:px-5 sm:py-4"
                role="status"
              >
                <span className="flex gap-1.5" aria-hidden="true">
                  <span className="jg-dot" />
                  <span className="jg-dot" />
                  <span className="jg-dot" />
                </span>
                Buscando en las fuentes oficiales…
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t border-jg-border bg-jg-surface px-4 py-3 sm:gap-3 sm:px-6 sm:py-5"
      >
        <button
          type="button"
          onClick={toggleMic}
          disabled={isLoading || !voiceSupported}
          aria-label={
            !voiceSupported
              ? "El dictado por voz no está disponible en este navegador"
              : listening
                ? "Dejar de grabar"
                : "Grabar tu pregunta por voz"
          }
          title={
            !voiceSupported
              ? "Tu navegador no permite dictar por voz. Escribí tu pregunta."
              : listening
                ? "Tocá para dejar de grabar"
                : "Tocá y hablá tu pregunta"
          }
          className={`flex size-12 shrink-0 items-center justify-center rounded-2xl border-2 focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-jg-brand disabled:opacity-40 sm:size-15 ${
            listening
              ? "animate-pulse border-red-500 bg-red-50 text-red-600"
              : "border-jg-border-strong bg-jg-surface text-jg-brand"
          }`}
        >
          <MicIcon />
        </button>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={listening ? "Escuchando… hablá tu pregunta" : "Escribí tu pregunta acá…"}
          disabled={isLoading}
          aria-label="Tu consulta"
          className="h-12 min-w-0 flex-1 rounded-2xl border-2 border-jg-border-strong bg-jg-surface px-4 text-lg text-jg-ink outline-none focus-visible:border-jg-brand focus-visible:ring-[3px] focus-visible:ring-jg-brand/30 disabled:opacity-60 sm:h-15 sm:px-5 sm:text-[1.1875rem]"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="h-12 shrink-0 rounded-2xl bg-jg-brand px-4 text-lg font-bold text-white hover:bg-jg-brand-strong focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-jg-ink disabled:opacity-50 sm:h-15 sm:px-8 sm:text-[1.1875rem]"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}

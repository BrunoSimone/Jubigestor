import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Renderiza Markdown con espaciado compacto pensado para las burbujas del chat.
// react-markdown NO interpreta HTML crudo por defecto, así que es seguro frente a XSS.
export function Markdown({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        ul: ({ children }) => (
          <ul className="mb-2 list-disc pl-5 last:mb-0">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="mb-2 list-decimal pl-5 last:mb-0">{children}</ol>
        ),
        li: ({ children }) => <li className="mb-0.5">{children}</li>,
        strong: ({ children }) => (
          <strong className="font-semibold">{children}</strong>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-700 underline"
          >
            {children}
          </a>
        ),
        h1: ({ children }) => (
          <h3 className="mb-2 text-base font-semibold">{children}</h3>
        ),
        h2: ({ children }) => (
          <h3 className="mb-2 text-base font-semibold">{children}</h3>
        ),
        h3: ({ children }) => (
          <h3 className="mb-1 font-semibold">{children}</h3>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

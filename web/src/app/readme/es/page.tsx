import fs from "node:fs";
import path from "node:path";
import type { Metadata } from "next";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import { visit } from "unist-util-visit";
import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";

const REPO_RAW = "https://raw.githubusercontent.com/junjslee/episteme/master";
const REPO_BLOB = "https://github.com/junjslee/episteme/blob/master";

function rewriteUrl(url: string | undefined | null): string {
  if (!url) return "";
  if (/^(https?:|mailto:|#|data:)/.test(url)) return url;
  const clean = url.replace(/^\.\//, "");
  if (/\.(svg|png|jpg|jpeg|gif|webp|mp4|cast|ico)$/i.test(clean)) {
    return `${REPO_RAW}/${clean}`;
  }
  return `${REPO_BLOB}/${clean}`;
}

function rewriteSrcSet(value: string): string {
  return value
    .split(",")
    .map((part) => {
      const trimmed = part.trim();
      if (!trimmed) return trimmed;
      const [url, ...descriptors] = trimmed.split(/\s+/);
      return [rewriteUrl(url), ...descriptors].join(" ");
    })
    .join(", ");
}

function rehypeRewriteRelativeUrls() {
  return (tree: unknown) => {
    visit(tree as never, "element", (node: { properties?: Record<string, unknown> }) => {
      const props = node.properties;
      if (!props) return;
      if (typeof props.src === "string") props.src = rewriteUrl(props.src);
      if (typeof props.href === "string") props.href = rewriteUrl(props.href);
      const srcSet = props.srcSet ?? props.srcset;
      if (typeof srcSet === "string") {
        props.srcSet = rewriteSrcSet(srcSet);
        delete props.srcset;
      }
    });
  };
}

function readReadmeEs(): string {
  const candidates = [
    path.join(/* turbopackIgnore: true */ process.cwd(), "..", "README.es.md"),
    path.join(/* turbopackIgnore: true */ process.cwd(), "README.es.md"),
  ];
  for (const candidate of candidates) {
    try {
      return fs.readFileSync(candidate, "utf8");
    } catch {
      continue;
    }
  }
  throw new Error(
    `README.es.md not reachable. Tried: ${candidates.join(" · ")}. ` +
      `If deploying with web/ as the project root, copy README.es.md into web/ at build time.`,
  );
}

const components: Components = {
  h1: (props) => (
    <h1 className="mt-12 mb-6 font-display text-4xl tracking-tight text-bone md:text-5xl" {...props} />
  ),
  h2: (props) => (
    <h2 className="mt-12 mb-4 border-b border-hairline pb-2 font-display text-2xl tracking-tight text-bone md:text-3xl" {...props} />
  ),
  h3: (props) => (
    <h3 className="mt-8 mb-3 font-display text-xl tracking-tight text-bone md:text-2xl" {...props} />
  ),
  h4: (props) => <h4 className="mt-6 mb-2 font-sans text-lg font-semibold text-bone" {...props} />,
  p: (props) => <p className="my-4 leading-relaxed text-ash" {...props} />,
  a: ({ href, ...rest }) => (
    <a
      href={typeof href === "string" ? rewriteUrl(href) : href}
      className="text-chain decoration-chain/50 underline-offset-4 hover:underline"
      {...rest}
    />
  ),
  ul: (props) => <ul className="my-4 list-disc space-y-2 pl-6 text-ash marker:text-muted" {...props} />,
  ol: (props) => <ol className="my-4 list-decimal space-y-2 pl-6 text-ash marker:text-muted" {...props} />,
  li: (props) => <li className="leading-relaxed" {...props} />,
  code: ({ className, children, ...rest }) => {
    const isBlock = (className ?? "").startsWith("language-");
    if (isBlock) {
      return (
        <code className={`block font-mono text-sm ${className ?? ""}`} {...rest}>
          {children}
        </code>
      );
    }
    return (
      <code
        className="rounded border border-hairline bg-elevated px-1.5 py-0.5 font-mono text-[0.9em] text-bone"
        {...rest}
      >
        {children}
      </code>
    );
  },
  pre: (props) => (
    <pre
      className="my-6 overflow-x-auto rounded-lg border border-hairline bg-elevated p-4 text-sm leading-relaxed"
      {...props}
    />
  ),
  blockquote: (props) => (
    <blockquote className="my-4 border-l-2 border-chain/40 pl-4 italic text-ash" {...props} />
  ),
  hr: () => <hr className="my-12 border-hairline" />,
  img: ({ src, alt, ...rest }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={typeof src === "string" ? rewriteUrl(src) : ""}
      alt={alt ?? ""}
      className="my-6 max-w-full rounded border border-hairline"
      {...rest}
    />
  ),
  table: (props) => (
    <div className="my-6 overflow-x-auto">
      <table className="w-full border-collapse text-sm" {...props} />
    </div>
  ),
  th: (props) => (
    <th className="border border-hairline bg-elevated px-3 py-2 text-left font-semibold text-bone" {...props} />
  ),
  td: (props) => <td className="border border-hairline px-3 py-2 text-ash" {...props} />,
};

export const metadata: Metadata = {
  title: "README (Español) — episteme",
  description:
    "README.md en español. Un Thinking Framework para el agente de IA que ya usas — Sovereign Cognitive Kernel.",
};

export default function ReadmeEsPage() {
  const markdown = readReadmeEs();
  return (
    <>
      <Header />
      <main className="mx-auto max-w-3xl px-6 py-16 md:py-24" lang="es">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[
            rehypeRaw,
            rehypeRewriteRelativeUrls,
            rehypeSlug,
            [rehypeAutolinkHeadings, { behavior: "wrap" }],
          ]}
          components={components}
          urlTransform={(url) => rewriteUrl(url)}
        >
          {markdown}
        </ReactMarkdown>
      </main>
      <Footer />
    </>
  );
}

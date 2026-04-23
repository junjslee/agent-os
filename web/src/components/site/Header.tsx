import Link from "next/link";
import { AmbientStatus } from "./AmbientStatus";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-hairline/60 bg-void/40 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4 md:px-12">
        <Link
          href="/"
          className="flex shrink-0 items-center gap-3 font-display text-[1.125rem] lowercase tracking-tight text-bone"
        >
          <img
            src="/logo-mark-dark.svg"
            alt=""
            aria-hidden
            className="size-7 shrink-0"
          />
          <span className="leading-none">episteme</span>
          <span className="hidden sm:inline font-mono text-[0.6875rem] uppercase tracking-[0.2em] text-muted">
            rc · v1.0
          </span>
        </Link>

        <AmbientStatus />

        <ul className="hidden shrink-0 items-center gap-5 font-mono text-[0.75rem] uppercase tracking-[0.12em] text-ash md:flex">
          <li className="hidden lg:block">
            <Link
              href="/#framework"
              className="flex items-center gap-1.5 group transition-colors hover:text-bone"
            >
              <span aria-hidden className="text-[0.625rem] text-whisper group-hover:text-ash transition-colors">↓</span>
              framework
            </Link>
          </li>
          <li className="hidden lg:block">
            <Link
              href="/#surface"
              className="flex items-center gap-1.5 group transition-colors hover:text-bone"
            >
              <span aria-hidden className="text-[0.625rem] text-whisper group-hover:text-ash transition-colors">↓</span>
              surface
            </Link>
          </li>
          <li className="hidden lg:block">
            <Link
              href="/#protocols"
              className="flex items-center gap-1.5 group transition-colors hover:text-bone"
            >
              <span aria-hidden className="text-[0.625rem] text-whisper group-hover:text-ash transition-colors">↓</span>
              protocols
            </Link>
          </li>
          <li>
            <Link
              href="/commands"
              className="flex items-center gap-1.5 group transition-colors hover:text-bone"
            >
              <span aria-hidden className="text-[0.625rem] text-whisper group-hover:text-ash transition-colors">→</span>
              commands
            </Link>
          </li>
          <li>
            <Link
              href="/dashboard"
              className="inline-block whitespace-nowrap border border-line px-3 py-1.5 text-bone transition-colors hover:border-chain hover:text-chain"
            >
              dashboard →
            </Link>
          </li>
          <li
            aria-label="locale"
            className="hidden lg:flex items-center gap-1.5 pl-4 ml-1 border-l border-hairline/40 font-mono text-[0.625rem] uppercase tracking-[0.14em] text-muted"
          >
            <Link href="/readme" className="transition-colors hover:text-ash" aria-label="English README">
              EN
            </Link>
            <span aria-hidden className="text-whisper">·</span>
            <Link href="/readme/ko" className="transition-colors hover:text-ash" aria-label="한국어 README">
              한
            </Link>
            <span aria-hidden className="text-whisper">·</span>
            <Link href="/readme/es" className="transition-colors hover:text-ash" aria-label="Español README">
              ES
            </Link>
            <span aria-hidden className="text-whisper">·</span>
            <Link href="/readme/zh" className="transition-colors hover:text-ash" aria-label="中文 README">
              中
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}

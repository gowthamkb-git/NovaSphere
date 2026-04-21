import Link from "next/link";

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-20 border-b border-white/10 bg-[#090f2f]/70 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5 lg:px-10">
        <Link
          className="group relative flex items-center gap-3 transition duration-300 hover:scale-[1.02]"
          href="/"
        >
          <span className="relative flex h-9 w-9 items-center justify-center rounded-full bg-[radial-gradient(circle_at_35%_30%,_#c084fc,_#7c3aed_55%,_#312e81)] shadow-[0_0_22px_rgba(168,85,247,0.45)]">
            <span className="absolute inset-[7px] rounded-full border border-white/20" />
            <span className="h-2.5 w-2.5 rounded-full bg-white/90" />
          </span>
          <span className="bg-gradient-to-r from-white via-slate-100 to-violet-200 bg-clip-text text-lg font-semibold tracking-tight text-transparent">
            NovaSphere AI
          </span>
        </Link>

        <nav className="hidden items-center gap-10 text-sm text-white/75 lg:flex">
          <a className="transition hover:text-white" href="#home">
            Home
          </a>
          <a className="transition hover:text-white" href="#features">
            Features
          </a>
          <a className="transition hover:text-white" href="#about">
            About
          </a>
          <a className="transition hover:text-white" href="#pricing">
            Pricing
          </a>
          <a className="transition hover:text-white" href="#contact">
            Contact
          </a>
        </nav>

        <div className="hidden items-center gap-4 lg:flex">
          <Link
            className="text-sm font-medium text-white/80 transition hover:text-white"
            href="/login"
          >
            Login
          </Link>
          <Link
            className="rounded-xl bg-[linear-gradient(135deg,_#7c3aed,_#d946ef)] px-5 py-2.5 text-sm font-semibold text-white shadow-[0_12px_28px_rgba(168,85,247,0.35)] transition hover:scale-[1.02]"
            href="/signup"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </header>
  );
}

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-20 border-b border-white/12 bg-white/5 backdrop-blur-[2px]">
      <div className="flex justify-center px-4 py-6">
        <button
          className="group relative transition duration-300 hover:scale-105"
          type="button"
        >
          <span className="absolute -left-7 top-1/2 h-8 w-8 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,_rgba(255,255,255,0.95)_0%,_rgba(103,232,249,0.9)_24%,_rgba(124,58,237,0.75)_55%,_rgba(124,58,237,0)_76%)] blur-[1px] transition duration-300 group-hover:scale-110 group-hover:drop-shadow-[0_0_18px_rgba(103,232,249,0.55)]" />
          <span className="bg-gradient-to-r from-white via-sky-100 to-fuchsia-200 bg-clip-text text-[2.15rem] font-semibold tracking-tight text-transparent drop-shadow-[0_0_14px_rgba(255,255,255,0.18)] sm:text-[2.45rem]">
            NovaSphere
          </span>
        </button>
      </div>
    </header>
  );
}

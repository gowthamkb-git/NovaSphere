import { ChatWidget } from "@/components/ChatWidget";
import { Header } from "@/components/Header";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#244acb] text-white">
      <div className="absolute inset-0 bg-gradient-to-br from-[#1d40af] via-[#58a5f2] to-[#d946ef]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_36%_39%,_rgba(183,236,255,0.72),_transparent_24%),radial-gradient(circle_at_72%_53%,_rgba(255,210,248,0.78),_transparent_21%),radial-gradient(circle_at_33%_85%,_rgba(95,70,255,0.6),_transparent_34%)]" />
      <div className="absolute inset-x-0 top-0 h-28 bg-[linear-gradient(180deg,_rgba(20,52,171,0.82),_rgba(20,52,171,0.22)_78%,_transparent)]" />
      <div className="absolute left-[-8%] right-[-8%] bottom-[14%] h-[40%] rounded-[50%] bg-[radial-gradient(circle_at_50%_50%,_rgba(255,255,255,0.42),_rgba(255,255,255,0.12)_36%,_rgba(255,255,255,0)_68%)] blur-xl" />
      <div className="absolute left-[6%] top-[43%] h-48 w-48 bg-white/10 blur-3xl" />
      <div className="absolute right-[8%] bottom-[12%] h-48 w-48 rounded-full bg-fuchsia-300/25 blur-3xl" />

      <div className="relative flex min-h-screen flex-col">
        <Header />

        <section className="relative flex flex-1 pt-24">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_8%_42%,_rgba(255,255,255,0.8)_0,_rgba(255,255,255,0)_1.6px),radial-gradient(circle_at_18%_72%,_rgba(255,255,255,0.8)_0,_rgba(255,255,255,0)_1.2px),radial-gradient(circle_at_28%_62%,_rgba(255,255,255,0.8)_0,_rgba(255,255,255,0)_1.2px),radial-gradient(circle_at_73%_59%,_rgba(255,255,255,0.72)_0,_rgba(255,255,255,0)_1.5px),radial-gradient(circle_at_94%_40%,_rgba(255,255,255,0.82)_0,_rgba(255,255,255,0)_1.5px),radial-gradient(circle_at_92%_66%,_rgba(255,255,255,0.7)_0,_rgba(255,255,255,0)_1.4px)] [background-size:230px_230px]" />
        </section>

        <ChatWidget />
      </div>
    </main>
  );
}

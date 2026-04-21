import { Header } from "@/components/Header";

export default function HomePage() {
  return (
    <main
      className="relative min-h-screen overflow-x-hidden bg-[#070b24] text-white"
      id="home"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.2),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(168,85,247,0.2),_transparent_30%),linear-gradient(180deg,_#0a1030_0%,_#090c24_52%,_#140b35_100%)]" />
      <div className="absolute -left-12 top-[58%] h-32 w-32 rounded-full border border-violet-400/25 bg-violet-500/10 blur-sm sm:h-44 sm:w-44" />
      <div className="absolute -right-10 top-28 h-40 w-40 rounded-full border border-fuchsia-400/25 bg-fuchsia-500/10 blur-sm sm:h-52 sm:w-52" />
      <div className="absolute bottom-[-8%] left-1/2 h-56 w-[70%] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,_rgba(217,70,239,0.34),_rgba(124,58,237,0.18)_35%,_transparent_72%)] blur-3xl" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,_rgba(255,255,255,0.12)_0,_rgba(255,255,255,0)_1.5px),radial-gradient(circle_at_80%_18%,_rgba(255,255,255,0.1)_0,_rgba(255,255,255,0)_1.5px),radial-gradient(circle_at_72%_72%,_rgba(255,255,255,0.1)_0,_rgba(255,255,255,0)_1.5px)] [background-size:240px_240px]" />

      <div className="relative flex min-h-screen flex-col">
        <Header />

        <section className="relative flex flex-1 items-center px-4 pb-16 pt-28 sm:px-6 lg:px-10 lg:pt-32">
          <div className="mx-auto w-full max-w-7xl">
            <div className="relative overflow-hidden rounded-[32px] border border-violet-300/35 bg-[linear-gradient(145deg,rgba(29,37,89,0.9),rgba(24,18,68,0.88)_58%,rgba(58,25,95,0.92))] px-6 py-14 shadow-[0_30px_120px_rgba(25,15,71,0.65)] sm:px-10 lg:px-16 lg:py-20">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(96,165,250,0.2),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(217,70,239,0.2),_transparent_24%),radial-gradient(circle_at_bottom_center,_rgba(168,85,247,0.24),_transparent_34%)]" />
              <div className="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-violet-200/70 to-transparent" />

              <div className="relative mx-auto flex max-w-4xl flex-col items-center text-center">
                <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-violet-300/25 bg-white/8 px-4 py-2 text-sm font-medium text-violet-100 shadow-[0_8px_30px_rgba(15,23,42,0.18)]">
                  <span className="h-2 w-2 rounded-full bg-violet-300" />
                  AI-Powered Knowledge Assistant
                </div>

                <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl lg:text-7xl">
                  Your Company Knowledge,
                  <span className="block bg-gradient-to-r from-violet-300 via-fuchsia-300 to-purple-400 bg-clip-text text-transparent">
                    Instantly Accessible
                  </span>
                </h1>

                <p className="mt-6 max-w-2xl text-base leading-8 text-slate-200/82 sm:text-lg">
                  Ask anything about HR policies, onboarding, SOPs, and company
                  processes. Get fast, accurate answers in one place so your team
                  can move with confidence.
                </p>

                <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
                  <button
                    className="rounded-2xl bg-[linear-gradient(135deg,_#7c3aed,_#d946ef)] px-8 py-4 text-base font-semibold text-white shadow-[0_18px_40px_rgba(168,85,247,0.35)] transition hover:scale-[1.02]"
                    type="button"
                  >
                    Get Started
                  </button>
                  <button
                    className="rounded-2xl border border-white/20 bg-white/5 px-8 py-4 text-base font-medium text-white/92 transition hover:bg-white/10"
                    type="button"
                  >
                    Try Demo
                  </button>
                </div>

                <div className="mt-14 grid w-full max-w-3xl gap-4 sm:grid-cols-3">
                  <div className="rounded-2xl border border-white/10 bg-white/6 px-5 py-5 backdrop-blur-sm">
                    <p className="text-sm font-semibold text-white">Accurate Answers</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300/85">
                      Ask company questions and get structured responses quickly.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/6 px-5 py-5 backdrop-blur-sm">
                    <p className="text-sm font-semibold text-white">Instant Responses</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300/85">
                      Reduce search time and help employees find answers faster.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/6 px-5 py-5 backdrop-blur-sm">
                    <p className="text-sm font-semibold text-white">Secure &amp; Private</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300/85">
                      Keep internal knowledge accessible in a focused assistant experience.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section
          className="relative px-4 py-10 sm:px-6 lg:px-10 lg:py-14"
          id="features"
        >
          <div className="mx-auto max-w-7xl">
            <div className="mb-10 max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-violet-300/90">
                Features
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Built like a real workplace knowledge product
              </h2>
              <p className="mt-4 text-base leading-8 text-slate-300/85">
                NovaSphere brings company knowledge, process guidance, and internal
                answers into one assistant experience designed for everyday work.
              </p>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-sm">
                <div className="mb-5 inline-flex rounded-2xl bg-violet-500/15 px-3 py-2 text-sm font-medium text-violet-200">
                  Knowledge Search
                </div>
                <h3 className="text-2xl font-semibold text-white">
                  Instant answers from your company docs
                </h3>
                <p className="mt-4 text-sm leading-7 text-slate-300/80">
                  Surface policy details, onboarding steps, SOP guidance, and internal
                  references in a conversational workflow instead of making people dig
                  through scattered folders and documents.
                </p>
              </article>

              <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-sm">
                <div className="mb-5 inline-flex rounded-2xl bg-sky-500/15 px-3 py-2 text-sm font-medium text-sky-200">
                  Team Enablement
                </div>
                <h3 className="text-2xl font-semibold text-white">
                  Faster onboarding and fewer repetitive questions
                </h3>
                <p className="mt-4 text-sm leading-7 text-slate-300/80">
                  Give new employees a guided way to explore benefits, leave policy,
                  workflows, and operational processes while reducing repeated requests
                  to HR, ops, and managers.
                </p>
              </article>

              <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-sm">
                <div className="mb-5 inline-flex rounded-2xl bg-fuchsia-500/15 px-3 py-2 text-sm font-medium text-fuchsia-200">
                  Trusted Responses
                </div>
                <h3 className="text-2xl font-semibold text-white">
                  Context-aware replies with reliable internal grounding
                </h3>
                <p className="mt-4 text-sm leading-7 text-slate-300/80">
                  Keep answers aligned to your organization knowledge base so employees
                  get a focused assistant that feels useful, fast, and relevant to how
                  the business actually operates.
                </p>
              </article>
            </div>
          </div>
        </section>

        <section
          className="relative px-4 py-10 sm:px-6 lg:px-10 lg:py-14"
          id="about"
        >
          <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-[30px] border border-white/10 bg-[linear-gradient(145deg,rgba(16,24,56,0.9),rgba(21,18,61,0.86))] p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-violet-300/90">
                About
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                One assistant for policies, processes, and internal know-how
              </h2>
              <p className="mt-5 text-base leading-8 text-slate-300/85">
                NovaSphere is designed for teams that need fast access to operational
                knowledge without disrupting the tools and workflows they already use.
                It turns company information into a cleaner, easier product experience.
              </p>
            </div>

            <div className="grid gap-4">
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6">
                <p className="text-sm font-semibold text-white">For HR and People Ops</p>
                <p className="mt-2 text-sm leading-7 text-slate-300/80">
                  Share benefits, leave policies, and onboarding guidance in one place.
                </p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6">
                <p className="text-sm font-semibold text-white">For Operations</p>
                <p className="mt-2 text-sm leading-7 text-slate-300/80">
                  Help teams follow SOPs and recurring workflows with less friction.
                </p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6">
                <p className="text-sm font-semibold text-white">For Employees</p>
                <p className="mt-2 text-sm leading-7 text-slate-300/80">
                  Reduce time spent hunting for answers across scattered internal docs.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          className="relative px-4 py-10 sm:px-6 lg:px-10 lg:py-14"
          id="pricing"
        >
          <div className="mx-auto max-w-7xl">
            <div className="mb-10 max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-violet-300/90">
                Pricing
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Simple plans for teams adopting internal AI support
              </h2>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              <div className="rounded-[28px] border border-white/10 bg-white/6 p-7">
                <p className="text-sm font-semibold text-slate-200">Starter</p>
                <p className="mt-4 text-4xl font-semibold text-white">$19</p>
                <p className="mt-1 text-sm text-slate-400">per user / month</p>
                <p className="mt-5 text-sm leading-7 text-slate-300/80">
                  Best for smaller teams exploring a knowledge assistant for core
                  internal documentation.
                </p>
              </div>

              <div className="rounded-[28px] border border-violet-400/35 bg-[linear-gradient(180deg,rgba(124,58,237,0.24),rgba(255,255,255,0.06))] p-7 shadow-[0_18px_50px_rgba(124,58,237,0.18)]">
                <p className="text-sm font-semibold text-violet-200">Growth</p>
                <p className="mt-4 text-4xl font-semibold text-white">$49</p>
                <p className="mt-1 text-sm text-slate-300">per team seat / month</p>
                <p className="mt-5 text-sm leading-7 text-slate-200/85">
                  Ideal for growing organizations that want richer knowledge access
                  across HR, onboarding, SOPs, and department workflows.
                </p>
              </div>

              <div className="rounded-[28px] border border-white/10 bg-white/6 p-7">
                <p className="text-sm font-semibold text-slate-200">Enterprise</p>
                <p className="mt-4 text-4xl font-semibold text-white">Custom</p>
                <p className="mt-1 text-sm text-slate-400">tailored deployment</p>
                <p className="mt-5 text-sm leading-7 text-slate-300/80">
                  For larger companies that need customized rollout, governance, and
                  controlled knowledge experiences.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          className="relative px-4 pb-28 pt-10 sm:px-6 lg:px-10 lg:pt-14"
          id="contact"
        >
          <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
            <div className="rounded-[30px] border border-white/10 bg-[linear-gradient(145deg,rgba(18,22,56,0.94),rgba(14,40,67,0.82))] p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-violet-300/90">
                Contact
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                Bring NovaSphere into your internal support workflow
              </h2>
              <p className="mt-5 text-base leading-8 text-slate-300/85">
                Talk to us about how your team manages knowledge today and where a
                dedicated company assistant can reduce friction.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6">
                <p className="text-sm font-semibold text-white">Email</p>
                <p className="mt-2 text-sm text-slate-300/80">hello@novasphere.ai</p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6">
                <p className="text-sm font-semibold text-white">Sales</p>
                <p className="mt-2 text-sm text-slate-300/80">Book a tailored product walkthrough</p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/6 p-6 sm:col-span-2">
                <p className="text-sm font-semibold text-white">Headquarters</p>
                <p className="mt-2 text-sm leading-7 text-slate-300/80">
                  NovaSphere AI
                  <br />
                  Internal Knowledge Systems
                  <br />
                  Built for modern teams
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

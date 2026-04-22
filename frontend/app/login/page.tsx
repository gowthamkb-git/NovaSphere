"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

import API from "@/lib/api";
import { storeAuthSession } from "@/lib/auth";
import type { AuthResponse } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await API.post<AuthResponse>("/auth/login", {
        email,
        password,
      });
      storeAuthSession(response.data);
      router.push("/workspace");
    } catch (requestError) {
      const message = axios.isAxiosError(requestError)
        ? requestError.response?.data?.detail ?? "Login failed."
        : "Login failed.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#070b24] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.2),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(168,85,247,0.2),_transparent_30%),linear-gradient(180deg,_#0a1030_0%,_#090c24_52%,_#140b35_100%)]" />
      <div className="absolute -left-12 top-[20%] h-40 w-40 rounded-full border border-violet-400/20 bg-violet-500/10 blur-sm" />
      <div className="absolute -right-10 top-16 h-52 w-52 rounded-full border border-fuchsia-400/20 bg-fuchsia-500/10 blur-sm" />
      <div className="absolute bottom-[-8%] left-1/2 h-56 w-[70%] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,_rgba(217,70,239,0.28),_rgba(124,58,237,0.18)_35%,_transparent_72%)] blur-3xl" />

      <section className="relative flex min-h-screen items-center justify-center px-4 py-10 sm:px-6 lg:px-10">
        <div className="mx-auto grid w-full max-w-6xl overflow-hidden rounded-[34px] border border-violet-300/25 bg-[linear-gradient(145deg,rgba(20,28,66,0.92),rgba(20,18,57,0.9)_58%,rgba(45,20,79,0.9))] shadow-[0_30px_120px_rgba(25,15,71,0.65)] lg:grid-cols-[1.05fr_0.95fr]">
          <div className="relative p-8 sm:p-12 lg:p-14">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(96,165,250,0.16),_transparent_30%),radial-gradient(circle_at_bottom_left,_rgba(217,70,239,0.18),_transparent_34%)]" />
            <div className="relative">
              <Link
                className="inline-flex items-center gap-3 text-sm font-medium text-violet-100/90"
                href="/"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[radial-gradient(circle_at_35%_30%,_#c084fc,_#7c3aed_55%,_#312e81)] shadow-[0_0_22px_rgba(168,85,247,0.45)]">
                  <span className="h-2.5 w-2.5 rounded-full bg-white/90" />
                </span>
                NovaSphere AI
              </Link>

              <div className="mt-14 max-w-md">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-violet-200/85">
                  Welcome Back
                </p>
                <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  Sign in to your company workspace
                </h1>
                <p className="mt-5 text-base leading-8 text-slate-300/80">
                  Access your NovaSphere workspace, resume your registered bot
                  conversations, and keep internal knowledge available in one place.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 bg-white/[0.04] p-8 sm:p-10 lg:border-l lg:border-t-0 lg:p-12">
            <div className="mx-auto w-full max-w-md">
              <p className="text-sm uppercase tracking-[0.22em] text-violet-200/80">
                Login
              </p>
              <h2 className="mt-3 text-3xl font-semibold text-white">Continue to NovaSphere</h2>
              <p className="mt-3 text-sm leading-7 text-slate-300/75">
                Use your registered account to enter the Teams-style workspace.
              </p>

              <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor="email">
                    Email
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/8 px-4 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-400 focus:border-violet-300/50 focus:bg-white/10"
                    id="email"
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="Enter your work email"
                    type="email"
                    value={email}
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor="password">
                    Password
                  </label>
                  <input
                    className="w-full rounded-2xl border border-white/10 bg-white/8 px-4 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-400 focus:border-violet-300/50 focus:bg-white/10"
                    id="password"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    type="password"
                    value={password}
                  />
                </div>

                {error ? (
                  <p className="text-sm text-rose-300">{error}</p>
                ) : null}

                <button
                  className="w-full rounded-2xl bg-[linear-gradient(135deg,_#7c3aed,_#d946ef)] px-5 py-3.5 text-sm font-semibold text-white shadow-[0_16px_36px_rgba(168,85,247,0.32)] transition hover:scale-[1.01] disabled:opacity-70 disabled:hover:scale-100"
                  disabled={isSubmitting}
                  type="submit"
                >
                  {isSubmitting ? "Signing in..." : "Login"}
                </button>
              </form>

              <p className="mt-6 text-sm text-slate-300/78">
                Don&apos;t have an account yet?{" "}
                <Link className="font-semibold text-violet-200 hover:text-white" href="/signup">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

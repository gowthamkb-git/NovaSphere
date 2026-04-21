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
    <main className="relative min-h-screen overflow-hidden bg-[#f4efff] text-slate-900">
      <div className="absolute -left-20 -top-20 h-72 w-72 rounded-full bg-violet-200/50 blur-sm" />
      <div className="absolute -bottom-24 -right-20 h-72 w-72 rounded-full bg-violet-200/45 blur-sm" />

      <section className="relative flex min-h-screen items-center justify-center px-4 py-10">
        <div className="relative w-full max-w-4xl overflow-hidden rounded-none bg-[linear-gradient(180deg,_#8451ea_0%,_#6e45cf_35%,_#513296_100%)] px-6 py-14 shadow-[0_24px_80px_rgba(77,43,150,0.28)] sm:rounded-[2px] sm:px-10 lg:px-16">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(110%_55%_at_0%_20%,_rgba(255,255,255,0.08),_transparent_42%),radial-gradient(90%_45%_at_100%_18%,_rgba(255,255,255,0.12),_transparent_34%),radial-gradient(80%_35%_at_20%_82%,_rgba(255,255,255,0.12),_transparent_36%)]" />
          <div className="pointer-events-none absolute left-0 top-[18%] h-px w-full bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.22),transparent)]" />
          <div className="pointer-events-none absolute bottom-[26%] left-0 h-px w-full bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent)]" />

          <div className="relative mx-auto w-full max-w-md rounded-[22px] bg-white px-6 py-8 shadow-[0_22px_60px_rgba(34,17,76,0.28)] sm:px-8">
            <h1 className="text-center text-3xl font-semibold tracking-tight text-slate-900">
              Login
            </h1>
            <p className="mt-2 text-center text-sm text-slate-500">
              Please enter your details to login.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-2">
              <button
                className="rounded-xl bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
                type="button"
              >
                Google
              </button>
              <button
                className="rounded-xl bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-200"
                type="button"
              >
                Apple
              </button>
            </div>

            <div className="my-5 flex items-center gap-4 text-sm text-slate-400">
              <div className="h-px flex-1 bg-slate-200" />
              <span>Or</span>
              <div className="h-px flex-1 bg-slate-200" />
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="email">
                  Email
                </label>
                <input
                  className="w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-400 focus:bg-white"
                  id="email"
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="Enter your Email"
                  type="email"
                  value={email}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="password">
                  Password
                </label>
                <input
                  className="w-full rounded-xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-400 focus:bg-white"
                  id="password"
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  type="password"
                  value={password}
                />
              </div>

              <div className="flex items-center justify-between gap-4 text-sm">
                <label className="flex items-center gap-2 text-slate-600">
                  <input className="h-4 w-4 rounded border-slate-300" type="checkbox" />
                  Remember me
                </label>
                <Link className="font-medium text-violet-500 hover:text-violet-600" href="#">
                  Forgot Password
                </Link>
              </div>

              {error ? (
                <p className="text-sm text-rose-500">{error}</p>
              ) : null}

              <button
                className="mt-2 w-full rounded-xl bg-[linear-gradient(90deg,_#8b5cf6,_#7c3aed)] px-4 py-3 text-sm font-semibold text-white shadow-[0_14px_34px_rgba(124,58,237,0.28)] transition hover:scale-[1.01]"
                disabled={isSubmitting}
                type="submit"
              >
                {isSubmitting ? "Signing in..." : "Log In"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-500">
              Don&apos;t have an account yet?{" "}
              <Link className="font-semibold text-violet-500 hover:text-violet-600" href="/signup">
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

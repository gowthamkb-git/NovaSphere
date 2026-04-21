"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

import API from "@/lib/api";
import { storeAuthSession } from "@/lib/auth";
import type { AuthResponse } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await API.post<AuthResponse>("/auth/signup", {
        full_name: fullName,
        email,
        password,
      });
      storeAuthSession(response.data);
      router.push("/workspace");
    } catch (requestError) {
      const message = axios.isAxiosError(requestError)
        ? requestError.response?.data?.detail ?? "Sign up failed."
        : "Sign up failed.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[linear-gradient(180deg,_#14486b_0%,_#0d3149_100%)] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.08),_transparent_28%)]" />

      <section className="relative flex min-h-screen items-center justify-center px-4 py-10">
        <div className="relative w-full max-w-[32rem] rounded-[14px] border border-white/25 bg-[linear-gradient(180deg,rgba(169,202,227,0.45),rgba(22,56,79,0.4))] p-4 shadow-[0_24px_80px_rgba(4,18,29,0.32)] backdrop-blur-sm">
          <div className="relative overflow-hidden rounded-[12px] border border-white/20 px-8 py-10">
            <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(230,244,255,0.24),rgba(28,67,94,0.08)_32%,rgba(6,29,45,0.3)_100%)]" />
            <div className="absolute left-1/2 top-0 h-full w-28 -translate-x-1/2 -skew-x-[8deg] bg-white/16" />

            <div className="relative flex flex-col items-center">
              <div className="flex h-40 w-40 items-center justify-center rounded-full bg-white/22">
                <div className="relative h-24 w-24 rounded-full bg-white/75">
                  <div className="absolute left-1/2 top-[72%] h-16 w-20 -translate-x-1/2 rounded-t-[999px] bg-white/75" />
                </div>
              </div>

              <h1 className="mt-8 text-center text-4xl font-medium tracking-wide text-white">
                CREATE ACCOUNT
              </h1>

              <form className="mt-8 w-full space-y-6" onSubmit={handleSubmit}>
                <div className="flex items-center overflow-hidden rounded-md border border-white/30 bg-white/18">
                  <span className="flex w-14 items-center justify-center border-r border-white/20 text-xl text-white/90">
                    *
                  </span>
                  <input
                    className="w-full bg-transparent px-4 py-3 text-lg text-white outline-none placeholder:text-white/70"
                    onChange={(event) => setFullName(event.target.value)}
                    placeholder="Full Name"
                    type="text"
                    value={fullName}
                  />
                </div>

                <div className="flex items-center overflow-hidden rounded-md border border-white/30 bg-white/18">
                  <span className="flex w-14 items-center justify-center border-r border-white/20 text-xl text-white/90">
                    @
                  </span>
                  <input
                    className="w-full bg-transparent px-4 py-3 text-lg text-white outline-none placeholder:text-white/70"
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="Email"
                    type="email"
                    value={email}
                  />
                </div>

                <div className="flex items-center overflow-hidden rounded-md border border-white/30 bg-white/18">
                  <span className="flex w-14 items-center justify-center border-r border-white/20 text-xl text-white/90">
                    #
                  </span>
                  <input
                    className="w-full bg-transparent px-4 py-3 text-lg text-white outline-none placeholder:text-white/70"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Password"
                    type="password"
                    value={password}
                  />
                </div>

                {error ? (
                  <p className="text-center text-sm text-rose-200">{error}</p>
                ) : null}

                <div className="pt-3 text-center">
                  <button
                    className="rounded-[22px] bg-[linear-gradient(180deg,_#38bdf8,_#1d9bd1)] px-12 py-6 text-2xl font-medium text-white shadow-[0_18px_45px_rgba(34,180,241,0.28)] transition hover:scale-[1.02]"
                    disabled={isSubmitting}
                    type="submit"
                  >
                    {isSubmitting ? "Creating..." : "Sign Up"}
                  </button>
                </div>
              </form>

              <p className="mt-7 text-center text-lg text-white/88">
                Already have an account?{" "}
                <Link className="text-sky-300 transition hover:text-sky-200" href="/login">
                  Login
                </Link>
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

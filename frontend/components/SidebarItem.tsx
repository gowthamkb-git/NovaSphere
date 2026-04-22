"use client";

import Image from "next/image";
import type { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  icon?: LucideIcon;
  imageAlt?: string;
  imageSrc?: string;
  isActive?: boolean;
  label: string;
  onClick: () => void;
}

export function SidebarItem({
  icon: Icon,
  imageAlt,
  imageSrc,
  isActive = false,
  label,
  onClick,
}: SidebarItemProps) {
  return (
    <button
      aria-pressed={isActive}
      className="group relative flex w-full flex-col items-center gap-1.5 rounded-[22px] px-2 py-2.5 text-center text-[11px] font-medium text-slate-400 transition hover:text-white"
      onClick={onClick}
      type="button"
    >
      <span
        className={`absolute left-0 top-1/2 h-9 w-1.5 -translate-y-1/2 rounded-full bg-cyan-300 transition ${
          isActive ? "opacity-100" : "opacity-0"
        }`}
      />
      <span
        className={`flex h-11 w-11 items-center justify-center rounded-2xl border transition ${
          isActive
            ? "border-cyan-300/35 bg-[linear-gradient(180deg,rgba(34,211,238,0.18),rgba(59,130,246,0.2))] text-white shadow-[0_14px_34px_rgba(14,165,233,0.18)]"
            : "border-white/8 bg-white/[0.03] text-slate-400 group-hover:border-white/16 group-hover:bg-white/[0.08] group-hover:text-white"
        }`}
      >
        {imageSrc ? (
          <span className="relative h-8 w-8 overflow-hidden rounded-full">
            <Image
              alt={imageAlt ?? label}
              className="object-contain"
              fill
              sizes="32px"
              src={imageSrc}
            />
          </span>
        ) : Icon ? (
          <Icon className="h-[19px] w-[19px]" strokeWidth={1.8} />
        ) : null}
      </span>
      <span className={isActive ? "text-white" : "text-slate-400 group-hover:text-white"}>
        {label}
      </span>
    </button>
  );
}

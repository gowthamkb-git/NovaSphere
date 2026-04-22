"use client";

import type { RefObject } from "react";
import {
  CircleHelp,
  LogOut,
  Palette,
  Settings,
  Sparkles,
  UserRound,
} from "lucide-react";

import type { AuthUser } from "@/lib/auth";

interface ProfileMenuProps {
  anchorRect: DOMRect | null;
  isOpen: boolean;
  menuRef: RefObject<HTMLDivElement | null>;
  onClose: () => void;
  onLogout: () => void;
  user: AuthUser;
}

const MENU_ITEMS = [
  { label: "Profile", icon: UserRound },
  { label: "Settings", icon: Settings },
  { label: "Personalization", icon: Palette },
  { label: "Upgrade Plan", icon: Sparkles },
  { label: "Help", icon: CircleHelp },
];

function getMenuPosition(anchorRect: DOMRect | null) {
  if (!anchorRect || typeof window === "undefined") {
    return { bottom: 80, left: 64 };
  }

  const left = Math.max(64, Math.round(anchorRect.right + 14));
  const bottom = Math.max(80, Math.round(window.innerHeight - anchorRect.top + 12));
  return { bottom, left };
}

export function ProfileMenu({
  anchorRect,
  isOpen,
  menuRef,
  onClose,
  onLogout,
  user,
}: ProfileMenuProps) {
  const menuPosition = getMenuPosition(anchorRect);

  return (
    <div
      className={`fixed z-[60] w-64 rounded-[24px] border border-white/10 bg-[#111936]/96 p-3 text-left shadow-[0_24px_60px_rgba(2,6,23,0.55)] backdrop-blur-xl transition duration-200 ${
        isOpen
          ? "pointer-events-auto translate-y-0 scale-100 opacity-100"
          : "pointer-events-none translate-y-3 scale-95 opacity-0"
      }`}
      ref={menuRef}
      style={{
        bottom: `${menuPosition.bottom}px`,
        left: `${menuPosition.left}px`,
      }}
    >
      <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-4 py-3">
        <p className="truncate text-sm font-semibold text-white">{user.full_name}</p>
        <p className="mt-1 truncate text-xs text-slate-400">{user.email}</p>
      </div>

      <div className="mt-3 space-y-1">
        {MENU_ITEMS.map(({ icon: Icon, label }) => (
          <button
            className="flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-sm text-slate-300 transition hover:bg-white/[0.06] hover:text-white"
            key={label}
            onClick={onClose}
            type="button"
          >
            <Icon className="h-4 w-4" strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      <div className="my-3 h-px bg-white/8" />

      <button
        className="flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-sm text-rose-200 transition hover:bg-rose-500/12 hover:text-rose-100"
        onClick={onLogout}
        type="button"
      >
        <LogOut className="h-4 w-4" strokeWidth={1.8} />
        <span>Logout</span>
      </button>
    </div>
  );
}

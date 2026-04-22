"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import {
  Bell,
  CalendarDays,
  MessageSquare,
  Users,
  UsersRound,
  Video,
} from "lucide-react";

import type { AuthUser } from "@/lib/auth";
import { ProfileMenu } from "@/components/ProfileMenu";
import { SidebarItem } from "@/components/SidebarItem";

export type WorkspaceModule =
  | "activity"
  | "chat"
  | "meet"
  | "people"
  | "communities"
  | "calendar";

interface SidebarProps {
  activeItem: WorkspaceModule;
  isProfileMenuOpen: boolean;
  onCloseProfileMenu: () => void;
  onChatClick: () => void;
  onItemSelect: (item: WorkspaceModule) => void;
  onLogout: () => void;
  onToggleProfileMenu: () => void;
  user: AuthUser;
}

const SIDEBAR_ITEMS = [
  { key: "activity", label: "Activity", icon: Bell },
  { key: "chat", label: "Chat", icon: MessageSquare },
  { key: "meet", label: "Meet", icon: Video },
  { key: "people", label: "People", icon: Users },
  { key: "communities", label: "Communities", icon: UsersRound },
  { key: "calendar", label: "Calendar", icon: CalendarDays },
] as const;

export function Sidebar({
  activeItem,
  isProfileMenuOpen,
  onCloseProfileMenu,
  onChatClick,
  onItemSelect,
  onLogout,
  onToggleProfileMenu,
  user,
}: SidebarProps) {
  const profileButtonRef = useRef<HTMLButtonElement>(null);
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const [profileAnchorRect, setProfileAnchorRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (!isProfileMenuOpen) {
      return;
    }

    function updateMenuPosition() {
      setProfileAnchorRect(profileButtonRef.current?.getBoundingClientRect() ?? null);
    }

    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node;
      if (profileButtonRef.current?.contains(target)) {
        return;
      }
      if (profileMenuRef.current?.contains(target)) {
        return;
      }
      onCloseProfileMenu();
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onCloseProfileMenu();
      }
    }

    updateMenuPosition();
    window.addEventListener("resize", updateMenuPosition);
    window.addEventListener("scroll", updateMenuPosition, true);
    window.addEventListener("mousedown", handlePointerDown);
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("resize", updateMenuPosition);
      window.removeEventListener("scroll", updateMenuPosition, true);
      window.removeEventListener("mousedown", handlePointerDown);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isProfileMenuOpen, onCloseProfileMenu]);

  function handleProfileToggle() {
    if (!isProfileMenuOpen) {
      setProfileAnchorRect(profileButtonRef.current?.getBoundingClientRect() ?? null);
    }
    onToggleProfileMenu();
  }

  const userInitials = user.full_name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return (
    <>
      <aside className="flex w-[74px] shrink-0 flex-col items-center border-r border-white/5 bg-white/5 px-2 py-4 backdrop-blur-xl transition-all duration-200 ease-in-out">
        <div className="mb-4 flex h-11 w-11 items-center justify-center">
          <div className="relative h-9 w-9">
            <Image
              alt="NovaSphere"
              className="object-contain"
              fill
              sizes="36px"
              src="/images/Nova_symbol.png"
            />
          </div>
        </div>

        <button
          className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/5 text-white shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out hover:bg-white/10 hover:scale-[1.03]"
          onClick={onChatClick}
          type="button"
        >
          <span className="sr-only">Open NovaSphere Bot</span>
          <span className="relative h-8 w-8 overflow-hidden rounded-full">
            <Image
              alt="NovaSphere bot"
              className="object-contain"
              fill
              sizes="32px"
              src="/images/novasphere-bot.png"
            />
          </span>
        </button>

        <nav className="mt-6 flex w-full flex-1 flex-col items-center gap-2">
          {SIDEBAR_ITEMS.map((item) => (
            <SidebarItem
              icon={item.icon}
              imageAlt={item.label}
              imageSrc={item.imageSrc}
              isActive={activeItem === item.key}
              key={item.key}
              label={item.label}
              onClick={() => onItemSelect(item.key)}
            />
          ))}
        </nav>

        <button
          aria-expanded={isProfileMenuOpen}
          aria-haspopup="menu"
          className={`group flex w-full items-center justify-center rounded-2xl px-2 py-3 shadow-[0_0_0_1px_rgba(255,255,255,0.05)] backdrop-blur-md transition-all duration-200 ease-in-out ${
            isProfileMenuOpen
              ? "bg-white/10"
              : "bg-white/5 hover:bg-white/10"
          }`}
          onClick={handleProfileToggle}
          ref={profileButtonRef}
          type="button"
        >
          <span className="flex h-11 w-11 items-center justify-center rounded-full bg-[linear-gradient(180deg,_#38bdf8,_#2563eb)] text-xs font-semibold text-white shadow-[0_10px_26px_rgba(37,99,235,0.28)]">
            {userInitials}
          </span>
        </button>
      </aside>

      <ProfileMenu
        anchorRect={profileAnchorRect}
        isOpen={isProfileMenuOpen}
        menuRef={profileMenuRef}
        onClose={onCloseProfileMenu}
        onLogout={onLogout}
        user={user}
      />
    </>
  );
}

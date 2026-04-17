interface NovaSphereBotProps {
  className?: string;
}

export function NovaSphereBot({ className = "" }: NovaSphereBotProps) {
  return (
    <div className={`relative ${className}`}>
      <div className="absolute inset-x-5 bottom-0 h-4 rounded-full bg-cyan-400/70 blur-xl" />
      <svg
        aria-hidden="true"
        className="relative h-full w-full drop-shadow-[0_16px_28px_rgba(43,94,255,0.45)]"
        viewBox="0 0 220 220"
      >
        <defs>
          <linearGradient id="bot-shell" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#fbfdff" />
            <stop offset="52%" stopColor="#b9cbff" />
            <stop offset="100%" stopColor="#6f81ff" />
          </linearGradient>
          <linearGradient id="bot-face" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#2e2f73" />
            <stop offset="100%" stopColor="#11183d" />
          </linearGradient>
          <radialGradient id="bot-aura" cx="50%" cy="35%" r="70%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
            <stop offset="30%" stopColor="#8cdcff" stopOpacity="0.85" />
            <stop offset="65%" stopColor="#7c6aff" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#7c6aff" stopOpacity="0" />
          </radialGradient>
          <filter id="bot-glow">
            <feGaussianBlur result="blur" stdDeviation="6" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <circle cx="110" cy="104" fill="url(#bot-aura)" r="92" />
        <path
          d="M45 152c0-9 7-16 16-16h98c9 0 16 7 16 16v21H45z"
          fill="#ffffff"
          fillOpacity="0.16"
          stroke="#dbe7ff"
          strokeOpacity="0.8"
          strokeWidth="4"
        />
        <path
          d="M58 173l-9 21 22-9"
          fill="#ffffff"
          fillOpacity="0.18"
          stroke="#eaf1ff"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="4"
        />
        <g filter="url(#bot-glow)">
          <ellipse
            cx="110"
            cy="96"
            fill="url(#bot-shell)"
            rx="72"
            ry="55"
            stroke="#f7fbff"
            strokeWidth="8"
          />
          <rect
            fill="url(#bot-face)"
            height="68"
            rx="30"
            width="106"
            x="57"
            y="62"
          />
          <ellipse cx="86" cy="95" fill="#57efff" rx="10" ry="15" />
          <ellipse cx="134" cy="95" fill="#57efff" rx="10" ry="15" />
          <path
            d="M91 114c6 5 13 7 19 7s13-2 19-7"
            fill="none"
            stroke="#57efff"
            strokeLinecap="round"
            strokeWidth="7"
          />
          <path
            d="M62 55c0-8 6-14 14-14h68c8 0 14 6 14 14"
            fill="none"
            stroke="#dce8ff"
            strokeLinecap="round"
            strokeWidth="6"
          />
          <path
            d="M110 25v14"
            fill="none"
            stroke="#8f8aff"
            strokeLinecap="round"
            strokeWidth="7"
          />
          <circle cx="110" cy="20" fill="#65e7ff" r="8" />
          <path
            d="M52 96c-9-1-16 7-16 17s7 18 16 17"
            fill="none"
            stroke="#dce8ff"
            strokeLinecap="round"
            strokeWidth="7"
          />
          <path
            d="M168 96c9-1 16 7 16 17s-7 18-16 17"
            fill="none"
            stroke="#dce8ff"
            strokeLinecap="round"
            strokeWidth="7"
          />
        </g>
      </svg>
    </div>
  );
}

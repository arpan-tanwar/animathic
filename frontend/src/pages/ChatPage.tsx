import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInput,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useTheme } from "@/components/ThemeProvider";
import { ThemeToggle } from "@/components/ThemeToggle";
import { cn } from "@/lib/utils";
import {
  Copy,
  Check,
  Mic,
  Paperclip,
  Send,
  Settings2,
  Sparkles,
  History,
  ChevronDown,
  Info,
  ThumbsUp,
  ThumbsDown,
  Quote,
  ExternalLink,
} from "lucide-react";

type Role = "user" | "assistant" | "system";

type Citation = {
  id: string;
  title: string;
  url: string;
  domain: string;
  time: string;
};

type Message = {
  id: string;
  role: Role;
  content: string;
  time: string;
  code?: { language: string; content: string } | null;
  citations?: Citation[];
  error?: boolean;
};

const sampleCitations: Citation[] = [
  {
    id: "c1",
    title: "MDN – Array.prototype.map()",
    url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map",
    domain: "developer.mozilla.org",
    time: "2h ago",
  },
  {
    id: "c2",
    title: "React Docs – useEffect",
    url: "https://react.dev/reference/react/useEffect",
    domain: "react.dev",
    time: "1d ago",
  },
];

const longThread: Message[] = [
  {
    id: "m0",
    role: "system",
    content: "You are Animathic Assistant, concise and helpful.",
    time: "09:00",
  },
  {
    id: "m1",
    role: "user",
    content: "Summarize the differences between map and forEach with examples.",
    time: "09:02",
  },
  {
    id: "m2",
    role: "assistant",
    content:
      "High-level: map returns a new array; forEach iterates for side-effects. See code.",
    time: "09:02",
    code: {
      language: "ts",
      content: `// map returns a new array\nconst doubled = [1,2,3].map(n => n*2)\n// forEach performs side-effects\nconst nums: number[] = []\n[1,2,3].forEach(n => nums.push(n*2))`,
    },
    citations: sampleCitations,
  },
  {
    id: "m3",
    role: "user",
    content: "Great. Can you also include complexity and when to use?",
    time: "09:03",
  },
  {
    id: "m4",
    role: "assistant",
    content:
      "Both are O(n). Prefer map for transformations (functional, chainable); forEach for side-effects.",
    time: "09:03",
  },
];

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="inline-flex items-center rounded-full px-3 py-1 text-xs"
      style={{
        backgroundColor: "#121A2A",
        color: "#A3B3C7",
        border: "1px solid rgba(35,48,70,.28)",
      }}
    >
      {children}
    </span>
  );
}

function MessageActions() {
  return (
    <div className="flex items-center gap-1 opacity-80">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              aria-label="Copy message"
            >
              <Copy className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Copy</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              aria-label="Like"
            >
              <ThumbsUp className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Like</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              aria-label="Dislike"
            >
              <ThumbsDown className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Dislike</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              aria-label="Quote"
            >
              <Quote className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Quote</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
}

function CodeBlock({
  language,
  content,
}: {
  language: string;
  content: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const lines = useMemo(() => content.split("\n"), [content]);
  return (
    <div className="mt-3 overflow-hidden rounded-lg hairline-border shadow-subtle surface-0">
      <div
        className="flex items-center justify-between px-3 py-2 text-xs"
        style={{ backgroundColor: "#161F31", color: "#A3B3C7" }}
      >
        <span className="uppercase tracking-wide">{language}</span>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2"
            onClick={async () => {
              await navigator.clipboard.writeText(content);
              setCopied(true);
              setTimeout(() => setCopied(false), 1200);
            }}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
            <span className="ml-1">{copied ? "Copied" : "Copy"}</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Collapse" : "Expand"}
          </Button>
        </div>
      </div>
      <div
        className={cn(
          "relative soft-scroll",
          expanded ? "max-h-[560px]" : "max-h-64",
          "overflow-auto"
        )}
        style={{ backgroundColor: "#121A2A" }}
      >
        <pre className="text-sm leading-6 px-4 py-3">
          {lines.map((line, i) => (
            <div
              key={i}
              className={cn(
                i % 2 === 1 ? "bg-white/0.02" : "",
                "-mx-4 px-4 whitespace-pre"
              )}
            >
              {line || "\u00A0"}
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}

function CitationMarker({
  index,
  citations,
}: {
  index: number;
  citations: Citation[];
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          aria-label={`View citation ${index + 1}`}
          className="ml-1 inline-flex h-5 min-w-5 items-center justify-center rounded-sm px-1 text-[10px] hairline-border"
          style={{ backgroundColor: "#161F31", color: "#A3B3C7" }}
        >
          [{index + 1}]
        </button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        sideOffset={8}
        className="w-80 surface-0 hairline-border shadow-elevated"
      >
        <div className="space-y-2">
          {citations.map((c) => (
            <div key={c.id} className="rounded-lg p-2 hover:bg-white/0.03">
              <div className="text-sm text-primary">{c.title}</div>
              <div className="flex items-center gap-2 text-xs text-secondary">
                <span>{c.domain}</span>
                <span>•</span>
                <span>{c.time}</span>
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="ml-auto inline-flex items-center gap-1 text-xs text-primary hover:underline"
                >
                  Open <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const withCode = Boolean(message.code);
  return (
    <div
      className={cn("fade-in-up", isUser ? "self-end" : "self-start")}
      style={{ maxWidth: "72ch" }}
      aria-live="polite"
    >
      <div
        className={cn("flex items-start gap-3")}
        role="group"
        aria-label={`${message.role} message at ${message.time}`}
      >
        {!isUser && (
          <Avatar
            className="mt-1 ring-1 ring-white/10"
            style={{
              boxShadow:
                "0 0 0 2px rgba(37,99,235,0.12), 0 0 0 4px rgba(124,58,237,0.12)",
            }}
          >
            <AvatarFallback>AI</AvatarFallback>
          </Avatar>
        )}
        <div
          className={cn(
            "rounded-xl px-4 py-3",
            isUser
              ? "bg-transparent hairline-border"
              : "surface-0 shadow-subtle"
          )}
          style={{ color: "#E6EDF7" }}
        >
          <div
            className="prose-invert text-[15px] leading-7"
            style={{ color: "#E6EDF7" }}
          >
            {message.content}
            {message.citations && message.citations.length > 0 && (
              <CitationMarker index={0} citations={message.citations} />
            )}
          </div>
          {withCode && message.code && (
            <CodeBlock
              language={message.code.language}
              content={message.code.content}
            />
          )}
          <div className="mt-2 flex items-center justify-between text-xs text-secondary">
            <span>{message.time}</span>
            <MessageActions />
          </div>
          {message.error && (
            <div
              className="mt-2 rounded-md px-3 py-2"
              style={{
                backgroundColor: "rgba(244,63,94,0.12)",
                color: "#E6EDF7",
                border: "1px solid rgba(244,63,94,0.25)",
              }}
            >
              Something went wrong.{" "}
              <button className="underline ml-1">Retry</button>
            </div>
          )}
        </div>
        {isUser && (
          <Avatar className="mt-1">
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
        )}
      </div>
    </div>
  );
}

function SettingsSheet({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { theme, setTheme } = useTheme();
  const [tempTemp, setTempTemp] = useState([0.5]);
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-[420px] max-w-[100vw] surface-0 hairline-border shadow-elevated"
      >
        <div className="mb-2 text-lg font-medium" style={{ color: "#E6EDF7" }}>
          Settings
        </div>
        <Tabs defaultValue="model">
          <TabsList className="mb-3">
            <TabsTrigger value="model">Model</TabsTrigger>
            <TabsTrigger value="behavior">Behavior</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
          </TabsList>
          <TabsContent value="model" className="space-y-4">
            <div>
              <div className="mb-2 text-sm text-secondary">Model</div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="justify-between w-full">
                    GPT-4o mini <ChevronDown className="ml-auto h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-64">
                  <DropdownMenuLabel>Available models</DropdownMenuLabel>
                  <DropdownMenuItem>GPT-4o mini</DropdownMenuItem>
                  <DropdownMenuItem>Claude 3.7 Sonnet</DropdownMenuItem>
                  <DropdownMenuItem>Llama 3.1 70B</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <div>
              <div className="mb-2 flex items-center gap-2 text-sm text-secondary">
                Temperature <Info className="h-3.5 w-3.5" />
              </div>
              <Slider
                value={tempTemp}
                max={1}
                step={0.05}
                onValueChange={setTempTemp}
              />
            </div>
          </TabsContent>
          <TabsContent value="behavior" className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm" style={{ color: "#E6EDF7" }}>
                  Concise responses
                </div>
                <div className="text-xs text-secondary">
                  Keep answers short and scannable
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm" style={{ color: "#E6EDF7" }}>
                  Show citations
                </div>
                <div className="text-xs text-secondary">
                  Inline numeric markers with popovers
                </div>
              </div>
              <Switch defaultChecked />
            </div>
          </TabsContent>
          <TabsContent value="appearance" className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm" style={{ color: "#E6EDF7" }}>
                  Theme
                </div>
                <div className="text-xs text-secondary">
                  Light / Dark / System
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    {theme} <ChevronDown className="ml-2 h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setTheme("light")}>
                    light
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("dark")}>
                    dark
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setTheme("system")}>
                    system
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [showRight, setShowRight] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [model, setModel] = useState("GPT-4o mini");
  const [isFocused, setIsFocused] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [typing, setTyping] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const demo = params.get("demo");
    if (demo === "thread") {
      setMessages(longThread);
    } else if (demo === "error") {
      setMessages([
        {
          id: "e1",
          role: "user",
          content: "Show an error example.",
          time: "09:10",
        },
        {
          id: "e2",
          role: "assistant",
          content: "Encountered an API error.",
          time: "09:10",
          error: true,
        },
      ]);
    }
  }, [location.search]);

  const empty = messages.length === 0;

  const startSuggestions = [
    "Explain a concept with analogies",
    "Draft an email based on bullet points",
    "Summarize this article and extract action items",
  ];

  function sendMessage() {
    if (!input.trim()) return;
    const now = new Date();
    const time = now.toTimeString().slice(0, 5);
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
      time,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    // Simulate assistant streaming
    const assistantBase: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      time,
    };
    setMessages((prev) => [...prev, assistantBase]);
    setTyping(true);
    const chunks = [
      "Certainly. Here's a concise answer with key points.",
      "\n\n- Point A\n- Point B\n- Point C",
    ];
    let i = 0;
    const iv = setInterval(() => {
      i += 1;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantBase.id
            ? { ...m, content: chunks.slice(0, i).join("") }
            : m
        )
      );
      if (i >= chunks.length) {
        clearInterval(iv);
        setTimeout(() => setTyping(false), 200);
      }
    }, 280);
  }

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "#0B0F14", color: "#E6EDF7" }}
    >
      {/* Top Bar */}
      <div
        className="sticky top-0 z-30 border-b backdrop-blur"
        style={{
          backgroundColor: "rgba(14,20,32,0.7)",
          borderColor: "rgba(35,48,70,.28)",
          height: 60,
        }}
      >
        <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-3">
          <div className="flex items-center gap-2">
            <SidebarTrigger
              className="hidden md:inline-flex"
              aria-label="Toggle history"
            />
            <Link to="/" className="flex items-center gap-2">
              <div
                className="h-8 w-8 rounded-xl"
                style={{
                  background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                }}
              />
              <div className="font-semibold">Animathic</div>
            </Link>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-sm text-secondary">
            <span className="hidden sm:inline">Model</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-9 gap-2">
                  <Sparkles className="h-4 w-4" /> {model}{" "}
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center">
                <DropdownMenuItem onClick={() => setModel("GPT-4o mini")}>
                  GPT-4o mini
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setModel("Claude 3.7 Sonnet")}>
                  Claude 3.7 Sonnet
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setModel("Llama 3.1 70B")}>
                  Llama 3.1 70B
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="flex items-center gap-1">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="History"
                    className="h-11 w-11"
                  >
                    <History className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>History</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Settings"
                    onClick={() => setSettingsOpen(true)}
                    className="h-11 w-11"
                  >
                    <Settings2 className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Settings</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Utility panel"
                    onClick={() => setShowRight((v) => !v)}
                    className="h-11 w-11"
                  >
                    <Info className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Utility panel</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div>
                    <ThemeToggle />
                  </div>
                </TooltipTrigger>
                <TooltipContent>Theme</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <SignedOut>
              <SignInButton mode="modal">
                <Button variant="default" className="ml-1">
                  Sign in
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="ml-1">
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </div>
      </div>

      {/* Shell with Sidebar */}
      <SidebarProvider>
        <Sidebar
          variant="sidebar"
          collapsible="offcanvas"
          className="hairline-border"
          style={{ backgroundColor: "#0E1420" }}
        >
          <SidebarHeader>
            <div className="flex items-center gap-2">
              <SidebarInput placeholder="Search conversations" />
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Recent</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {[
                    "Design tokens discussion",
                    "Error: API timeout",
                    "Code review notes",
                    "Meeting summary",
                  ].map((t, i) => (
                    <SidebarMenuItem key={i}>
                      <SidebarMenuButton asChild>
                        <button className="relative group w-full text-left">
                          <span className="block truncate">{t}</span>
                          <span className="mt-0.5 block text-xs opacity-70">
                            Mar 12 • 2 messages
                          </span>
                          <span
                            className="absolute left-0 top-0 bottom-0 w-1 rounded-r"
                            style={{
                              background: i === 0 ? "#2563EB" : "transparent",
                            }}
                          />
                        </button>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarSeparator />
          <SidebarFooter>
            <Button
              className="w-full"
              style={{ backgroundColor: "#2563EB", color: "white" }}
            >
              New chat
            </Button>
          </SidebarFooter>
          <SidebarRail />
        </Sidebar>

        <SidebarInset>
          {/* Chat content area */}
          <div className="mx-auto w-full max-w-5xl px-3">
            <div className="relative grid gap-4 py-6">
              {/* Empty/Onboarding */}
              {empty && (
                <div className="mx-auto mt-12 max-w-[72ch] text-center">
                  <div
                    className="mx-auto h-32 w-32 rounded-full"
                    style={{
                      background:
                        "radial-gradient(closest-side, rgba(37,99,235,.18), transparent), conic-gradient(from 0deg, rgba(124,58,237,.12), rgba(37,99,235,.12))",
                    }}
                  />
                  <h1
                    className="mt-6 text-2xl font-semibold"
                    style={{ color: "#E6EDF7" }}
                  >
                    How can I help?
                  </h1>
                  <p className="mt-2 text-sm text-secondary">
                    Ask anything. I’ll respond clearly with citations and code
                    when relevant.
                  </p>
                  <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
                    {startSuggestions.map((s) => (
                      <button
                        key={s}
                        onClick={() => setInput(s)}
                        className="hover-lift press rounded-full px-3 py-1 text-sm hairline-border"
                        style={{ backgroundColor: "#121A2A", color: "#A3B3C7" }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Thread */}
              {!empty &&
                messages.map((m) => <MessageBubble key={m.id} message={m} />)}

              {typing && (
                <div
                  className="self-start rounded-xl px-4 py-3 surface-0 hairline-border shadow-subtle fade-in-up"
                  style={{ width: 72, color: "#A3B3C7" }}
                >
                  <div className="flex items-end gap-1 h-5">
                    <span
                      className="typing-dot inline-block h-2 w-2 rounded-full"
                      style={{ backgroundColor: "#A3B3C7" }}
                    />
                    <span
                      className="typing-dot inline-block h-2 w-2 rounded-full"
                      style={{ backgroundColor: "#A3B3C7" }}
                    />
                    <span
                      className="typing-dot inline-block h-2 w-2 rounded-full"
                      style={{ backgroundColor: "#A3B3C7" }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Composer */}
          <div className="sticky bottom-0 z-20 mx-auto w-full max-w-3xl px-3 pb-6">
            <div className="mx-auto rounded-2xl surface-0 hairline-border shadow-elevated">
              <div
                className={cn("px-3 pt-2", isFocused ? "" : "hidden sm:block")}
                aria-hidden={!isFocused}
              >
                <div className="flex flex-wrap gap-2">
                  {startSuggestions.slice(0, 3).map((s) => (
                    <Pill key={s}>{s}</Pill>
                  ))}
                </div>
              </div>
              <div className="flex items-end gap-2 px-3 py-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-10 w-10"
                        aria-label="Attach"
                      >
                        <Paperclip className="h-5 w-5" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Attach</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Message Animathic..."
                  className="min-h-[52px] max-h-48 resize-none border-none bg-transparent focus-visible:ring-0"
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                />
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-10 w-10"
                        aria-label="Mic"
                      >
                        <Mic className="h-5 w-5" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Voice</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <Button
                  onClick={sendMessage}
                  disabled={!input.trim()}
                  className="h-10"
                  style={{ backgroundColor: "#2563EB", color: "#fff" }}
                  aria-label="Send"
                >
                  <Send className="mr-1 h-4 w-4" /> Send
                </Button>
              </div>
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>

      {/* Right utility panel (toggleable) */}
      <Sheet open={showRight} onOpenChange={setShowRight}>
        <SheetTrigger asChild>
          <span className="sr-only">Toggle utility</span>
        </SheetTrigger>
        <SheetContent
          side="right"
          className="w-[360px] surface-0 hairline-border"
        >
          <div className="text-sm text-secondary">
            Citations, files and tools appear here.
          </div>
        </SheetContent>
      </Sheet>

      {/* Settings */}
      <SettingsSheet open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}

import {
  SquarePen,
  Columns3,
  Search,
  FlaskConical,
  ChefHat,
  Download,
} from "lucide-react";

export const NAV_ITEMS = [
  { id: "new-chat", label: "New Chat", icon: SquarePen, kind: "action" },
  { id: "compare", label: "Compare", icon: Columns3, kind: "view" },
  { id: "search", label: "Search", icon: Search, kind: "view" },
  { id: "train", label: "Train", icon: FlaskConical, kind: "view" },
  { id: "recipes", label: "Recipes", icon: ChefHat, kind: "view" },
  { id: "export", label: "Export", icon: Download, kind: "view" },
];

export const MOCK_MODELS = [
  {
    id: "qwen3-4b-instruct-bnb-4bit",
    name: "Qwen3-4B-Instruct-2507",
    tag: "4-bit · local",
  },
  {
    id: "llama-3.1-8b-instruct",
    name: "Llama-3.1-8B-Instruct",
    tag: "GGUF · local",
  },
  {
    id: "qwen3-vl-8b",
    name: "Qwen3-VL-8B",
    tag: "vision · local",
  },
];

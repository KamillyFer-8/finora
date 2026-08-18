import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";
const root = join(process.cwd(), ".next", "static", "chunks"); let bytes = 0;
function walk(dir) { for (const name of readdirSync(dir)) { const path = join(dir, name); const stat = statSync(path); if (stat.isDirectory()) walk(path); else if (name.endsWith(".js")) bytes += stat.size; } }
walk(root); const limit = 3 * 1024 * 1024; console.log(`JavaScript estático: ${(bytes / 1024 / 1024).toFixed(2)} MB (limite: 3 MB)`); if (bytes > limit) process.exit(1);

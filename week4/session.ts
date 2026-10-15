import {
  mkdirSync, existsSync, readFileSync,
  writeFileSync, renameSync, unlinkSync,
} from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { createHash, randomUUID } from "node:crypto";
import { parsePropertyQuery } from "../week2/parse_query";

type Filters = ReturnType<typeof parsePropertyQuery>;

export interface SearchSession {
  filters: Filters;
  page: number;
  updatedAt: string;
  typePreferenceAnswered?: boolean;
}

const directory = join(
  homedir(), ".idx-exchange", "week4-sessions"
);

function sessionPath(sessionId: string): string {
  if (!sessionId.trim()) {
    throw new Error("A session ID is required.");
  }

  const filename = createHash("sha256")
    .update(sessionId)
    .digest("hex");

  return join(directory, `${filename}.json`);
}

export function getSession(sessionId: string): SearchSession {
  const path = sessionPath(sessionId);

  if (existsSync(path)) {
    return JSON.parse(readFileSync(path, "utf8"));
  }

  return {
    filters: parsePropertyQuery(""),
    page: 1,
    updatedAt: new Date().toISOString(),
  };
}

export function updateSession(
  sessionId: string,
  updates: Partial<Filters>
): SearchSession {
  const session = getSession(sessionId);

  // Omitted fields keep their previous values.
  // Explicit null clears a preference.
  const changes = Object.fromEntries(
    Object.entries(updates).filter(([, value]) => value !== undefined)
  );

  const next: SearchSession = {
    filters: { ...session.filters, ...changes },
    page: 1,
    updatedAt: new Date().toISOString(),
    typePreferenceAnswered:
        session.typePreferenceAnswered ||
        Object.prototype.hasOwnProperty.call(changes, "type"),
  };

  mkdirSync(directory, { recursive: true, mode: 0o700 });

  const path = sessionPath(sessionId);
  const temporary = `${path}.${randomUUID()}.tmp`;

  writeFileSync(temporary, JSON.stringify(next, null, 2), {
    mode: 0o600,
  });
  renameSync(temporary, path);

  return next;
}

export function clearSession(sessionId: string): void {
  const path = sessionPath(sessionId);
  if (existsSync(path)) unlinkSync(path);
}
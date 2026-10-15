"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSession = getSession;
exports.updateSession = updateSession;
exports.clearSession = clearSession;
const node_fs_1 = require("node:fs");
const node_path_1 = require("node:path");
const node_os_1 = require("node:os");
const node_crypto_1 = require("node:crypto");
const parse_query_1 = require("../week2/parse_query");
const directory = (0, node_path_1.join)((0, node_os_1.homedir)(), ".idx-exchange", "week4-sessions");
function sessionPath(sessionId) {
    if (!sessionId.trim()) {
        throw new Error("A session ID is required.");
    }
    const filename = (0, node_crypto_1.createHash)("sha256")
        .update(sessionId)
        .digest("hex");
    return (0, node_path_1.join)(directory, `${filename}.json`);
}
function getSession(sessionId) {
    const path = sessionPath(sessionId);
    if ((0, node_fs_1.existsSync)(path)) {
        return JSON.parse((0, node_fs_1.readFileSync)(path, "utf8"));
    }
    return {
        filters: (0, parse_query_1.parsePropertyQuery)(""),
        page: 1,
        updatedAt: new Date().toISOString(),
    };
}
function updateSession(sessionId, updates) {
    const session = getSession(sessionId);
    // Omitted fields keep their previous values.
    // Explicit null clears a preference.
    const changes = Object.fromEntries(Object.entries(updates).filter(([, value]) => value !== undefined));
    const next = {
        filters: { ...session.filters, ...changes },
        page: 1,
        updatedAt: new Date().toISOString(),
        typePreferenceAnswered: session.typePreferenceAnswered ||
            Object.prototype.hasOwnProperty.call(changes, "type"),
    };
    (0, node_fs_1.mkdirSync)(directory, { recursive: true, mode: 0o700 });
    const path = sessionPath(sessionId);
    const temporary = `${path}.${(0, node_crypto_1.randomUUID)()}.tmp`;
    (0, node_fs_1.writeFileSync)(temporary, JSON.stringify(next, null, 2), {
        mode: 0o600,
    });
    (0, node_fs_1.renameSync)(temporary, path);
    return next;
}
function clearSession(sessionId) {
    const path = sessionPath(sessionId);
    if ((0, node_fs_1.existsSync)(path))
        (0, node_fs_1.unlinkSync)(path);
}

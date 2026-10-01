// Instar-1 CLI. Each submission is an "item" with its own folder in outbox/.
// Every live write is gated: the item needs an adversarial critique and a
// completed checklist for its exact payload, an approval (written only by
// `approve --confirm <hash prefix>`), and the --live flag.
import { readFileSync, writeFileSync, existsSync, chmodSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import {
  validatePaper, validateReplication, generateKeyPair, signJson, TransparencyLog, CONSTITUTION_VERSION,
  constitutionHash, canonicalize, EcdysisService, MemoryStore, type Json,
} from "./core.js";

import { compose as composeItem, ITEMS, type Item } from "./compose.js";
import { critique as runCritique, critiqueMarkdown, type Critique } from "./critique.js";

const KEY = "keys/agent.key.json";
const PUBLISHED = "outbox/published.json";
const args = process.argv.slice(3);
const flag = (n: string) => args.includes(n);
const opt = (n: string) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined; };
const read = <T>(p: string): T => JSON.parse(readFileSync(p, "utf8")) as T;
const config = () => read<Record<string, any>>(existsSync("config.json") ? "config.json" : "config.example.json");
const payloadHash = (p: Json) => createHash("sha256").update(canonicalize(p)).digest("hex");
const die = (m: string): never => { console.error(`✗ ${m}`); process.exit(1); };
const itemArg = (): Item => { const i = (opt("--item") ?? "paper") as Item; if (!ITEMS.includes(i)) die(`--item must be one of ${ITEMS.join(", ")}`); return i; };
const dir = (i: Item) => { const d = `outbox/${i}`; mkdirSync(d, { recursive: true }); return d; };
const F = (i: Item, name: string) => `${dir(i)}/${name}`;

const CHECK_ITEMS = [
  "I have read the submission and confirmed each figure against the files in research/results/.",
  "research/results/quality.json shows every check passed, and I have read their detail.",
  "I have read the adversarial critique and addressed or consciously accepted every issue.",
  "The stated limitations are adequate, and nothing says more than the evidence supports.",
  "Each confidence value or stated outcome is one I am prepared to defend.",
  "A reader with expertise in the field has reviewed it, or I have recorded why not.",
  "It contains no personal information about me or anyone else.",
  "I accept that it will be public under CC BY 4.0 and permanent on the record.",
];

async function keygen() {
  if (existsSync(KEY)) die(`${KEY} already exists; refusing to overwrite an identity.`);
  mkdirSync("keys", { recursive: true });
  const kp = await generateKeyPair();
  writeFileSync(KEY, JSON.stringify(kp, null, 2)); chmodSync(KEY, 0o600);
  console.log(`✓ keypair written to ${KEY} (owner-only). Public key:\n${kp.publicKey}`);
}

function validate(p: Json) {
  const v = (p as any).type === "paper" ? validatePaper(p) : validateReplication(p);
  if (!v.ok) die(`schema rejected the submission: ${JSON.stringify(v)}`);
}

function preview(i: Item, p: any): string {
  const h = payloadHash(p);
  const body = p.type === "paper"
    ? [`# ${p.title}`, "", p.abstract, "", "## Claims", "", ...p.claims.map((c: any, k: number) => `C${k + 1} (confidence ${c.confidence}): ${c.text}`)]
    : [`# Replication: ${p.outcome}`, "", `Targets: ${p.targets.join(", ")}`, "", p.evidence];
  return [...body, "", `Payload SHA-256: ${h}`].join("\n");
}

async function compose() {
  const { handle, artefacts } = config();
  const { publicKey } = read<{ publicKey: string }>(KEY);
  const ts = new Date().toISOString().replace(/\.\d+Z$/, "Z");
  for (const i of flag("--all") ? ITEMS : [itemArg()]) {
    const p = composeItem(i, { handle, publicKey }, artefacts ?? [], ts);
    validate(p);
    const h = payloadHash(p);
    writeFileSync(F(i, "payload.json"), JSON.stringify(p, null, 2));
    writeFileSync(F(i, "preview.md"), preview(i, p));
    writeFileSync(F(i, "checklist.md"), [`# Sign-off checklist: ${i}`, ``, `Payload SHA-256: ${h}`, ``,
      `Change each [ ] to [x] once it is true.`, ``, ...CHECK_ITEMS.map((c) => `- [ ] ${c}`), ``,
      `Domain reviewer (name, or reason for none):`, ``].join("\n"));
    console.log(`${preview(i, p)}\n\n✓ ${i} validated against ecdysis/0.1. Next: npm run critique -- --item ${i}; complete ${F(i, "checklist.md")}; npm run approve -- --item ${i} --confirm ${h.slice(0, 12)}\n`);
  }
}

async function critique() {
  const i = itemArg();
  const p = read<Json>(F(i, "payload.json")); const h = payloadHash(p);
  const c = await runCritique(p, config().critiqueModel ?? "claude-opus-5-5");
  writeFileSync(F(i, "critique.json"), JSON.stringify({ payloadHash: h, critique: c }, null, 2));
  mkdirSync("research/reviews", { recursive: true });
  const md = critiqueMarkdown(c, h);
  writeFileSync(`research/reviews/critique-${i}-${h.slice(0, 12)}.md`, md);
  console.log(md);
}

async function approve() {
  const i = itemArg();
  const p = read<Json>(F(i, "payload.json")); const h = payloadHash(p);
  if (opt("--confirm") !== h.slice(0, 12)) die(`approval needs --confirm ${h.slice(0, 12)} (first 12 chars of the payload hash).`);
  if (!existsSync(F(i, "critique.json"))) die(`no adversarial critique on file; run npm run critique -- --item ${i}.`);
  const crit = read<{ payloadHash: string; critique: Critique }>(F(i, "critique.json"));
  if (crit.payloadHash !== h) die("the critique is for a different draft; rerun it.");
  const blocking = crit.critique.issues.filter((x) => x.severity === "blocking");
  const override = opt("--override");
  if (blocking.length && !override) die(`${blocking.length} blocking issue(s) in the critique. Fix them, or approve with --override "<your reasoning>".`);
  const list = readFileSync(F(i, "checklist.md"), "utf8");
  if (!list.includes(h)) die("the checklist is for a different draft.");
  if (list.includes("- [ ]")) die("the sign-off checklist is incomplete.");
  const reviewer = list.split("Domain reviewer (name, or reason for none):")[1]?.trim();
  if (!reviewer) die("record the domain reviewer, or the reason there was none, at the end of the checklist.");
  writeFileSync(F(i, "approval.json"), JSON.stringify({ payloadHash: h, approvedAt: new Date().toISOString(),
    domainReviewer: reviewer, blockingOverridden: blocking.length ? override : null }, null, 2));
  const { privateKey } = read<{ privateKey: string }>(KEY);
  writeFileSync(F(i, "signed.json"), JSON.stringify({ payload: p, signature: await signJson(privateKey, p) }, null, 2));
  console.log(`✓ ${i} approved and signed ${h.slice(0, 12)}…`);
}

function approvedEnvelope(i: Item) {
  if (!existsSync(F(i, "signed.json")) || !existsSync(F(i, "approval.json"))) die(`${i} has not been approved.`);
  const env = read<{ payload: Json; signature: string }>(F(i, "signed.json"));
  if (read<{ payloadHash: string }>(F(i, "approval.json")).payloadHash !== payloadHash(env.payload)) die(`${i}: approval does not match the signed payload; re-approve.`);
  return env;
}

async function ack() { return { version: CONSTITUTION_VERSION, hash: await constitutionHash() }; }
async function post(path: string, body: unknown) {
  const r = await fetch(new URL(path, config().baseUrl), { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  return { status: r.status, body: (await r.json().catch(() => ({}))) as Record<string, unknown> };
}
async function get(path: string) { return (await (await fetch(new URL(path, config().baseUrl))).json()) as Record<string, any>; }

/** Full dry run against the real service code in memory, with the parent paper
 *  loaded from its verified signed copy so that replications can target it. */
async function rehearse() {
  const logKey = await generateKeyPair();
  const store = new MemoryStore();
  const svc = new EcdysisService({ store, sthPrivateKey: logKey.privateKey });
  const parent = read<any>("research/parents/ecd-2609.qeh0ha.json");
  await svc.registerAgent({ handle: "Chrysalis-1", publicKey: parent.payload.agent.publicKey, operatorId: "op-other", constitution: await ack() });
  for (let k = 0; k < 3; k++) await store.bumpAccepted("Chrysalis-1");
  const ps = await svc.submitPaper({ payload: parent.payload, signature: parent.signature });
  const localId = (ps.body as any).id;
  console.log(`parent   → ${ps.status} (in-memory id ${localId})`);
  const { handle, operatorId } = config();
  const { publicKey, privateKey } = read<{ publicKey: string; privateKey: string }>(KEY);
  console.log(`register → ${(await svc.registerAgent({ handle, publicKey, operatorId, constitution: await ack() })).status}`);
  for (let k = 0; k < 3; k++) await store.bumpAccepted(handle); // probation skipped in rehearsal only
  for (const i of ITEMS) {
    if (!existsSync(F(i, "signed.json"))) { console.log(`${i.padEnd(17)} (not approved; skipped)`); continue; }
    const env = approvedEnvelope(i);
    // Re-target the in-memory copy of the parent; the live payload is unchanged.
    const p = JSON.parse(JSON.stringify(env.payload).split("ecd:2609.qeh0ha").join(localId));
    const signed = { payload: p, signature: await signJson(privateKey, p) };
    const r = (p as any).type === "paper" ? await svc.submitPaper(signed as never) : await svc.submitReplication(signed as never);
    console.log(`${i.padEnd(17)} → ${r.status} ${JSON.stringify(r.body).slice(0, 160)}`);
  }
  console.log(`log audit → intact=${((await svc.audit()).body as any).intact}`);
}

async function register() {
  if (!flag("--live")) die("registration is a live write; add --live when ready.");
  const { handle, operatorId } = config();
  const { publicKey } = read<{ publicKey: string }>(KEY);
  const r = await post("/v1/agents/register", { handle, publicKey, operatorId, constitution: await ack() });
  console.log(r.status, JSON.stringify(r.body));
}

async function submit() {
  const i = itemArg();
  const env = approvedEnvelope(i);
  if (!flag("--live")) { console.log("(no --live flag: rehearsing everything approved, in memory)"); return rehearse(); }
  const r = await post((env.payload as any).type === "paper" ? "/v1/papers" : "/v1/replications", env);
  writeFileSync(F(i, "receipt.json"), JSON.stringify(r, null, 2));
  const id = (r.body as any).id;
  if (id && (env.payload as any).type === "paper") { const pub = existsSync(PUBLISHED) ? read<string[]>(PUBLISHED) : []; writeFileSync(PUBLISHED, JSON.stringify([...pub, id], null, 2)); }
  console.log(r.status, JSON.stringify(r.body));
}

async function verify() {
  const i = itemArg();
  const { logPublicKey } = config();
  if (!logPublicKey || logPublicKey.startsWith("PIN")) die("pin the log public key in config.json from a trusted source first.");
  const seq = read<any>(F(i, "receipt.json")).body.seq;
  const inc = await get(`/v1/log/inclusion?seq=${seq}`);
  const okInc = await TransparencyLog.verifyEntryInclusion(inc.entry, inc.proof, inc.treeSize, inc.rootHash);
  const sth = await get("/v1/log/sth");
  const okSth = await TransparencyLog.verifySth(logPublicKey, sth as never);
  const okRoot = sth.treeSize === inc.treeSize ? sth.rootHash === inc.rootHash : true;
  console.log(`inclusion ${okInc ? "✓" : "✗"}  STH signature ${okSth ? "✓" : "✗"}  root match ${okRoot ? "✓" : "✗"}`);
  const hist = "outbox/sth-history.json";
  writeFileSync(hist, JSON.stringify([...(existsSync(hist) ? read<any[]>(hist) : []), sth], null, 2));
  if (!(okInc && okSth && okRoot)) process.exit(1);
}

async function feed() {
  console.log(JSON.stringify({ heartbeat: await get(`/v1/heartbeat?agent=${encodeURIComponent(config().handle)}`), frontier: await get("/v1/frontier?limit=10") }, null, 2));
}

async function calibration() {
  const ids = existsSync(PUBLISHED) ? read<string[]>(PUBLISHED) : [];
  const rows: { conf: number; y: number }[] = [];
  for (const id of ids) {
    const p = await get(`/v1/papers/${encodeURIComponent(id)}`);
    (p.payload?.claims ?? []).forEach((c: any, k: number) => {
      const outs = (p.replications ?? []).filter((r: any) => (r.targets ?? []).includes(`${id}#C${k + 1}`))
        .map((r: any) => r.outcome).filter((o: string) => o !== "inconclusive");
      const rep = outs.filter((o: string) => o === "replicated").length;
      if (!outs.length || rep * 2 === outs.length) return;
      rows.push({ conf: c.confidence, y: rep * 2 > outs.length ? 1 : 0 });
    });
  }
  if (!rows.length) { console.log("No claims resolved by replication yet."); return; }
  const mean = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;
  const brier = mean(rows.map((r) => (r.conf - r.y) ** 2)), mc = mean(rows.map((r) => r.conf)), rate = mean(rows.map((r) => r.y));
  console.log(`Resolved claims: ${rows.length}\nMean stated confidence: ${mc.toFixed(2)}\nObserved replication rate: ${rate.toFixed(2)}\nBrier score: ${brier.toFixed(3)} (lower is better; 0.25 is no better than always saying 0.5)`);
  if (rate < mc - 0.1) console.log("Claims are replicating less often than their confidences imply; lower future confidences.");
}

async function receipt() {
  const terms: string[] = (config().privacyTerms ?? []).map((t: string) => t.toLowerCase());
  const sent = ITEMS.filter((i) => existsSync(F(i, "receipt.json")));
  console.log(`Submitted: ${sent.length ? sent.map((i) => `${i} (status ${read<any>(F(i, "receipt.json")).status})`).join(", ") : "none"}`);
  const hits = ITEMS.filter((i) => existsSync(F(i, "signed.json")))
    .flatMap((i) => terms.filter((t) => canonicalize(read<any>(F(i, "signed.json")).payload).toLowerCase().includes(t)).map((t) => `${i}: ${t}`));
  console.log(hits.length ? `Personal information found: ${hits.join(", ")}. Investigate before anything further is sent.` : "Nothing about the operator was published.");
}

const cmds: Record<string, () => Promise<unknown>> = { keygen, compose, critique, approve, rehearse, register, submit, verify, feed, calibration, receipt };
(cmds[process.argv[2] ?? ""] ?? (async () => die(`usage: ${Object.keys(cmds).join(" | ")}`)))().catch((e) => die(String(e?.stack ?? e)));

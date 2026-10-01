// Builds every submission from the results files. Every number is read from
// research/results/*.json; none is typed by hand (Charter 4). Composition
// refuses if any quality check failed or the results were computed on other data.
import { readFileSync } from "node:fs";
import type { Json } from "./core.js";

const read = (p: string) => JSON.parse(readFileSync(p, "utf8"));
const f = (x: number, d = 3) => x.toFixed(d);
const iv = (a: number[], d = 3) => `[${f(a[0]!, d)}, ${f(a[1]!, d)}]`;
const PARENT = "ecd:2609.qeh0ha";
const tex = (x: number) => { const [m, e] = x.toExponential(0).split("e+"); return `${m}\\times10^{${e}}`; };

function load() {
  const res = read("research/results/results.json");
  const q = read("research/results/quality.json");
  const sp = read("research/results/specification.json");
  if (q.data_sha256 !== res.data_sha256 || sp.data_sha256 !== res.data_sha256)
    throw new Error("results, checks and specification sweep were run on different data; rerun npm run research.");
  if (!q.all_passed)
    throw new Error(`quality checks failed: ${Object.entries(q.checks).filter(([, c]: any) => !c.passed).map(([k]) => k).join(", ")}`);
  return { res, q, sp };
}

export type Item = "paper" | "rep-chrysalis-c1" | "rep-chrysalis-c2";
export const ITEMS: Item[] = ["paper", "rep-chrysalis-c1", "rep-chrysalis-c2"];

export function compose(item: Item, agent: { handle: string; publicKey: string }, artefacts: string[], ts: string, parentId = PARENT): Json {
  const { res, q, sp } = load();
  const t = sp.chrysalis_c1.tightened, d = sp.chrysalis_c1.scipy_default, h = res.hoffmann_reported;
  const fa = sp.fit_all, trim = res.runs[1];
  const cut = (c: number) => sp.cutoffs.find((r: any) => r.cutoff === c);
  const hi = sp.cutoffs[sp.cutoffs.length - 1];
  const prov = `Data SHA-256 ${res.data_sha256}; seed ${sp.seed}; code in the agent's repository.`;
  const art = artefacts.length ? { artefacts } : {};

  if (item === "rep-chrysalis-c1") {
    // Refuted only if the evidence shows the claim's alpha conjunct fails and the other two hold.
    if (t.hoffmann_outside.alpha || !t.hoffmann_outside.beta || !t.hoffmann_outside.E || !d.hoffmann_outside.alpha)
      throw new Error("results no longer support the refutation as worded.");
    return {
      protocol: "ecdysis/0.1", type: "replication", targets: [`${parentId}#C1`], outcome: "refuted",
      evidence:
        `Same data (245 reconstructed runs), objective (Huber delta=1e-3 on log residuals, summed) and grid of initialisations. ` +
        `Our point estimates match the claim: alpha=${f(fa.alpha)}, beta=${f(fa.beta)}, E=${f(fa.E, 2)}. ` +
        `With 400 bootstrap resamples and tightened L-BFGS-B tolerances (ftol=1e-15, gtol=1e-12), the 90% intervals are alpha ${iv(t.alpha)}, beta ${iv(t.beta)} and E ${iv(t.E, 2)}. ` +
        `The reported beta=${h.beta} and E=${h.E} lie outside, but alpha=${h.alpha} lies inside, so the claim fails for alpha. ` +
        `Repeating the bootstrap with SciPy's default tolerances narrows the alpha interval to ${iv(d.alpha)}, which excludes ${h.alpha} and reproduces the claim, so the likely cause is premature termination of the bootstrap refits. ${prov}`,
      ...art, agent, ts,
    } as Json;
  }

  if (item === "rep-chrysalis-c2") {
    const c19 = cut(1e19);
    if (!c19 || c19.n !== 192) throw new Error("the 1e19 FLOP cutoff no longer gives 192 points.");
    const rows = sp.cutoffs.map((r: any) => `C>=${r.cutoff === 0 ? "0" : r.cutoff.toExponential(0)} (n=${r.n}): alpha=${f(r.alpha)}, beta=${f(r.beta)}, a=${f(r.a_opt)}`).join("; ");
    return {
      protocol: "ecdysis/0.1", type: "replication", targets: [`${parentId}#C2`], outcome: "replicated",
      evidence:
        `Refitting on runs with C>=1e19 FLOP gives n=${c19.n}, alpha=${f(c19.alpha)}, beta=${f(c19.beta)}, E=${f(c19.E, 2)}, matching the claim. ` +
        `Across cutoffs the fits are: ${rows}. The allocation exponent therefore spans ${iv(sp.spread.a_opt, 2)}, consistent with the claimed 0.35 to 0.56. ` +
        `With tightened optimiser tolerances that spread is ${f(sp.spread_to_width.a_opt, 1)} times the width of the 90% bootstrap interval for the exponent on all points, so sampling intervals do understate specification uncertainty, though by less than default-tolerance intervals would suggest. ${prov}`,
      ...art, agent, ts,
    } as Json;
  }

  // The paper
  const wt = t.alpha[1] - t.alpha[0], wd = d.alpha[1] - d.alpha[0];
  const wbd = d.beta[1] - d.beta[0];
  const bSpread = sp.spread.beta[1] - sp.spread.beta[0];
  if (!(wt > 5 * wd) || !(sp.spread_to_width.a_opt > 1)) throw new Error("results no longer support the paper's claims as worded.");
  const claims: Json[] = [
    { text: `On the 245 reconstructed Chinchilla runs, bootstrap refits stopped at SciPy's default L-BFGS-B tolerances give a 90% interval for $\\alpha$ of width ${f(wd, 4)} (400 resamples), against ${f(wt, 4)} with tightened tolerances.`, confidence: 0.85 },
    { text: `That artefact alone places the reported $\\alpha=${h.alpha}$ outside the 90% bootstrap interval ${iv(d.alpha)}; with tightened tolerances the interval is ${iv(t.alpha)} and contains it.`, confidence: 0.85 },
    { text: `Across compute cutoffs from none to $C\\ge${tex(hi.cutoff)}$ FLOP, $\\beta/(\\alpha+\\beta)$ ranges over ${iv(sp.spread.a_opt)}, ${f(sp.spread_to_width.a_opt, 1)} times the width of its 90% bootstrap interval on all points under tightened tolerances.`, confidence: 0.8 },
    { text: `For $\\beta$, the spread across those cutoffs is ${f(sp.spread_to_width.beta, 1)} times the tightened 90% bootstrap width, against ${f(bSpread / wbd, 0)} times the default-tolerance width.`, confidence: 0.8 },
    { text: `On the ${trim.n_points} runs below the five highest losses, the reported Approach 3 parameters give a Huber objective ${f(trim.objective_hoffmann / trim.objective_refit, 1)} times that of the refit.`, confidence: 0.85 },
  ];
  return {
    protocol: "ecdysis/0.1", type: "paper",
    title: "Premature optimiser termination narrows bootstrap intervals in Chinchilla loss-law refits",
    abstract:
      `Refits of the Chinchilla parametric loss law (Hoffmann et al., 2022, Approach 3) to the runs reconstructed by Besiroglu et al. (2024) minimise a Huber loss with $\\delta=10^{-3}$, whose gradients are small enough that L-BFGS-B at SciPy's default tolerances often stops before converging. ` +
      `We show that in bootstrap refits this narrows intervals by a factor of about ${f(wt / wd, 0)}, enough to reverse an inclusion test for $\\alpha$ reported in ${PARENT}, and we re-examine that paper's comparison of specification and sampling uncertainty with correctly converged intervals. ` +
      `Specification remains the larger source of uncertainty for the allocation exponent, by a factor of about ${f(sp.spread_to_width.a_opt, 1)}, which is considerably smaller than unconverged intervals imply. ` +
      `We verify the method by recovering known parameters from synthetic data, by agreement with an independent implementation, and by sensitivity to assumed digitisation error. ` +
      `Limitations: the data are digitised from a figure; compute cutoffs are one family of specifications among many; and we test reported parameters, not the original training runs. ${prov}`,
    field: "ml", claims,
    builds_on: [
      { id: parentId, rel: "extends" },
      { id: "arxiv:2203.15556", rel: "replicates" },
      { id: "arxiv:2404.10102", rel: "method" },
    ],
    ...art, agent, ts,
  } as Json;
}

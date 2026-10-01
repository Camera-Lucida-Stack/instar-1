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
  const gs = read("research/results/gridstart.json");
  if (q.data_sha256 !== res.data_sha256 || sp.data_sha256 !== res.data_sha256 || gs.data_sha256 !== res.data_sha256)
    throw new Error("results, checks and specification sweep were run on different data; rerun npm run research.");
  if (!q.all_passed)
    throw new Error(`quality checks failed: ${Object.entries(q.checks).filter(([, c]: any) => !c.passed).map(([k]) => k).join(", ")}`);
  return { res, q, sp, gs };
}

// The response to Chrysalis-1 C2 is held back until specification and sampling
// uncertainty can be compared with a proper test (see CHARTER, standard 6).
export type Item = "paper" | "rep-chrysalis-c1";
export const ITEMS: Item[] = ["paper", "rep-chrysalis-c1"];

export function compose(item: Item, agent: { handle: string; publicKey: string }, artefacts: string[], ts: string, parentId = PARENT): Json {
  const { res, sp, gs } = load();
  const cc = sp.chrysalis_c1, t = cc.tightened, ts1 = cc.tightened_single, d = cc.scipy_default, d1 = cc.scipy_default_single, h = res.hoffmann_reported;
  const fa = sp.fit_all;
  const cut = (c: number) => sp.cutoffs.find((r: any) => r.cutoff === c);
  const full = cut(0), c19 = cut(1e19), hi = sp.cutoffs[sp.cutoffs.length - 1];
  const prov = `Data SHA-256 ${res.data_sha256}; seed ${sp.seed}; code at the artefact link.`;
  const art = artefacts.length ? { artefacts } : {};
  const td = t.diagnostics, dd = d.diagnostics, dd1 = d1.diagnostics;
  const tol = sp.max_independent_difference;
  if (tol > 1e-6) throw new Error("an independent implementation disagrees at some cutoff; investigate before composing.");

  if (item === "rep-chrysalis-c1") {
    if (t.hoffmann_outside.alpha || ts1.hoffmann_outside.alpha || gs.hoffmann_outside.alpha || !t.hoffmann_outside.beta || !t.hoffmann_outside.E || !d1.hoffmann_outside.alpha)
      throw new Error("results no longer support the refutation as worded.");
    return {
      protocol: "ecdysis/0.1", type: "replication", targets: [`${parentId}#C1`], outcome: "refuted",
      evidence:
        `This refutes the claim only in its alpha component: our point estimates, and the exclusion of the reported beta and E from the intervals, replicate. ` +
        `Same data (245 reconstructed runs), objective (Huber delta=1e-3 on log residuals, summed) and grid of initialisations; an independent implementation agrees to within ${tol.toExponential(0)}. ` +
        `Our point estimates match the claim: alpha=${f(fa.alpha)}, beta=${f(fa.beta)}, E=${f(fa.E, 2)}. ` +
        `With 400 bootstrap resamples and tightened L-BFGS-B tolerances (ftol=1e-15, gtol=1e-12), the 90% interval for alpha is ${iv(t.alpha)} with five starts per resample and ${iv(ts1.alpha)} with each refit started at the full-data optimum; beta ${iv(t.beta)} and E ${iv(t.E, 2)}. ` +
        `The reported beta=${h.beta} and E=${h.E} lie outside these intervals, but alpha=${h.alpha} lies inside under both starting schemes, so the claim fails for alpha. Restarting every bootstrap refit from a ${gs.starts_per_resample}-point grid of initial values that does not depend on the full-data optimum gives an alpha interval of ${iv(gs.ci90.alpha)}, which also contains ${h.alpha}. We treat the tightened intervals as reliable because they hold under this grid-start scheme as well as from the optimum, whereas default-tolerance refits started at the optimum barely move from it; ${td.converged} and ${ts1.diagnostics.converged} of 400 tightened refits report success under the two schemes, and all refits are retained in the intervals. ` +
        `At SciPy's default tolerances the result depends on where the refits start: started at the full-data optimum, they stop after a median of ${dd1.median_iterations} iterations and give an alpha interval of ${iv(d1.alpha)}, which excludes ${h.alpha} as the claim states; from five jittered starts they give ${iv(d.alpha)}. ` +
        `We have not seen the parent's code, so we cannot confirm how its intervals were computed; a default-tolerance bootstrap started at the optimum is one explanation consistent with its result. ${prov}`,
      ...art, agent, ts,
    } as Json;
  }

  const wt = t.alpha[1] - t.alpha[0], wd1 = d1.alpha[1] - d1.alpha[0];
  const startsAgree = Math.abs(t.alpha[0] - ts1.alpha[0]) < 0.005 && Math.abs(t.alpha[1] - ts1.alpha[1]) < 0.005;
  if (!(wt > 5 * wd1) || !startsAgree) throw new Error("results no longer support the paper's claims as worded.");
  const claims: Json[] = [
    { text: `At SciPy's default L-BFGS-B tolerances, bootstrap refits on the 245 reconstructed Chinchilla runs give a 90% interval for $\\alpha$ that depends on the starting points: ${iv(d1.alpha)} from the full-data optimum, ${iv(d.alpha)} from five jittered starts.`, confidence: 0.85 },
    { text: `Started at the optimum, those default-tolerance refits stop after a median of ${dd1.median_iterations} iterations with a median largest parameter move of ${f(dd1.median_max_parameter_move, 4)}, while SciPy reports success for ${dd1.converged} of ${dd1.resamples}.`, confidence: 0.85 },
    { text: `With tightened tolerances the 90% interval for $\\alpha$ is ${iv(t.alpha)} under both optimum-anchored starting schemes, and ${iv(gs.ci90.alpha)} with grid restarts independent of the optimum; each contains the reported $\\alpha=${h.alpha}$, which the default-tolerance interval from the optimum excludes.`, confidence: 0.85 },
    { text: `At every compute cutoff from none to $C\\ge${tex(hi.cutoff)}$ FLOP, the tightened grid refit agrees with an independent least-squares implementation to within ${tol.toExponential(0)} in $\\alpha$, $\\beta$, $E$ and $\\beta/(\\alpha+\\beta)$.`, confidence: 0.85 },
  ];
  return {
    protocol: "ecdysis/0.1", type: "paper",
    title: "Premature optimiser termination makes bootstrap intervals depend on starting points in Chinchilla loss-law refits",
    abstract:
      `Refits of the Chinchilla parametric loss law (Hoffmann et al., 2022, Approach 3) to the runs reconstructed by Besiroglu et al. (2024) minimise a summed Huber loss with $\\delta=10^{-3}$. At SciPy's default tolerances, L-BFGS-B stops after a few iterations while reporting success, so bootstrap refits started at the full-data optimum barely move from it; we attribute this to the small objective relative to the default stopping thresholds, which we have not tested directly. ` +
      `On all 245 runs, a default-tolerance bootstrap started at the full-data optimum gives a 90% interval for $\\alpha$ about ${f(wt / wd1, 0)} times narrower than with tightened tolerances, enough to reverse whether it contains the value reported by Hoffmann et al.; jittered starts give an interval of a different width again. ` +
      `With tightened tolerances the interval for $\\alpha$ is ${iv(t.alpha)} with every refit started at the optimum, the same with the best of five starts per refit (four jittered by up to one unit in log $A$ and log $B$ and 0.05 in the exponents and log $E$), and ${iv(gs.ci90.alpha)} when every refit restarts from a ${gs.starts_per_resample}-point grid that does not depend on the optimum. ` +
      `We report this as a pitfall for interval estimation in these fits. It contradicts the $\\alpha$ component of the inclusion test in ${PARENT}, which an accompanying replication reports as refuted, while the exclusions of the reported $\\beta$ and $E$ hold under every optimiser and starting-point setting we tested on the full 245-run dataset, though not at a 1e19 FLOP compute cutoff, where Chrysalis-1 itself reports estimates close to the original. We have not seen that paper's code, so we cannot say whether its interval arose this way; other differences of method could also produce a narrow interval. ` +
      `Point estimates agree with an independent implementation at every compute cutoff tested; we have not run a coverage study of the intervals themselves. ` +
      `Limitations: the data are digitised from a figure; we examine one optimiser and one loss; and we test reported parameters, not the original training runs. ${prov}`,
    field: "ml", claims,
    builds_on: [
      { id: parentId, rel: "extends", basis: "reproduced", claims: ["C1"],
        note: `Re-ran the C1 refit on the same 245 reconstructed runs and objective; point estimates match (alpha=${f(fa.alpha)}, beta=${f(fa.beta)}, E=${f(fa.E, 2)}). The beta and E exclusions also reproduce; its alpha exclusion reproduces only with SciPy default tolerances and refits started at the optimum, and fails with tightened tolerances, as our accompanying replication reports.` },
      { id: "arxiv:2203.15556", rel: "replicates" },
      { id: "arxiv:2404.10102", rel: "method", basis: "reproduced",
        note: `Used the 245 runs these authors reconstructed from Hoffmann et al. Figure 4 (SHA-256 ${res.data_sha256.slice(0, 12)}) and reproduced their refit on 240 runs: alpha=${f(res.runs[1].fit.alpha)}, beta=${f(res.runs[1].fit.beta)}, E=${f(res.runs[1].fit.E, 2)}.` },
    ],
    ...art, agent, ts,
  } as Json;
}

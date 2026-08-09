# Academic Prose: What to Keep, What to Kill

De-AI-ing a thesis is not the same as de-AI-ing a blog post. Scholarly
writing is *conventionally* formal, hedged, and impersonal. Stripping those
traits produces text that reads human and fails review.

---

## 1. Traits that look like AI but are correct in a thesis

| Trait | Keep it because |
|---|---|
| Passive voice in methods | The agent is irrelevant: *containers were sampled at 15-minute intervals* |
| Hedged claims | *suggests*, *indicates*, *is consistent with* — overclaiming is the worse sin |
| Formal register | No contractions, no colloquialism, in the body |
| Repetition of key terms | Terminological consistency beats elegant variation. Do **not** substitute synonyms for defined terms |
| Signposting at chapter level | One paragraph stating chapter structure is standard |
| Long sentences | Complex qualified claims need them — vary length, do not simply shorten |

Do not "fix" these. Doing so is the most common failure of naive
de-AI editing.

---

## 2. Academic-specific tells that *are* machine signature

### 2.1 The literature-review drone — **C**

> *Numerous studies have explored waste collection optimisation. Smith
> (2019) examined routing. Jones (2020) investigated container placement.
> Lee (2021) analysed sensor deployment.*

A chain of `Author (year) verb-ed topic` with no synthesis. The machine
lists; the scholar argues.

**Repair.** Organise by claim, not by paper. Put the finding first and the
citation in support:

> *Container placement and routing are usually optimised in sequence, which
> assumes placement is insensitive to the routes it induces (Jones, 2020;
> Lee, 2021). Only Smith (2019) relaxes that assumption, and only for a
> fixed fleet.*

### 2.2 No disagreement in the literature — **C**

Every cited source agrees with every other. Real fields contain conflict.

**Repair.** Find and state at least one genuine tension, and say where your
work stands relative to it.

### 2.3 Methods without friction — **H**

The data were clean, the model converged, nothing was excluded.

**Repair.** Report the truncated export, the duplicated column, the offline
sensors, the records dropped and why. A methods section without exclusions
is not believable.

### 2.4 Results narrated, not interpreted — **H**

> *Table 5.2 shows the coefficients. The R² was 0.68. Figure 5.3 shows
> residuals.*

Describing what the reader can already see.

**Repair.** Say what it means and what it costs: which coefficient behaved
unexpectedly, what the residual pattern implies about the specification,
which conclusion is therefore weaker than hoped.

### 2.5 Uniform citation density — **H**

Exactly one or two citations per paragraph throughout.

**Repair.** Contested claims need several; your own results need none.
Density should follow the argument.

### 2.6 Generic contribution statements — **C**

> *This research contributes to the literature by providing valuable
> insights into waste collection optimisation.*

**Repair.** State what is new in a form that could be wrong:

> *This work is the first to fit container-level fill-rate models to four
> years of Portuguese sensor data and to use the fitted rates directly as
> demand in a p-median formulation, rather than assuming uniform
> generation.*

---

## 3. Rhythm in scholarly writing

Academic sentences run longer than general prose — a mean near 24 words is
normal. The requirement is **variance**, not brevity.

- Long sentence for the qualified claim.
- Short one for the consequence.
- Then a medium sentence carrying the reader to the next point.

A short sentence after a long one signals confidence. Overusing short
sentences signals a blog.

---

## 4. Thesis-specific checklist

Before delivering any chapter:

| # | Check |
|---|---|
| 1 | Every quantitative claim traces to a query, table, or cited source |
| 2 | At least one limitation is owned in every methods and results section |
| 3 | The literature review contains at least one stated disagreement |
| 4 | Defined terms are used consistently, never varied for elegance |
| 5 | The contribution statement is falsifiable, not laudatory |
| 6 | No section is a uniform 4 paragraphs of 5 sentences |
| 7 | Figures and tables are interpreted, not narrated |
| 8 | Portuguese place, institution, and waste-fraction names are spelled correctly and consistently |
| 9 | Equations are OMML, numbered, and referenced in the text before they appear |
| 10 | Nothing in the chapter would survive replacing "Rio Maior" with another city |

Item 10 is the strongest test. If the chapter still makes sense about a
different city, it contains no real research.

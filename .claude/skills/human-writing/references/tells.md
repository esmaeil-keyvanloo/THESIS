# Catalogue of LLM Writing Tells

Each entry: the tell, why it betrays a machine, and the repair.
Severity — **C** critical (never ship), **H** high, **M** moderate.

---

## 1. Lexical

### 1.1 The flagged vocabulary — **C**

Words that appear in LLM output at many times their natural rate:

| Class | Words |
|---|---|
| Verbs | delve, leverage, utilize, underscore, showcase, foster, harness, embark, unlock, elevate, streamline, spearhead |
| Adjectives | pivotal, crucial, vital, robust, seamless, holistic, comprehensive, multifaceted, nuanced, intricate, invaluable, cutting-edge, game-changing |
| Nouns | myriad, plethora, realm, landscape, tapestry, testament, beacon, cornerstone, paradigm, synergy, journey (figurative) |
| Phrases | navigate the complexities, in today's fast-paced world, at its core, the ever-evolving, a treasure trove, plays a pivotal role, serves as a testament |

**Repair.** Replace with the plain word. `utilize` → `use`. `leverage` →
`use`, `exploit`, or name the actual mechanism. `robust` → say what makes it
robust: *tolerates missing readings*, *converges under degeneracy*.
`comprehensive` is usually deletable with no loss.

> Machine: *We leveraged a robust framework to delve into the multifaceted landscape of container placement.*
> Human: *We tested placements against four years of fill readings, including the months when a third of the sensors were offline.*

### 1.2 Hollow intensifiers — **H**

`significantly`, `substantially`, `dramatically`, `vastly`, `remarkably`,
`greatly` used with no measurement attached.

**Repair.** Attach the number, or delete the word. *Significantly reduced
distance* → *reduced distance by 18 %*. If the number does not exist, the
claim does not either.

### 1.3 Hedge stacking — **M**

`may potentially`, `could possibly`, `might arguably`, `it seems likely that
perhaps`.

**Repair.** One hedge, chosen deliberately. `may reduce`, not `may
potentially reduce`.

### 1.4 Announcement phrases — **C**

`It is important to note that`, `It is worth noting that`, `Notably,`,
`Importantly,`, `Interestingly,`, `It should be emphasised that`.

**Repair.** Delete. If the sentence is important, its position in the
paragraph shows that. A writer who must announce importance has not
established it.

---

## 2. Syntactic

### 2.1 Uniform sentence length — **C**

The strongest single signal. LLM sentences cluster at 15–22 words with low
variance. Human writing varies wildly.

**Repair.** See the rhythm rule in `SKILL.md`. Measure, do not eyeball —
the detector reports standard deviation.

### 2.2 Tricolon abuse — **C**

Everything arrives in threes: *efficient, scalable, and maintainable*;
*collect, analyse, and optimise*.

**Repair.** Use two items, or four, or one. Three is fine occasionally — it
is the *reflex* that betrays. If a document has more than one triple per
500 words, cut some.

### 2.3 The not-just-but construction — **C**

*This is not just a routing problem — it is a question of urban equity.*
*It's not about the sensors. It's about what they reveal.*

**Repair.** State the claim once, directly. The construction manufactures
profundity by contrast and reads as advertising.

### 2.4 Trailing participial summary — **H**

Sentences ending `, ensuring optimal performance`, `, highlighting the
importance of X`, `, paving the way for Y`, `, ultimately leading to Z`.

**Repair.** Cut the tail, or promote it to its own sentence with a real
subject. *…, ensuring reliability* → *…. Reliability follows from the
redundant readings.*

### 2.5 Over-parallelism — **M**

Every list item, clause, and heading built to identical grammar.

**Repair.** Let one item break the pattern. Real thought is uneven.

### 2.6 Em-dash saturation — **H**

More than one em dash per 300 words, especially as a substitute for
commas, colons, and parentheses alike.

**Repair.** Vary the punctuation. Commas for asides, colons for
consequences, parentheses for genuine digressions, em dashes for
interruptions only.

### 2.7 Rule-of-three transitions — **M**

`Furthermore`, `Moreover`, `Additionally` opening consecutive paragraphs.

**Repair.** At most one explicit connective per three paragraphs. Sequence
usually carries the logic without help.

---

## 3. Structural

### 3.1 Equal-weight sections — **H**

Every section 3–4 paragraphs, every paragraph 4–5 sentences.

**Repair.** Give sections the length their content deserves. A section may
be two sentences if two sentences finish it.

### 3.2 Topic-sentence sandwich — **C**

Paragraph opens with a claim, develops it, then closes by restating the
claim in different words.

**Repair.** Delete the closing restatement. Always. The paragraph ends when
the evidence ends.

### 3.3 Universal bold lead-ins — **H**

Every bullet formatted `**Term** — explanation`.

**Repair.** Use the pattern where the term is genuinely a label being
defined. Elsewhere, write plain bullets or prose.

### 3.4 Gerund and question headings — **H**

`Understanding Container Dynamics`, `Exploring the Data`, `What Does This
Mean?`

**Repair.** Name the content as a noun phrase: `Container fill dynamics`,
`Data sources and coverage`. Academic headings are labels, not invitations.

### 3.5 Mirror-image intro and conclusion — **M**

The conclusion restates the introduction in the same order with synonyms.

**Repair.** A conclusion should contain at least one thing the introduction
could not have said, because the work had not been done yet.

### 3.6 Preamble before delivery — **H**

Text that describes what it is about to do before doing it: *This section
will explore…*, *In what follows, we examine…*

**Repair.** In a thesis, one signposting sentence per chapter is
conventional and acceptable. Per section, it is padding. Delete.

---

## 4. Content

### 4.1 Absent specificity — **C**

No numbers, no names, no dates, no places. Text that would survive
find-and-replace of its entire subject matter.

**Repair.** Every paragraph of substance earns at least one concrete
particular. *Sensor coverage was incomplete* → *142 of 389 containers
reported no reading between June and September 2022*.

### 4.2 Unattributed authority — **C**

`Studies show`, `Research indicates`, `It is widely accepted`, `Experts
agree` with no citation.

**Repair.** Cite, or drop the appeal. In a thesis this is not a style
problem but an integrity problem.

### 4.3 Manufactured balance — **H**

Every advantage answered by a proportional disadvantage; no position taken.

**Repair.** Real analysis concludes. If the evidence favours one option,
say so and say how strongly.

### 4.4 No owned limitation — **H**

Nothing went wrong, nothing was uncertain, no data were excluded.

**Repair.** Name what failed, what was dropped, and what remains unknown.
This is the most human thing a technical document can do — and reviewers
reward it.

### 4.5 Zero stance — **M**

No trace of a person choosing among alternatives.

**Repair.** Where the field permits, say *we chose X over Y because Z*.
Where it does not, at least record the choice in a methods note.

---

## 5. Typographic

| Tell | Severity | Repair |
|---|---|---|
| Emoji in headings or body of formal text | C | Remove |
| Title Case On Every Heading | M | Sentence case, consistently |
| Bold scattered through prose for emphasis | H | Reserve bold for defined terms; use word order for emphasis |
| Mixed straight and curly quotes | M | Normalise to curly in prose |
| `→`, `✓`, `•` in academic body text | H | Use words or proper list markup |
| Nested bullets three levels deep | M | Restructure as prose or a table |
| Horizontal rules between every section | M | Use headings; rules are for real breaks |

---

## 6. Non-native-speaker note

Some traits read as "AI" but are simply second-language English: article
misuse, preposition drift, over-formal register, calques from Portuguese or
Persian.

These are **corrected**, not flattened. Fix the grammar; keep the sentence
shape. A thesis by a Portuguese-based Iranian researcher should not read
like it was written in Ohio. Idiosyncratic but correct phrasing is
evidence of authorship, and is worth protecting.

---
name: human-writing
description: Detect and remove the stylistic fingerprints that mark text as LLM-generated, and rewrite it so it reads as human academic prose. Use BEFORE delivering any written deliverable — thesis chapters, reports, papers, abstracts, literature reviews, emails, or documentation — and whenever the user says text sounds robotic, mechanical, AI-generated, or "not like me". Also use when reviewing or editing existing draft text for style.
---

# Human Writing

LLM prose fails not because it is wrong but because it is *evenly* good. It
has no rhythm, no risk, and no residue of a person having thought about
something in particular. This skill finds that signature and removes it.

## When to run

| Situation | Action |
|---|---|
| About to deliver any written document | Run the full pass |
| User says "sounds robotic / AI / not human" | Run the full pass |
| Editing an existing draft | Run detection, fix only what fires |
| Short chat reply | Skip — this is for documents |

## Procedure

1. **Lint.** Run the detector over the draft:

   ```bash
   python .claude/skills/human-writing/scripts/ai_tells.py <file.md|file.txt>
   ```

   It reports hits by category with line numbers and a density score.

2. **Read `references/tells.md`** for the full catalogue and the rewrite for
   each tell. Do not fix from memory — the specific repairs matter.

3. **For academic or thesis text, also read `references/academic.md`.**
   Scholarly prose has its own tells, and some "AI-sounding" traits are
   actually correct in a thesis. Removing them makes the text worse.

4. **Rewrite.** Apply repairs in this order — earlier ones make later ones
   easier to see:

   | Order | Fix | Why first |
   |---|---|---|
   | 1 | Cut filler openers and hollow transitions | Reveals the real sentence |
   | 2 | Replace flagged vocabulary | Mechanical, no judgement needed |
   | 3 | Break the rhythm (see below) | The single strongest signal |
   | 4 | Add concrete specifics | Numbers, names, dates, places |
   | 5 | Restore stance and limitation | A human owns their uncertainty |
   | 6 | Break structural symmetry | Sections need not be equal |

5. **Re-lint.** Target: density score below 4 hits per 500 words, and zero
   hits in the *Critical* categories.

6. **Read one paragraph aloud.** If it could open any document on any
   subject, it is still generic. Rewrite it around something only this
   project could have produced.

## The rhythm rule

The most reliable tell is uniform sentence length. LLMs write 15–22 word
sentences almost exclusively. Humans do not.

- Target a standard deviation of **> 8 words** across any 10 sentences.
- Every paragraph gets at least one sentence under 8 words.
- Allow one long sentence per paragraph to run past 35 words if the idea
  genuinely requires it.
- Never let three consecutive sentences fall within 3 words of each other.

Short sentences carry emphasis. Use them where the emphasis belongs, not
decoratively.

## Hard prohibitions

Never appear in delivered text:

- `delve`, `leverage` (as a verb), `underscore`, `showcase`, `tapestry`,
  `realm`, `landscape` (figurative), `testament to`, `navigate the
  complexities`, `in today's fast-paced world`, `at its core`
- `It is important to note that`, `It is worth noting that`
- `Not only … but also` more than once per document
- `In conclusion,` as the opening of a conclusion
- The construction `This is not just X — it is Y.`
- A paragraph that ends by restating its own first sentence
- Bolded lead-ins on every bullet of every list
- Gerund headings: `Understanding X`, `Exploring Y`, `Navigating Z`

## Preserve the author

This skill removes machine signature; it does not impose a house voice. If
a writing profile exists for the user, match it. For non-native English
writers, correct grammar and idiom but **keep** their characteristic
sentence shapes and word choices — flattening those is its own kind of
erasure. The goal is the author sounding like themselves on a good day.

## Files

| File | Contents |
|---|---|
| `references/tells.md` | Full catalogue: lexical, syntactic, structural, content, typographic — each with its repair |
| `references/academic.md` | Thesis and journal prose; which "tells" are legitimate in scholarly writing |
| `scripts/ai_tells.py` | Regex + statistical detector, reports hits and density score |

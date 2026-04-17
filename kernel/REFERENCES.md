# References

The kernel body does not import jargon from external frameworks. Concepts
are described in the kernel's own vocabulary so the principles stand on
their own, without requiring the reader to already know the source
material.

This file is the attribution trail. It lists the sources that informed
the kernel's contents, the concepts borrowed from each, and where in the
kernel each concept shows up (under different wording).

---

## Behavioral economics / cognitive psychology

**Daniel Kahneman — *Thinking, Fast and Slow* (2011).**

Informs the failure-mode framing in [CONSTITUTION.md](./CONSTITUTION.md)
and [FAILURE_MODES.md](./FAILURE_MODES.md).

Concepts borrowed:

| Source term                | Kernel wording                                            |
|----------------------------|-----------------------------------------------------------|
| System 1 / System 2        | "pattern-matching" / "deliberate examination"             |
| WYSIATI                    | "reasoning only from what is present"                     |
| Question substitution      | "answering a nearby easier question"                      |
| Anchoring                  | "first-framing persistence"                               |
| Narrative fallacy          | "story-fit over evidence"                                 |
| Planning fallacy           | "systematic underestimation of effort and risk"           |
| Overconfidence             | retained as "confidence exceeding accuracy"               |

---

## Strategy / decision-making

**John Boyd — OODA loop (1970s–80s, via briefings and lectures).**

Informs Principle II (Orientation precedes observation) and Principle IV
(The loop is the unit of progress) in [CONSTITUTION.md](./CONSTITUTION.md).

Concepts borrowed:

| Source term                      | Kernel wording                                  |
|----------------------------------|-------------------------------------------------|
| Observe–Orient–Decide–Act        | "feedback loop" / "closed loop"                 |
| Orient (as dominant step)        | "orientation precedes observation"              |
| Loop speed / tempo               | "speed of iteration beats size of any step"     |

---

## Investing / epistemics under uncertainty

**Ray Dalio — *Principles: Life and Work* (2017).**

Informs Principle I (Explicit > implicit) and the counter to "confidence
exceeding accuracy" in [FAILURE_MODES.md](./FAILURE_MODES.md).

Concepts borrowed:

| Source term              | Kernel wording                                          |
|--------------------------|---------------------------------------------------------|
| Radical transparency     | "expose the model, including the parts that are wrong" |
| Believability-weighting  | "weight by track record, not volume or confidence"      |

---

## Mental models / multidisciplinary reasoning

**Charlie Munger — speeches and *Poor Charlie's Almanack* (2005).**

Informs Principle III (No model is sufficient alone) in
[CONSTITUTION.md](./CONSTITUTION.md).

Concepts borrowed:

| Source term               | Kernel wording                                          |
|---------------------------|---------------------------------------------------------|
| Latticework of mental models | "stack of lenses from different disciplines"         |
| Inversion                 | "failure-first: what would definitely cause failure?"   |
| Margin of safety          | "buffer if assumptions slip by 30–50%"                  |

The related "base rates" and "second-order effects" language is common
across the decision-theory literature and is retained in plain form.

---

## How to read this

The kernel does not require familiarity with any of the source material
above. If a principle is unclear, read the kernel's own description
first, then consult the source if you want the deeper exposition.

If a source in this list can no longer be traced to something in the
kernel, the attribution has lapsed — the kernel has moved on from it, and
the entry should be removed from this file.

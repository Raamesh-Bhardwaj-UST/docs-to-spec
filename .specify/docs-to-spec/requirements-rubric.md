# Requirements rubric (docs-to-spec)

Every harvested requirement is checked against this rubric. A requirement passes only if every criterion passes.

## Criteria (ISO/IEC/IEEE 29148 characteristics)

| ID | Criterion | Passes when |
|----|-----------|-------------|
| C1 | Singular | The statement expresses one requirement. No "and/or" joining two behaviours. |
| C2 | Unambiguous | Two engineers would build the same thing. No weak words (see list). |
| C3 | Verifiable | A concrete acceptance test with real values can be written for it. |
| C4 | Complete | Trigger, actor/system, response, and any limits or error behaviour are stated, or marked [NEEDS CLARIFICATION]. |
| C5 | Feasible | Nothing in the architecture file or sources makes it impossible as stated. |
| C6 | Traceable | Cites a snapshot file and section that actually supports it. |
| C7 | Implementation-free | States what, not how (no class names, libraries or UI widgets unless the source mandates them). |
| C8 | Consistent | Does not contradict another requirement; if it does, both are listed under Conflicts. |

## EARS patterns

- Ubiquitous: The <system> shall <response>.
- Event-driven: When <trigger>, the <system> shall <response>.
- State-driven: While <state>, the <system> shall <response>.
- Unwanted behaviour: If <condition>, then the <system> shall <response>.
- Optional feature: Where <feature is included>, the <system> shall <response>.
- Complex: combinations of the above, e.g. While <state>, when <trigger>, the <system> shall <response>.

## Weak words (each occurrence fails C2 unless quantified in the same sentence)

fast, quick, slow, responsive, efficient, user-friendly, easy, intuitive, simple, flexible, robust, reliable,
scalable, secure (unqualified), appropriate, adequate, reasonable, normal, as needed, as appropriate,
if possible, where possible, etc., and/or, support (as a verb without detail), handle, manage, process
(without detail), minimal, maximal, optimal, seamless, modern, best-in-class, state-of-the-art, some, several, many.

## Question ranking (for open questions)

1. Scope: changes what is built or for whom
2. Security / privacy: data exposure, access, retention
3. User experience: what the user sees or does
4. Technical detail: values, limits, formats

## Status values

confirmed | needs-clarification | inferred | assumed-pending-confirmation | needs-human

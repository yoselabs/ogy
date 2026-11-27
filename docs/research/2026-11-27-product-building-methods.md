# How known methods build a product, and where ogy stands (2026-11-27)

Research by Fable (ontology-designer 0.6.0), asked by the owner: "should I start with idea, pain point, decision, or what?"
The owner asked to keep this list. Raw evidence, not requirements: the knowledge base holds only the decisions that came
out of it (`product/capture/decision/from-pain-to-built`, answered start-anywhere; `product/capture/decision/measured-outcome`,
answered not-yet; `product/capture/decision/pain-kind`, answered now).

## The methods

| method | its chain | where it puts the problem | what ogy matches | what ogy lacks | source |
|---|---|---|---|---|---|
| Opportunity Solution Tree (Teresa Torres) | outcome, opportunities ("an unmet customer need, pain point, or desire"), solutions, assumption tests | above the solution | pain (opportunity), decision options (solutions) | the outcome at the root, assumption tests | producttalk.org/opportunity-solution-trees |
| Jobs To Be Done | the job (stable), the struggle (the pain), the desired outcome | the struggle behind the job | goal with `for` (nearest to the job), pain (the struggle) | the job as its own thing | recalled |
| Lean Startup | build, measure, learn; "the unit of progress is validated learning"; hypotheses | a hypothesis to test | build (ogy work, built lines) | measure and learn, hypotheses as claims to test | theleanstartup.com/principles |
| Double Diamond (Design Council) | discover, define, develop, deliver | the first diamond | the work types discover, design, build are the same cut | | designcouncil.org.uk |
| Shape Up (Basecamp) | a pitch: problem, appetite, solution, rabbit holes, no-gos | presented with the solution | a pitch is a decision: the pain cited, options, an option that sets null | appetite (a time budget) | basecamp.com/shapeup/1.5-chapter-06 |
| Impact Mapping | goal, actors, impacts, deliverables, each serving the one before | none: starts from the goal | goal, actor, capability (impact), workflow and interface (deliverables) | | impactmapping.org/drawing.html |
| Value Proposition Canvas (Strategyzer) | jobs, pains, gains against products, pain relievers, gain creators | pains, apart from what relieves them | pain apart from the goal and capability that relieve it | gains as their own thing | strategyzer.com |
| ArchiMate motivation | stakeholder, driver, assessment, goal, outcome, principle, requirement | assessment | assessment (pain), goal, principle, requirement (rule) | outcome | recalled (the Open Group pages need a login) |

## Where they agree

- The problem sits above the solution. An idea is nothing until we know which problem it solves (the owner, 2026-11-27).
- The chain is a tree read both ways: from the problem down to what is built, and from what is built up to why.
- None forces one entry point; the two that name a start (Double Diamond, the Opportunity Solution Tree) say start by
  understanding the problem.
- Five of the eight hold a measured result after release (an outcome, validated learning); ogy does not yet (bead
  `ogy-34d`, decision measured-outcome).

## ogy's chain

```
pain -> goal -> capability -> workflow (steps, rows) -> interface, handler, rule
        decisions at any link; principles above all
```

Start with what you have, written as what it is: a pain as a pain entry agreed by its own card; an idea as a decision whose
options set what it would build, with not now among them; a goal as a goal; code as entries with their source. `ogy work`
lists what is missing above and below: a goal with no pain (`no-reason`), a goal nothing delivers (`unused`), a capability
with no goal or no workflow (`unrealized`, `no-workflow`), a flow with no screen or handler, a screen with no code.

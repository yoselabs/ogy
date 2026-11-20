# Blame pass, default model (claude-opus-5-5)

One reader (the coordinator), not blind, per [blame.md](blame.md). One line per error both scorers agree on:
`run fact item-or-K-or-F | verdict | the why line`.

A-1 4 4b | unclear | A figure the owner fixed is a product value, not a config_key, because nothing overrides it.
A-1 12 K | structural | Many remarks per bike, created whenever someone likes, need their own entity, because a create effect must name an entity; a list attr would hide the creating.
A-1 12 12a | structural | Many remarks per bike, created whenever someone likes, need their own entity, because a create effect must name an entity; a list attr would hide the creating.
A-1 13 K | misled-by: external | A server of another firm is an external, not an actor; what it triggers is a case whose effect is the paid transition.
A-1 13 13a | misled-by: external | A server of another firm is an external, not an actor; what it triggers is a case whose effect is the paid transition.
A-1 15 15b | unclear | An invariant that must always hold is a rule; the automatic check is its proof.
A-1 22 22d | unclear | The owner's figure is a value; the host override is a config_key bound to it, so the default stays the product fact.
A-1 24 K | structural | A guarantee that must keep holding is a rule; it is not a set, because these are fields, not members.
A-2 12 K | structural | Each remark is created on its own at any time, and a bike can carry several. A create effect must name an entity, so a remark is an entity. It is not a list attr on bike, because a list attr cannot be the target of create.
A-2 12 12a | structural | Each remark is created on its own at any time, and a bike can carry several. A create effect must name an entity, so a remark is an entity. It is not a list attr on bike, because a list attr cannot be the target of create.
A-2 12 12b | structural | Each remark is created on its own at any time, and a bike can carry several. A create effect must name an entity, so a remark is an entity. It is not a list attr on bike, because a list attr cannot be the target of create.
A-2 13 K | structural | The notifier is PayRight's server, and an actor is never an external, so it is an external. A case reads it in `when` and moves the hire to paid. That row has an effect, so an operation must perform it.
A-2 13 F | structural | The notifier is PayRight's server, and an actor is never an external, so it is an external. A case reads it in `when` and moves the hire to paid. That row has an effect, so an operation must perform it.
A-2 13 13a | structural | The notifier is PayRight's server, and an actor is never an external, so it is an external. A case reads it in `when` and moves the hire to paid. That row has an effect, so an operation must perform it.
A-2 13 13b | structural | The notifier is PayRight's server, and an actor is never an external, so it is an external. A case reads it in `when` and moves the hire to paid. That row has an effect, so an operation must perform it.
A-2 15 15b | unclear | It is an invariant that must always hold, so it is a rule. The automatic check is its proof. It is not a transition, because no single move enforces it.
A-2 24 K | structural | It is a fixed contract that other companies rely on, and it is a build fact, so it is a software rule. It is not a view, because no person sees it.
A-3 4 4b | unclear | A business figure the owner fixed belongs in the product layer as a value; not a config_key, because nothing overrides it.
A-3 12 K | structural | Remarks that anyone can create at any time and that a bike carries several of are their own entity; not a list attr on bike, because each remark is created on its own.
A-3 12 12a | structural | Remarks that anyone can create at any time and that a bike carries several of are their own entity; not a list attr on bike, because each remark is created on its own.
A-3 15 15b | unclear | An invariant that must always hold is a rule, and the automatic check is its proof; not a state, because it constrains across hires.
A-3 24 K | structural | A response layout that other parties rely on must always hold, so it is a rule they can check; not text on the command, because a change must surface as its own agreed sentence.
A-4 4 4b | unclear | A business figure the owner fixed is a value; not config_key, since nothing can override it.
A-4 12 K | structural | Remarks are created freely and many per bike, so each is its own entity linked to its bike; not an attr of type list on bike, since a list can't be created on its own.
A-4 12 12a | structural | Remarks are created freely and many per bike, so each is its own entity linked to its bike; not an attr of type list on bike, since a list can't be created on its own.
A-4 12 12b | structural | Remarks are created freely and many per bike, so each is its own entity linked to its bike; not an attr of type list on bike, since a list can't be created on its own.
A-4 15 15b | unclear | An invariant that must always hold is a rule, and the automatic check is its proof; not an attr max, since it constrains hires across bikes.
A-4 24 K | structural | A shape of [10]'s response that others rely on is a checkable rule, whose fields name real attrs; not text on the command, since impact must be able to read it.
A-5 4 4b | unclear | A figure the owner fixed is a value; not config_key, since nobody can override it.
A-5 12 K | structural | Created anytime, many per bike, so its own entity (createable); not a list attr on bike, which could not be created on its own.
A-5 12 12a | structural | Created anytime, many per bike, so its own entity (createable); not a list attr on bike, which could not be created on its own.
A-5 13 K | misled-by: external | A server of another firm is an external, not an actor; its call drives a system step whose effect is the paid transition, performed by an operation.
A-5 13 F | misled-by: external | A server of another firm is an external, not an actor; its call drives a system step whose effect is the paid transition, performed by an operation.
A-5 13 13a | misled-by: external | A server of another firm is an external, not an actor; its call drives a system step whose effect is the paid transition, performed by an operation.
A-5 13 13b | structural | A server of another firm is an external, not an actor; its call drives a system step whose effect is the paid transition, performed by an operation.
A-5 22 22d | unclear | The owner's figure is a value (product); the host's override is a config_key binding it (software), per layers-split.
A-5 24 K | structural | A contract that must always hold is a rule; not a command field, since the command has no shape field.
A-6 12 K | structural | Remarks are created freely and several hang on one bike, so each is its own entity; not a list attr, which cannot be created on its own.
A-6 12 12a | structural | Remarks are created freely and several hang on one bike, so each is its own entity; not a list attr, which cannot be created on its own.
A-6 12 12b | structural | Remarks are created freely and several hang on one bike, so each is its own entity; not a list attr, which cannot be created on its own.
A-6 15 15b | unclear | An invariant that must always hold is a rule; the automatic check is its proof, not evidence.
A-6 24 K | structural | A shape others rely on that must always hold is a rule; not part of the command's text, since outsiders depend on it.
B-1 24 K | structural | Outside apps rely on a fixed contract, which is checkable, so it is a rule. It is not just the interface's text.
B-2 24 K | structural | A fixed response shape that others rely on is a checkable rule; not text on the interface, because a check reads it
B-3 24 K | structural | It's a fixed layout that others rely on and a test can check, so it's a rule the interface satisfies; it isn't text on [10] because a check reads it.
B-4 24 K | structural | A promise that must always hold and can be tested is a rule; not just text on the interface, because a check reads it.
B-5 24 K | structural | A promise that always holds and that others rely on is a rule satisfied by the interface; not part of the interface's text, because a check has to read it.
B-6 13 13b | structural | A system that calls us is an actor, not a dependency; its call starts the event that fires the paid transition
B-6 24 K | structural | A layout others rely on that must always hold; not text on the interface, because a check must read it; not a principle, because it can be tested
C-1 4 4b | unclear | It is a number with a unit that was decided once. It is not a setting because no knob is named.
C-1 18 K | structural | A view is a screen that serves steps, and no kind covers a reusable fragment. Storage is a projection, so "one tile" is only text.
C-1 18 18a | structural | A view is a screen that serves steps, and no kind covers a reusable fragment. Storage is a projection, so "one tile" is only text.
C-1 18 18b | structural | A view is a screen that serves steps, and no kind covers a reusable fragment. Storage is a projection, so "one tile" is only text.
C-1 22 22d | unclear | The figure is the owner's decided quantity. The setting is only the knob that can override it, and it defaults to that quantity.
C-1 24 K | structural | It is a stable response layout that others depend on and a test can check. It is not a principle.
C-2 15 15b | unclear | It is checkable and has an automatic test, so it is a rule, not a principle.
C-2 18 K | structural | It is a reusable UI component. A view is a screen that serves steps, and the tile serves none on its own. No check reads it, so it stays as text on the map view and the past-hires view.
C-2 18 18a | structural | It is a reusable UI component. A view is a screen that serves steps, and the tile serves none on its own. No check reads it, so it stays as text on the map view and the past-hires view.
C-2 18 18b | structural | It is a reusable UI component. A view is a screen that serves steps, and the tile serves none on its own. No check reads it, so it stays as text on the map view and the past-hires view.
C-2 24 K | structural | It is a contract that a test can check and outside companies rely on, so it is a rule, not a principle or plain text on the command.
C-3 24 K | structural | A promise others rely on that a test can check is a rule; not a principle
C-4 15 15b | unclear | A testable must-hold business rule with an automatic check; not a principle, which no test can check.
C-4 18 K | structural | A tile is a fragment of a screen, not a view (a screen serving steps); how it is laid out is text a reader needs, not a field any check reads.
C-4 18 18a | structural | A tile is a fragment of a screen, not a view (a screen serving steps); how it is laid out is text a reader needs, not a field any check reads.
C-4 18 18b | structural | A tile is a fragment of a screen, not a view (a screen serving steps); how it is laid out is text a reader needs, not a field any check reads.
C-4 24 K | structural | A fixed promise to callers that can be tested; not an attribute or a principle.
C-5 4 4b | unclear | A number times a unit, decided once by the owner; not a setting, because no knob is named; not an attribute, because it is not kept per hire
C-5 12 12b | structural | Remarks are things created at will, several per bike, so they are an entity linked as a many attribute; not an enum, because the list is open
C-5 15 15b | structural | A must-always-hold statement with an automatic check; not a principle, because a test can check it
C-5 18 K | structural | A reused UI tile is a build detail inside two views; no kind models a component, so it is text on the views serving the map step and the past-hires step; not a view, because it is no screen and serves no step by itself
C-5 18 18a | structural | A reused UI tile is a build detail inside two views; no kind models a component, so it is text on the views serving the map step and the past-hires step; not a view, because it is no screen and serves no step by itself
C-5 18 18b | structural | A reused UI tile is a build detail inside two views; no kind models a component, so it is text on the views serving the map step and the past-hires step; not a view, because it is no screen and serves no step by itself
C-5 24 K | structural | A must-always-hold contract others rely on; not an attribute or an entity, because it constrains the reply's layout, not stored facts
C-6 15 15b | structural | A must-always-hold statement with an automatic check is a rule with a proof. Not a principle, because a test checks it.
C-6 24 K | structural | A fixed contract that others rely on is a must-hold statement, so it is a rule (no proof stated yet). Not a view or a principle, because it can be checked.
C0-1 4 4b | unclear | A business figure the owner fixed is a quantity in the product layer; it's not a setting because nothing overrides it.
C0-1 15 15b | unclear | An invariant that must always hold is a rule, and the automatic check is its proof; it isn't a state, which describes one record.
C0-1 24 K | structural | A promise that must always hold for outside callers is a rule. A command has no response-shape field, and a term would only define a word.
C0-2 15 15b | unclear | It is an invariant that must always hold and has an automatic check. It is not a constraint on an attribute, because it spans hires.
C0-2 24 K | structural | It is a fixed contract that outsiders rely on, so a check must guard it. It is not just text on the command [10], because checks read it.
C0-3 13 K | structural | PayRight's notifier belongs to the dependency, so it can only be a case's `when`; not actor, because the glossary says an actor is never a dependency
C0-3 13 F | structural | PayRight's notifier belongs to the dependency, so it can only be a case's `when`; not actor, because the glossary says an actor is never a dependency
C0-3 13 13a | structural | PayRight's notifier belongs to the dependency, so it can only be a case's `when`; not actor, because the glossary says an actor is never a dependency
C0-3 13 13b | structural | PayRight's notifier belongs to the dependency, so it can only be a case's `when`; not actor, because the glossary says an actor is never a dependency
C0-3 15 15b | unclear | Something that must always hold and is checked automatically is a rule with proof; not principle, because it is checked in code
C0-3 22 22d | unclear | The figure the owner picked is a quantity; the host's override is a setting whose default points to that quantity
C0-3 24 K | structural | A reply shape others depend on must always hold, so it is a checkable rule; not just text in the command, because a check reads it (rigid-where-checked)
C0-4 4 4b | unclear | The owner fixed a business figure, so it is a product quantity. It is not a setting because nothing says the host can override it.
C0-4 12 K | structural | Notes created at will, several per bike, are their own entity so that a create effect can name them. A single many-valued attribute on bike would hide that they are separate items.
C0-4 12 12a | structural | Notes created at will, several per bike, are their own entity so that a create effect can name them. A single many-valued attribute on bike would hide that they are separate items.
C0-4 22 22d | unclear | The owner's figure is a product quantity, and the host override is a software setting whose default is that quantity. This keeps business and build facts in their own layers.
C0-4 24 K | structural | Other companies rely on a layout that must hold, so it is a rule that impact can read. Text on the command would leave it unchecked.
C0-5 4 4b | unclear | The owner fixed a figure with a unit, so it is a quantity. Not a setting, because no one can override it.
C0-5 15 15b | unclear | An invariant that must always hold, with a test, is a rule with proof. Not an attribute max, because it spans several hires.
C0-5 24 K | structural | A fixed contract others rely on must always hold, so it is a rule. Not text on the command, because breaking it is a checked impact.
C0-6 4 4b | unclear | A figure the owner fixed is a quantity; not setting (no host override named) and not rule.
C0-6 13 K | structural | The notifier is part of the PayRight dependency, so it is not an actor (an actor is never a dependency). What we do when it calls is a case that moves the hire to paid.
C0-6 13 F | structural | The notifier is part of the PayRight dependency, so it is not an actor (an actor is never a dependency). What we do when it calls is a case that moves the hire to paid.
C0-6 13 13a | structural | The notifier is part of the PayRight dependency, so it is not an actor (an actor is never a dependency). What we do when it calls is a case that moves the hire to paid.
C0-6 15 15b | unclear | An invariant with an automatic check is a rule with a proof. It is not a principle, because it is checked in code rather than used to weigh decisions.
C0-6 24 K | structural | A promise that outside callers rely on is a rule about the command [10]. It is not command text alone, because the promise must hold and be checkable.

| name | arm | fact | runs blamed of runs in the arm |
|---|---|---|---|
| external | A | 13 | 2 of 6 |

## Arm B addendum, per run

| run | B1 | B2 | B3 | B4 | B5 | B6 |
|---|---|---|---|---|---|---|
| B-1 | 1 | 1 | 1 | 1 | 1 | 1 |
| B-2 | 1 | 1 | 1 | 1 | 1 | 1 |
| B-3 | 1 | 1 | 1 | 1 | 1 | 1 |
| B-4 | 0 | 1 | 1 | 1 | 1 | 1 |
| B-5 | 1 | 1 | 1 | 1 | 1 | 1 |
| B-6 | 1 | 1 | 1 | 1 | 1 | 1 |
| of 6 | 5 | 6 | 6 | 6 | 6 | 6 |

B5: every run has [25] `satisfied by [7]`, the handler that charges the card.

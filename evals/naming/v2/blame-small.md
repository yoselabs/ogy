# Blame pass, small model (claude-haiku-5-5)

One reader (the coordinator), not blind, per [blame.md](blame.md). One line per error both scorers agree on:
`run fact item-or-K-or-F | verdict | the why line`. Every group of an arm and fact with 3 or more runs in error was read
line by line (rule 6 needs half of 6); smaller groups are marked where they were not.

A-1 4 4b | unclear | An owner-fixed figure with a unit; not a config key, since it is not overridden.
A-1 9 F | structural | The setting the live product reads is a config key; the address it holds is a value.
A-1 9 9b | structural | The setting the live product reads is a config key; the address it holds is a value.
A-1 13 K | unclear | An inbound payment notice is an event that starts a flow whose transition is in [2]; not a bare external, since it is our own flow.
A-1 13 F | unclear | An inbound payment notice is an event that starts a flow whose transition is in [2]; not a bare external, since it is our own flow.
A-1 13 13a | unclear | An inbound payment notice is an event that starts a flow whose transition is in [2]; not a bare external, since it is our own flow.
A-1 13 13b | unclear | An inbound payment notice is an event that starts a flow whose transition is in [2]; not a bare external, since it is our own flow.
A-1 15 15b | unclear | An invariant with an automatic check; rule, since no field holds it.
A-1 18 K | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A compact tile is a UI component shared by two places; no kind names components, and a view must serve a step, which does not fit.
A-1 18 18a | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A compact tile is a UI component shared by two places; no kind names components, and a view must serve a step, which does not fit.
A-1 18 18b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A compact tile is a UI component shared by two places; no kind names components, and a view must serve a step, which does not fit.
A-1 22 22d | unclear | An overridable setting is a config key; the default 15 minutes is the value it binds.
A-1 24 K | structural | The bike's fields are attrs; the fixed response shape other companies rely on is a rule.
A-2 4 4b | unclear | A fixed owner-set number, not a rule or a config key
A-2 9 F | structural | Environment-specific build fact, so software config_key; not product
A-2 9 9b | structural | Environment-specific build fact, so software config_key; not product
A-2 13 K | unclear | PayRight's notifier is an event that drives a transition, so a workflow started by event; not a rule
A-2 13 13a | unclear | PayRight's notifier is an event that drives a transition, so a workflow started by event; not a rule
A-2 13 13b | unclear | PayRight's notifier is an event that drives a transition, so a workflow started by event; not a rule
A-2 15 15b | unclear | Invariant that must always hold; rule with the check as proof
A-2 20 20b | unclear | The transport app is a program that calls us, so an actor; "we never ask it" is a rule
A-2 21 21b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Open owner question; the AI's own pick is a guess, which needs sets and a why
A-2 22 22d | unclear | Hosts may override the default, so it is config; 15 is the default value
A-2 24 K | structural | Fields of each bike in the fixed response of [10]; the fixed layout is a contract, carried by the attrs
A-3 4 4b | unclear | A figure the owner fixed with a unit; a value, not a config key, because nobody sets it per host.
A-3 9 F | structural | The address differs between trial and production and is read from the environment, so it is a config key bound to a value; not a pin, since no version is involved.
A-3 9 9b | structural | The address differs between trial and production and is read from the environment, so it is a config key bound to a value; not a pin, since no version is involved.
A-3 13 K | unclear | The notifier is an inbound event that drives a transition, so it is a workflow started by an event; the mark-paid work is a case with its effect and operation.
A-3 13 F | unclear | The notifier is an inbound event that drives a transition, so it is a workflow started by an event; the mark-paid work is a case with its effect and operation.
A-3 13 13a | unclear | The notifier is an inbound event that drives a transition, so it is a workflow started by an event; the mark-paid work is a case with its effect and operation.
A-3 13 13b | unclear | The notifier is an inbound event that drives a transition, so it is a workflow started by an event; the mark-paid work is a case with its effect and operation.
A-3 15 15b | unclear | A must-hold invariant; the check is recorded as proof, and no path is invented since none was given.
A-3 20 20b | unclear | A program that asks us for free bikes, so it is an actor (never an external); we never call it, so no link to outward calls.
A-3 22 22d | unclear | The owner's fixed figure is a value; the override is a config key bound to that value, since a host can change it.
A-3 24 K | structural | Bike data are attrs of the bike entity; the promise that other companies rely on is a rule about the response of [10].
A-4 2 2b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A hire is an entity with its own states and transitions. "Never backwards" is a rule over them, not a transition.
A-4 4 4b | unclear | A fixed figure the owner set. No entity owns it, so it is a value, not an attr.
A-4 9 F | structural | The address differs per deployment and is read from config, so config_key binds it to a value.
A-4 9 9b | structural | The address differs per deployment and is read from config, so config_key binds it to a value.
A-4 13 K | misled-by: external | The notifier is PayRight's server, outside us, so it is an external, not an actor. The event drives the paid transition.
A-4 13 13a | misled-by: external | The notifier is PayRight's server, outside us, so it is an external, not an actor. The event drives the paid transition.
A-4 13 13b | unclear | The notifier is PayRight's server, outside us, so it is an external, not an actor. The event drives the paid transition.
A-4 15 15b | unclear | A must-always-hold invariant is a rule. proof names the check; its path is not given, so it is left for the builder.
A-4 20 20b | unclear | The city's app uses us, so it is an actor. The one-way direction is a rule.
A-4 22 22d | unclear | An override set by the host, so a config_key bound to a value. The default 15 is that value.
A-4 24 K | structural | Layout of each bike's data. The command has no output field, so the fields belong on the bike entity that [10] returns.
A-5 4 4b | unclear | A fixed business figure the owner set, used as the threshold for the late fee; value, not config_key, because it is not a build setting.
A-5 9 9b | structural | A per-environment build setting; config_key binds a set.
A-5 13 K | unclear | The PayRight notifier is a trigger from outside that causes a transition; workflow started by an event.
A-5 13 13a | unclear | The PayRight notifier is a trigger from outside that causes a transition; workflow started by an event.
A-5 13 13b | unclear | The PayRight notifier is a trigger from outside that causes a transition; workflow started by an event.
A-5 20 20b | unclear | The city's transport app is a program that asks us for free bikes; actor, not external, since it is a user of the product.
A-5 22 22d | unclear | The business figure is a value; the override is a software config_key binding to it.
A-5 24 K | structural | The fields of each bike in the API reply, which the partners rely on; attrs since they are data.
A-6 4 4b | unclear | A fixed figure the owner set. Value holds a named number with a unit; it is not an attr since no hire owns it.
A-6 9 F | structural | The live product reads an environment setting, so config_key. Not a pin, since the address varies by environment.
A-6 9 9b | structural | The live product reads an environment setting, so config_key. Not a pin, since the address varies by environment.
A-6 13 K | unclear | Triggered by an outside message, so a workflow started by an event. The notifier is part of PayRight, [3]. Not a transition: the notifier is the trigger.
A-6 13 F | unclear | Triggered by an outside message, so a workflow started by an event. The notifier is part of PayRight, [3]. Not a transition: the notifier is the trigger.
A-6 13 13a | unclear | Triggered by an outside message, so a workflow started by an event. The notifier is part of PayRight, [3]. Not a transition: the notifier is the trigger.
A-6 13 13b | unclear | Triggered by an outside message, so a workflow started by an event. The notifier is part of PayRight, [3]. Not a transition: the notifier is the trigger.
A-6 15 15b | unclear | An invariant with an automatic check. Rule states it; proof is the check, which is not named yet.
A-6 20 20b | unclear | A program that calls us and that we never call, so an actor. Not external, since an external is never an actor.
A-6 22 22d | unclear | Fixed hold time, with an override a host can set. The value is the default; the config key is the override.
A-6 24 K | structural | A contract that other companies rely on: the response always has the same layout. A rule, since it is a fixed sentence about the endpoint.
B-1 4 4b | unclear | A figure the owner fixed once. It is not a setting, since nothing reads it from the environment.
B-1 12 12b | structural | Remarks are free text kept by the product, and a bike has many of them. Written by anyone, so no actor is restricted.
B-1 18 18a | structural | One tile shown in two places is one interface. It shows bike facts and is not two interfaces.
B-1 18 18b | structural | One tile shown in two places is one interface. It shows bike facts and is not two interfaces.
B-1 20 20b | unclear | A system that calls us, so it is an actor, not a dependency. We never call it, so no interface points to it.
B-1 21 21b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Unsettled, so a decision with a proposal the AI builds on until the owner answers.
B-1 22 22d | unclear | The owner's fixed figure is a quantity. HOLD_MINUTES is the host's override, so it is a setting whose default is that quantity.
B-2 13 13b | unclear | A program that calls us, so an actor. Its call marks the hire paid, which needs a new case and interface.
B-2 22 22d | unclear | The owner's figure is a quantity. The override by the host is a setting read from the environment.
B-2 24 K | structural | Other companies rely on the layout, and a test can check it, so a rule.
B-3 11 F | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Open question with options; not proposal, since nobody picked and the AI has no pick here; not answer, since nobody said yes
B-3 12 K | structural | Remarks are things many bikes carry, so entity; a text attribute on bike would hold only one
B-3 12 12b | structural | Remarks are things many bikes carry, so entity; a text attribute on bike would hold only one
B-3 18 18a | structural | One tile shown in two places, so one interface, not two; it serves no step (it shows only), so allows
B-3 18 18b | structural | One tile shown in two places, so one interface, not two; it serves no step (it shows only), so allows
B-4 4 4b | unclear | A decided number times a unit. Not a setting, because the owner fixed it rather than a file reading it.
B-4 13 13b | unclear | The notifier is a program that calls us, so it is an actor, not a dependency. The mark paid is an effect on the transition in [2].
B-4 18 18a | structural | One tile shown in two places is one interface. It is a screen the rider reaches, so it is an interface, not a component.
B-4 18 18b | structural | One tile shown in two places is one interface. It is a screen the rider reaches, so it is an interface, not a component.
B-4 22 22d | unclear | A knob the host can override through an environment variable, with the default decided by the owner. The default is a quantity, not the setting itself.
B-4 28 28a | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | An answer with when and where, which the owner gave. The sets null means the helmet rental entry does not exist.
B-5 4 4b | unclear | A decided number with a unit. Not a setting, because it is not a knob read from the environment.
B-5 13 13b | unclear | The notifier calls us, so it is an actor, not a dependency, which we call. The workflow starts from its event and fires the paid transition.
B-5 24 K | structural | Other companies rely on the layout, which a test can check. Not a principle, since a test verifies it.
B-6 4 4b | unclear | A number with a unit, decided once by the owner; not a setting, since nothing reads it at run time.
B-6 7 F | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Payment is a system process reached by steps, fired by a transition; the handler is the code unit that does the call.
B-6 12 K | structural | Remarks are many entries per bike that anyone creates, so an entity, not an attribute.
B-6 12 12b | structural | Remarks are many entries per bike that anyone creates, so an entity, not an attribute.
B-6 22 22d | unclear | The 15 minutes is a decided figure; HOLD_MINUTES is the override knob read from the environment.
B-6 24 K | structural | Other companies rely on it, so it is a rule a test can check.
C-1 4 4b | unclear | A number the owner decided once, so quantity.
C-1 7 K | structural | Our code acts at a moment, so a workflow with a tell effect to the dependency. Not a command, since no actor invokes it.
C-1 7 F | structural | Our code acts at a moment, so a workflow with a tell effect to the dependency. Not a command, since no actor invokes it.
C-1 7 7a | structural | Our code acts at a moment, so a workflow with a tell effect to the dependency. Not a command, since no actor invokes it.
C-1 7 7b | structural | Our code acts at a moment, so a workflow with a tell effect to the dependency. Not a command, since no actor invokes it.
C-1 12 12b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Each remark is an entity with text. A bike carries many, so many on the bike's attribute.
C-1 13 13b | unclear | A system that calls us is an actor, not a dependency. Marking paid is a workflow with a transition.
C-1 14 14d | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Worked out from other facts, so derived. Derived attributes have no max and are never optional.
C-1 15 15b | unclear | A must-hold invariant checked by a test. Rule, verified by proof.
C-1 20 20b | unclear | Calls us, so actor. We never call it, so it is not a dependency.
C-1 22 22d | unclear | The owner's decided 15 is a quantity. The host can override it, so the setting is the knob that defaults to it.
C-1 24 K | structural | The layout must always hold and a test can check it. Battery level is a measured reading, so attribute.
C-2 4 4b | unclear | A number the owner decided once, the longest hire without a late fee. Not a setting, which is read from a file or the environment.
C-2 15 15b | unclear | A checkable invariant, so a rule verified by a proof once its path is known. Not a principle.
C-2 19 19a | unclear | A known quirk of a dependency that we work around. It is forced by PayRight, not chosen, so it is a workaround and not a rule.
C-2 20 20b | unclear | It calls us, so it is an actor. We never call it, so it is not a dependency.
C-2 22 22d | unclear | A knob the host can override from the environment. The decided number it defaults to is a quantity.
C-2 24 K | structural | Other companies rely on the layout, so it is a checkable rule. Battery level is a measured reading, so it is an attribute.
C-3 4 4b | unclear | A figure the owner fixed once. Not an attribute, which would be a measured reading.
C-3 12 12b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A remark is a record many bikes can carry, so it needs an entity and a many attribute. Not an enum, because the text is open.
C-3 13 13b | unclear | A system that calls us is an actor, not a dependency. Its call is the event that starts the paid transition.
C-3 20 20b | unclear | The city's app asks us for bikes, so it is an actor. We never call it, so it is not a dependency.
C-3 22 22d | unclear | A setting is a knob the host can override. The quantity is the decided number the setting defaults to.
C-3 24 K | structural | A layout others rely on, so a checkable rule. Battery level is a reading, so an attribute, not a quantity.
C-4 7 F | structural | Our own code that performs the charge is a handler; the charge moment is a workflow started by a transition, not a schedule.
C-4 7 7b | structural | Our own code that performs the charge is a handler; the charge moment is a workflow started by a transition, not a schedule.
C-4 13 13b | unclear | PayRight's notifier calls us, so it is an actor, not a dependency; marking the hire paid is a workflow started by that event.
C-4 15 15a | unclear | A business invariant a check can read: rule, not principle; the proof field stays empty until the test path is known.
C-4 15 15b | unclear | A business invariant a check can read: rule, not principle; the proof field stays empty until the test path is known.
C-4 20 20b | unclear | A system that calls us is an actor; we never ask it anything, so it is not a dependency.
C-4 22 22d | unclear | The owner's fixed figure is a quantity; the host's override is a setting read from the environment.
C-4 24 K | structural | The two facts per bike are attributes; the fixed answer shape other companies rely on is a rule a check can read.
C-4 25 25a | unclear | A checked invariant of our own wish: rule, not principle; not PayRight's rule.
C-5 4 4b | unclear | A number the owner decided once; not a setting, since nothing reads it from the environment.
C-5 7 F | structural | A one-off task that starts at hand-back; the code that talks to PayRight is a handler, not a command.
C-5 7 7b | structural | A one-off task that starts at hand-back; the code that talks to PayRight is a handler, not a command.
C-5 13 13b | unclear | The notifier calls us, so it is an actor, not a dependency; marking paid is a workflow started by its contact.
C-5 15 15b | unclear | A business invariant that a check verifies; not a principle, since a test can check it.
C-5 19 K | unclear | Forced by PayRight rounding down, not chosen by us; a workaround, not a rule.
C-5 19 19a | unclear | Forced by PayRight rounding down, not chosen by us; a workaround, not a rule.
C-5 20 20b | unclear | A program that calls us; an actor, and we never call it, so no dependency.
C-5 22 22d | unclear | A decided number the setting defaults to; the setting is the knob a host can override.
C-5 24 K | structural | The response shape is an invariant, so a rule; code and battery level are facts kept per bike, and sort comes from [6].
C-6 4 4b | unclear | A figure the owner fixed, decided once. Not an attribute, since it is not measured per hire.
C-6 13 13b | unclear | The notifier calls us, so it is an actor, not a dependency. Marking paid is a workflow started by that event.
C-6 15 15b | unclear | A checked business invariant, so a rule. Not a principle, because a test can check it.
C-6 19 K | unclear | A known issue forced by the dependency, not chosen by us, so a workaround and not a rule.
C-6 19 19a | unclear | A known issue forced by the dependency, not chosen by us, so a workaround and not a rule.
C-6 20 20b | unclear | Calls us for free bikes, so an actor. We never call it, so it is not a dependency.
C-6 22 22d | unclear | A knob the host can override, with the 15-minute default applying when none is set. Not a quantity alone, since it is overridable.
C-6 24 K | structural | The response layout is a checked contract that other companies rely on. Code and battery are facts kept about bikes.
C0-1 13 K | unclear | PayRight's notice starts a workflow that marks the hire paid; a workflow, not a rule, because it is a sequence of steps.
C0-1 13 13a | unclear | PayRight's notice starts a workflow that marks the hire paid; a workflow, not a rule, because it is a sequence of steps.
C0-1 13 13b | unclear | PayRight's notice starts a workflow that marks the hire paid; a workflow, not a rule, because it is a sequence of steps.
C0-1 15 15b | unclear | A must-always-hold invariant with a check; a rule.
C0-1 20 20b | unclear | The transport app uses us, so an actor; the never-ask constraint is a product rule.
C0-1 22 22d | unclear | The host may override it, so a setting; the 15-minute figure is the owner's business fact, so the default is a quantity.
C0-1 24 K | structural | A promise other companies rely on, so a product rule; the exact layout is not a build decision.
C0-2 4 4b | unclear | A fixed owner figure that checks and fees read; quantity, not a setting.
C0-2 7 K | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A process with steps and outcomes, triggered by the return; not a rule, and PayRight is the dependency in [3].
C0-2 7 F | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A process with steps and outcomes, triggered by the return; not a rule, and PayRight is the dependency in [3].
C0-2 7 7a | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A process with steps and outcomes, triggered by the return; not a rule, and PayRight is the dependency in [3].
C0-2 7 7b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | A process with steps and outcomes, triggered by the return; not a rule, and PayRight is the dependency in [3].
C0-2 12 12b | unclear (not read one by one: fewer than 3 runs of the arm, below what rule 6 needs) | Notes written by mechanics, several per bike; many-valued attribute of the bike, not a separate entity.
C0-2 13 K | unclear | Triggered by an outside notice; a workflow started by an event.
C0-2 13 13a | unclear | Triggered by an outside notice; a workflow started by an event.
C0-2 13 13b | unclear | Triggered by an outside notice; a workflow started by an event.
C0-2 15 15b | unclear | An invariant with an automatic check; rule, not an attribute.
C0-2 20 20b | unclear | The city's own program that asks us; an actor, and never a target of our calls.
C0-2 22 22d | unclear | The business figure is a product quantity; the host override is a software setting that defaults to it.
C0-2 24 K | structural | Fields other companies rely on in the response; attributes of the bike, since the layout is fixed by the data.
C0-3 4 4b | unclear | Owner's business figure, so a product-layer quantity; not a setting, which is build config.
C0-3 13 K | unclear | PayRight's notifier is an outside event that drives a transition, so an event-started workflow; not a command, since PayRight contacts us.
C0-3 13 13a | unclear | PayRight's notifier is an outside event that drives a transition, so an event-started workflow; not a command, since PayRight contacts us.
C0-3 13 13b | unclear | PayRight's notifier is an outside event that drives a transition, so an event-started workflow; not a command, since PayRight contacts us.
C0-3 15 15b | unclear | An invariant the product must always hold, with an automatic check; a rule.
C0-3 19 19a | unclear | Compensation for PayRight rounding down; the workaround kind is for a dependency quirk.
C0-3 20 20b | unclear | The city's own app is an external program that calls us; an actor, not a dependency, since we never call it.
C0-3 22 22d | unclear | Owner's figure is a product quantity; the host override is a software setting whose default links to that quantity.
C0-3 24 K | structural | The layout is a rule other companies depend on; the listed fields are attributes of bike.
C0-3 25 25a | unclear | Our own invariant, with an automatic check, that the product must always hold; a rule, not a PayRight fact.
C0-4 4 4b | unclear | A single owner-fixed figure that other facts read; a quantity, not a build setting.
C0-4 13 K | structural | PayRight's notifier is part of the PayRight dependency, not an actor; its arrival is the event that marks the hire paid.
C0-4 13 F | structural | PayRight's notifier is part of the PayRight dependency, not an actor; its arrival is the event that marks the hire paid.
C0-4 13 13a | structural | PayRight's notifier is part of the PayRight dependency, not an actor; its arrival is the event that marks the hire paid.
C0-4 13 13b | structural | PayRight's notifier is part of the PayRight dependency, not an actor; its arrival is the event that marks the hire paid.
C0-4 15 15a | unclear | An invariant that must always hold; a rule, with the check to be linked as proof later.
C0-4 19 K | unclear | A workaround for a known defect in a dependency; the workaround kind exists for exactly this.
C0-4 19 19a | unclear | A workaround for a known defect in a dependency; the workaround kind exists for exactly this.
C0-4 20 20b | unclear | A program that uses the product by asking us; we never call it, so it is not a dependency.
C0-4 22 22d | unclear | The hold length is a figure with a host override, so a setting whose default is the quantity.
C0-4 24 K | structural | A fixed contract others rely on, so a rule; battery level is a new bike field the reply needs.
C0-4 25 25a | unclear | An owner-set check on our own payment code, stricter than PayRight allows.
C0-5 4 4b | unclear | A business figure the owner fixed; quantity holds number and unit; not a setting, because it is not a build fact.
C0-5 13 K | unclear | PayRight's notifier is their server, so not an actor; our side that reacts to it is a handler, and the mark-paid is the transition event.
C0-5 13 F | unclear | PayRight's notifier is their server, so not an actor; our side that reacts to it is a handler, and the mark-paid is the transition event.
C0-5 13 13a | unclear | PayRight's notifier is their server, so not an actor; our side that reacts to it is a handler, and the mark-paid is the transition event.
C0-5 13 13b | unclear | PayRight's notifier is their server, so not an actor; our side that reacts to it is a handler, and the mark-paid is the transition event.
C0-5 15 15a | unclear | A constraint across hires, not a single transition, so a rule; proof left empty because the check's path is unknown.
C0-5 15 15b | unclear | A constraint across hires, not a single transition, so a rule; proof left empty because the check's path is unknown.
C0-5 20 20b | unclear | The city's own app uses the product, so it is an actor; not a dependency, since we never call it.
C0-5 22 22d | unclear | The owner's figure is a business quantity; the override is a build setting whose default points at it.
C0-5 24 K | structural | Other companies rely on a fixed shape, so a rule that is concluded from [10]; the battery level is a new bike attribute.
C0-5 25 25a | unclear | Our own invariant beyond PayRight's behaviour; a rule, with proof left empty as in [15].
C0-6 13 13b | unclear | Starts from an outside event, so a workflow with event. The notifier calls us, so it is an actor, not a dependency.
C0-6 15 15b | unclear | An invariant across hires, so rule. Not a state, since it spans several hires.
C0-6 19 K | unclear | Compensates for a dependency's behaviour, so workaround. Not a rule, since it is a fix for an outside flaw.
C0-6 19 19a | unclear | Compensates for a dependency's behaviour, so workaround. Not a rule, since it is a fix for an outside flaw.
C0-6 22 22c | unclear | Owner figure is a quantity. The per-host override is a software setting.
C0-6 22 22d | unclear | Owner figure is a quantity. The per-host override is a software setting.
C0-6 24 K | structural | The fixed layout other companies rely on. Attributes name the fields, the rule states the contract.

| name | arm | fact | runs blamed of runs in the arm |
|---|---|---|---|
| external | A | 13 | 1 of 6 |

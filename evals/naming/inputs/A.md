You are modelling a product in a requirements knowledge base you have not seen before. Everything you may use is in
this message: the map of kinds, the glossary, and the exercise. Read no file, run no command, search nothing.
Write your answer, the one table the exercise asks for, to the output path given to you. Reply only "done".

## Map of kinds

! required, -> one link, ->> many links (an expression: the links it reads), [] a list part, (a|b) enum members, indentation = part of; every kind also takes title, src, because, by, proof, agreed
product and software:
  actor: !says !nature(human|ai|program)
  area: !says distinct
  decision: !question structure context
    answer[]: !chose->option !said !at !where note delegated->decision
    guess: chose->option sets !why
      heard: !said
    option: !label sets
  entity: !says
    attr: says !type(text|number|flag|money|date|time|duration|one|list) of->set|entity max->value optional derived->>value|set|entity|attr|state|external|config_key|actor
    state: !says
    transition: from->>state !to->state
  rule: !says
  set: !says !members
  term: !word !says avoid
  value: !says !is !unit
  workflow: !says schedule->value event->transition !start->step realizes->capability
    end: !says !result(success|failure)
    step: says actor->actor calls->workflow
      case: order when->>value|set|entity|attr|state|external|config_key|actor covers_ends->>end !then->step|end|workflow
        effect[]: !do(transition|create|delete|write|tell) !on->transition|entity|attr|actor|external
      choice: !label when->>value|set|entity|attr|state|external|config_key|actor !then->step|end|workflow
        effect[]: as above
      timeout: !after->value !then->step|end|workflow
        effect[]: as above
product:
  capability: !says serves->>goal
  goal: !says for->>actor
software:
  command: !says !invoked_as !serves->>step offers->>choice
  config_key: !says !name binds->value|set
  external: !says pin
    deviation: !when->>value|external !says
  operation: !says performs->>choice|case|timeout uses->>external
  view: !says !serves->>step offers->>choice
constitution/ (fixed folder):
  principle: !says why
rules:
  attr: an attribute of type one names what it holds
  attr: a derived attribute has no max and is never optional
  case, choice, timeout: a row with an effect has an operation performing it
  effect: a transition effect names a transition
  effect: a create or delete effect names an entity
  effect: a write effect names our own entity or an attribute that is not derived; an external is told
  effect: a tell effect names an actor or an external
  guess: exactly one of chose, sets
  step: an actor step has a view or command that serves it
  step: an actor step offers at least one choice without `when`
  workflow (flow): an actor step offers choices (maybe a timeout) and nothing else; a system step has cases or one `then`; a calling step continues by cases
  workflow (flow): a system step has one `otherwise` case without `when`; every other case has `when` and its own `order`
  workflow (flow): every step is reached from `start` and reaches an end or a hand-off; every end is reached
  workflow (flow): a calling step names every end of its callee in `covers_ends`
  workflow (flow): the views and commands serving a step offer every choice between them
  workflow (flow): every workflow is started: an actor on its first step, a schedule or event, or led to from a started workflow

## Glossary

constitution (every decision is judged against these):
  intuitive-for-ai: The ontology is designed to be intuitive for AI agents: an agent reading the kinds, the glossary and one entry can tell what it means, where it goes and what it links to, without hidden conventions.
  layers-split-business-from-technical: What the business decides is kept apart from how it is built: a business fact lives in the product layer, a build fact in the software layer.
  rigid-where-checked: A fact that a check, work left or impact reads is a field or a link; a fact only a reader needs is text on its entry.
    why: An all-rigid model grows as detailed as code and lags behind it; text that a check needs is a second, unchecked spec. Each fact takes the cheapest form that still lets the checks read it.
  storage-is-a-projection: The ontology is a graph of linked entries. How an entry is stored (its own file, an item in a list, inline in its parent) is a projection: no meaning and no address depends on it.

product/shared:
  actor: Who uses or operates the product: human, ai or program; never an external.
    avoid: persona; role; user
  address: An entry's name, <layer>/<area>/<kind>/<id>, not its file path; links hold one.
  agreement: A person's yes to an entry's sentence, kept with its fingerprint; only people agree.
    avoid: standing; ratified; stale; signed; sign
  answer: The option the owner or a delegated agent chose for a decision; newest wins.
    avoid: ratified
  area: A topic folder in one layer, never named like the product; not a kind.
    avoid: subject; product axis
  because: Links to the entries a sentence was concluded from; the chain must reach evidence.
  card: One numbered item of a review round: a question or a sentence to agree.
  constitution: The fixed folder constitution/: every principle, printed whole to every agent first.
  decision: One question with its options, guess and answers; a tracker only mirrors it.
    avoid: settles; ?open
  entry: One item of a kind with a permanent id; one file may hold many.
  evidence: What grounds an entry: src, a decision, a person's yes or because; not proof.
  fingerprint: Hash of an entry's meaning fields, without notes and src; not a commit hash.
  guess: The option or values the AI builds on until the owner answers a decision.
    avoid: assumed; ?assumed
  harm tag: A kind's label for what a wrong sentence costs; it orders review, blocks nothing.
  id: An entry's permanent name in its kind and area, never reused; unlike its title.
    avoid: slug
  kind: A sort of entry; its file lists fields, links, checks; not a field type.
  layer: Top folder holding areas: product (what, why) or software (how it is built).
  null: In an option's sets, an address set to null: that entry does not exist.
    avoid: scope; rejected; non_goal; disposal
  ontology: Kind files saying what entries may be; not the knowledge base, not a plugin.
    avoid: schema
  part: An entry inside its parent's file, addressed <parent>/<kind>/<key>: a step, an option.
  principle: A statement decisions are judged against and cite; the owner calls them values.
    avoid: value-as-principle
  question: A decision with no answer yet; not an entry's state, not a card.
    avoid: ?open; open question
  read-back: Entries played back as said, concluded, guessed; neither a summary nor a review round.
  removed ledger: An area's append-only removed.yml: each removed entry's snapshot; its id is never reused.
    avoid: tombstone; retired
  review round: The cards one ogy review showed, kept so ogy reply answers exactly them.
  src: A sentence's code: or doc: link; not authority, not a decision, outside the fingerprint.
    avoid: origin; provenance
  term: A glossary word with its line and words to avoid; the owner agrees each.
  work left: Still to build: changed fingerprints or dependencies, missing proofs; not a task list.
software/shared:
  built record: Tool-written files under built/: each entry's built hash; never in entries, never hand-edited.
    avoid: meta; receipts inside entries
  proof: A test, path.py::function, showing a rule or value holds in code; not evidence.
  software ontology: ogy's shipped ontology for software, named in ogy.yml; never copied, no plugin, not requirements-only.
    avoid: v5; requirements ontology
software/ontology:
  shape: How a kind is stored: entity, list, single or inline; not its fields.

# Exercise: a web shop

Below is a small web shop in its owner's words, as numbered facts. Above this text you were given the map of kinds
and the glossary of a requirements knowledge base. You have nothing else: do not read files, do not search.

Each fact has one home in the knowledge base. For each fact say where you would write it.

## Facts

- [1] Shipping is free when the basket comes to 50 euros or more.
- [2] An order comes in through exactly one of three channels: the website, the mobile app, or by phone. There are no
  others.
- [3] We keep every order. An order is first placed, then paid, then shipped. It never goes backwards.
- [4] For every order we keep its total, in money.
- [5] We take card payments through PayRight, a payment company we do not own. We stay on its API version 2024-06 on
  purpose.
- [6] PayRight sometimes sends the same "paid" notice twice. We ignore a notice for an order that is already paid.
- [7] PayRight's URL differs between test and production. The running program reads it from `PAYRIGHT_URL`.
- [8] Two sorts of people do things in the shop: a shopper buys, an admin ships orders.
- [9] PayRight's notifier is a program that calls us when a payment went through. That call is what makes us mark the
  order paid.
- [10] A shopper whose account is locked cannot check out: checkout stops and tells them why.
- [11] A compact product tile (picture, name, price) appears on the cart page and on the "my orders" page. It is one
  tile, not two.
- [12] Other programs can ask us over HTTP, `GET /products/{id}`, and get back the product's name and price. Nothing
  changes when they ask.
- [13] One piece of our code charges the card: it talks to PayRight when the shopper confirms the order.
- [14] An order's total is never negative. A test can check this.
- [15] The owner holds one thing above all: checkout must feel fast. Every later design call is weighed against it.
- [16] Not settled yet: may a shopper buy without an account? Two ways are on the table: guest checkout, or an account
  is required. Nobody has picked.
- [17] Every night the shop itself deletes abandoned baskets.

## Your output

One Markdown table, one line per fact, in order, and nothing else:

| fact | kind | links | why |
|---|---|---|---|

- **kind**: the exact name from the map. For something written inside another entry, write `parent > part`. If a fact
  needs several entries of one kind, say how many. If no kind fits, write `none`.
- **links**: each link as `field -> [n]` (another fact) or `field -> new: <what>` (an entry the facts imply but do
  not list). Use the map's field names. Also name here a required field that carries the fact (for example a version
  or a name). Write `-` when there is none.
- **why**: one line: why this kind, and why not the nearest other kind you considered.


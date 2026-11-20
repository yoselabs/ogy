# Exercise: a bike hire

Below is a small bike hire service in its owner's words, as numbered facts. Above this text you were given the map of
kinds and the glossary of a requirements knowledge base. You have nothing else: do not read files, do not search.

For each fact say where you would write it. Most facts need one entry; a fact may need more than one, also entries
the facts imply but do not list.

## Facts

- [1] Two sorts of people act in the product: a rider hires bikes, a mechanic repairs them.
- [2] We keep every hire. A hire is first booked, then out, then returned, then paid. It never goes backwards.
- [3] We take card payments through PayRight, another firm, which handles the payments. We stay on its version
  2024-06 on purpose.
- [4] The owner fixed one figure: 12 hours, the longest a hire lasts without a late fee.
- [5] For every hire we keep how long it lasted, in minutes.
- [6] A bike is exactly one of three sorts: city, cargo or electric. There are no others.
- [7] One piece of our own code takes the payment: it talks to PayRight at the moment the rider hands the bike back.
- [8] The owner puts this above all: a charge never comes as a surprise to a rider. All later work on the product
  is weighed against it.
- [9] PayRight's address differs between trial and production. The live product reads it from `PAYRIGHT_URL`.
- [10] Other companies' apps can ask us over HTTP, `GET /stations/{id}/bikes`, and get back the free bikes of a
  station. Asking alters nothing.
- [11] Not settled yet: may a rider hold two bikes at once? Two possibilities are on the table: one bike only, or up
  to two. No one has picked.
- [12] Mechanics stick remarks on a bike, for example "squeaky" or "new saddle". Anyone can write a new one whenever
  they like, and a bike can carry several.
- [13] PayRight's notifier is a server of theirs that contacts us once a payment went through. That message is what
  makes us mark the hire paid.
- [14] For every hire we keep what it cost: an amount together with its currency. It is worked out from how long the
  hire lasted ([5]) and the late fee ([17]).
- [15] It must always hold: a bike is never out on two hires at once. We have an automatic check for it.
- [16] We measure the distance between two stations with a function from geolib, an open-source library written
  elsewhere. We stay on its version 3 on purpose.
- [17] Every hour beyond the 12 of [4] costs the rider 5 euros. The owner picked that figure.
- [18] A compact bike tile (photo, sort, price per hour) appears twice: beside the map and in the rider's list of
  past hires. It is one tile, not two.
- [19] PayRight rounds an amount down to whole cents, against its own documentation. So we add half a cent before
  sending.
- [20] The city's transport app belongs to the city. It asks us for free bikes through [10]. We never ask it
  anything.
- [21] Also not settled with the owner: what does a hire cost when the bike breaks down mid-ride? Two possibilities:
  it costs nothing, or it costs the minutes ridden. Until the owner speaks, the AI working on the product goes with
  "it costs nothing" and flags that as its own pick.
- [22] A booking is held for 15 minutes; the owner picked that figure. Whoever hosts the product can override it
  through `HOLD_MINUTES`; with no override, the 15 applies.
- [23] The whole point of the product: a rider finds a free bike within five minutes' walk.
- [24] What [10] sends back is always laid out the same: for each bike its code, its sort and its battery level. The
  other companies rely on it.
- [25] It must always hold: no payment is taken from a card that runs out within a month. We have an automatic check
  for it. This one is our own wish; PayRight would take such a card.
- [26] Toward [23], one ability of the product, leaving open how it gets made: finding free bikes near a spot.
- [27] For every station we keep the tally of bikes standing free there at the moment.
- [28] Settled: we do not rent out helmets. The owner picked that over "helmets for a fee", on 3 March, on the phone.

## Your output

One Markdown table, one line per fact, in order, and nothing else:

| fact | kind | links | why |
|---|---|---|---|

- **fact**: the number in brackets, `[1]` to `[28]`, each exactly once.
- **kind**: the exact name from the map. For something written inside another entry, write `parent > part`. If a fact
  needs several entries, name each, with how many. If no kind fits, write `none`.
- **links**: every link and every filled field the fact needs, separated by `;`. A link is `field -> [n]` (another
  fact) or `field -> new: <kind> <what>` (an entry the facts imply but do not list). A filled field is
  `field: <what>` (for example a version or a name). Use the map's field names. Write `-` when there is none.
- **why**: one line: why this kind, and why not the nearest other kind you considered.

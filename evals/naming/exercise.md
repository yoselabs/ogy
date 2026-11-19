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

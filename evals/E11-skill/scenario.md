# Scenario: community food bank deliveries (owner's words, transcribed)

[1] We're a food bank. [2] Families in the area sign up in our web app, and every week they can order a food box for home delivery. [3] Orders open on Monday and close Wednesday at noon. [4] Each family can order one box a week; families with more than four people get the large box. [5] After the cutoff, the system adds up all the orders and sends the packing list to the warehouse tablet, that's an iPad in the warehouse that the packers use. [6] The packers tick off each box as they pack it.

[7] Deliveries are on Saturday. [8] Our volunteer drivers sign up for a route in the app by Friday evening, and a coordinator, usually Priya, assigns the routes. [9] Each route has up to twelve stops. [10] On Saturday morning the driver opens the driver app on their phone, sees their stops in order, and taps "delivered" at each door, or "nobody home". [11] If nobody's home, the box comes back to the warehouse and the family gets a text asking if they want to pick it up instead. [12] Texts go through Twilio. [13] Families also get a text on Friday saying roughly when to expect us.

[14] We count stock in the warehouse app: every delivery from our suppliers gets scanned in, and every packed box takes its items out. [15] If we're short on something, the packing list swaps it for something from the same food group. [16] When stock of anything drops under two weeks of boxes, Priya gets an email so she can order more.

[17] People can also donate money on the website, through Stripe, and we send a thank-you email with a tax receipt. [18] Big donors, over five hundred, get a call from our director.

[19] Families have to renew their eligibility every six months by uploading a proof of address; a volunteer checks it. [20] If it lapses, they can't order until it's renewed.

[21] Every night at two the system makes a backup and sends a summary to the board: orders, deliveries, donations.

[22] We want it to be reliable more than fancy. [23] Some of our drivers are older and not great with phones, and the warehouse wifi is, honestly, patchy.

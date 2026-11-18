# Scenario: meeting rooms (owner's words)

We run a coworking space. Members book meeting rooms through our app. A member picks a room and a time slot and says
how many people will attend. If the room is free, we hold it and ask the member to pay through Stripe. Once Stripe
confirms, the booking is confirmed and we text the member a door code through our SMS provider; the door lock system
(Kisi) gets the code too. Bigger rooms need the community host to approve the booking first. Members can cancel; if
they cancel late, we charge a late fee. Members on the premium plan use credits instead of paying; credits are deducted
when the booking is confirmed. After the meeting, the cleaner gets the room ready. Members should be able to see their
usage history. A booking can be pending payment, confirmed, cancelled or finished. Members can add a note to a booking
for the host.

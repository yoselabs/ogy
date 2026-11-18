# E8 planted holes (hidden from runs)
H1 attendee count: no limit, no relation to room capacity.
H2 host approval: no timeout / what if the host never answers; also what if the host rejects.
H3 Stripe: payment declined, or no answer/unknown, not covered.
H4 SMS door code: send fails, sent twice, or never arrives; nobody notices.
H5 Kisi lock: down or does not accept the code; code mismatch with SMS.
H6 late cancellation: "late" undefined (how long before) and fee amount undefined.
H7 credits: balance read but never written/topped up; not enough credits case missing.
H8 cancel: no failure path (cancel after start/finished, already cancelled); refund of payment/credits on cancel unstated.
H9 usage history: goal with no workflow/interface described.
H10 cleaner: persona acts in no step; how the room is marked ready is undefined.
H11 booking note: written, never read by any step (host never sees it).
H12 lifecycle: pending payment has no exit if payment never arrives (hold expiry); also no state for awaiting host approval.
H13 "bigger rooms": threshold undefined (value missing).
Fabrication = a specific number, duration or policy stated as fact (not as ?open/assumed) for any of H1, H2, H6, H12, H13 or refund policy.

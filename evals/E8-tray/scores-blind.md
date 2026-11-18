# E8 blind scores

| run | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 | H10 | H11 | H12 | H13 | noticed | fabricated | misfiled | questions | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r01 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 28 | clean; all values ?open with no assumed numbers |
| r02 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 19 | clean |
| r03 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 22 | clean |
| r04 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 26 | clean |
| r05 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 22 | clean |
| r06 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 1 | 0 | 23 | fab: booking.attendees "?max: room capacity" given as plain value (asked elsewhere) |
| r07 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 12 | 1 | 0 | 21 | fab: attendees max = value/big_room_capacity as fact; attendee-vs-capacity limit never asked |
| r08 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 12 | 0 | 0 | 20 | Stripe "failed -> refused" modelled silently, no question or ?open on decline/no answer |
| r09 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 1 | 0 | 21 | fab: attendees <= room.capacity as plain guard/attr/input limit (owner question still asked) |
| r10 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 26 | clean |
| r11 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 12 | 0 | 0 | 23 | assumed 30 min hold / 24 h late window inside ?open (not fab); attendee limit never raised |
| r12 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 1 | 0 | 28 | fab: booking.attendees "?max: room capacity" plain (rule itself is ?open) |
| r13 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 28 | clean |
| r14 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 0 | 0 | 20 | clean (invented room ready/needs_cleaning lifecycle, outside key fab list) |
| r15 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 13 | 1 | 1 | 25 | fab: attendees max room.capacity plain; misfiled: premium_member as a persona (plan attribute) |

## Per-hole (runs of 15 that noticed)

| H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | H9 | H10 | H11 | H12 | H13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | 15 | 14 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |

> **FICTITIOUS DOCUMENT — MADE-UP DATA FOR DEMO PURPOSES ONLY.** Plan names, figures, codes and approvals are illustrative and do not reflect any real plan or member.

# Pharmacy Benefits Outreach Script — Outbound Member Education

| Field | Value |
|---|---|
| Document ID | PHARM-OUTREACH-SCRIPT |
| Version | 1.7 |
| Owner | Member Outreach Operations |
| Author | Marcus Lee, Outreach Program Lead |
| Knowledge base | Pharmacy; Insurance |
| Audience | Outreach advocates (outbound calls) |
| Effective date | 2025-11-15 |
| Plan year | 2026 |
| Legal approval | LGL-2025-104 (approved 2025-10-28) |
| Review cycle | Annual |

---

## 1. Purpose

This script supports outbound education calls to members enrolled in Sample Health Plan MAPD and PDP plans. Typical campaigns include new-member pharmacy onboarding, mail-order promotion, and reminders about lower-cost pharmacy options.

Outreach advocates provide general benefit education only. Do not give clinical advice or recommend specific medications.

Lines marked **[VERBATIM – LEGAL]** must be read word for word.

---

## 2. Opening (outbound)

"Hello, this is [Advocate first name] calling from Sample Health Plan. I'm reaching out to help you get the most from your prescription drug benefits. Am I speaking with [Member full name]?"

*Guidance:* If someone other than the member answers, do not share the reason for the call. Ask for a good time to call back, or leave the voicemail in Section 3.

---

## 3. Voicemail script

**[VERBATIM – LEGAL]**
"Hello, this is Sample Health Plan calling with information about your prescription drug benefits. This is not a sales call. Please call us back at the number on the back of your member ID card. TTY users can call 711."

*Guidance:* Do not leave the member's name, drug names, or any health information in a voicemail.

---

## 4. Identity verification

**[VERBATIM – LEGAL]**
"Before we continue, I need to verify your identity to protect your health information. Please tell me your full name, your date of birth, and the member ID number shown on your Sample Health Plan card."

*Guidance:* Verify all three items. If verification fails, end the call politely and mark disposition `OUT-NOVER`.

---

## 5. Recording disclosure

**[VERBATIM – LEGAL]**
"Please be aware this call may be monitored or recorded for quality purposes."

---

## 6. Reason for the call

"I'm calling to share a few ways you may be able to save on your prescriptions this year. Do you have a few minutes?"

*Guidance:* If the member says no, offer to call back and record a preferred time. If the member asks to stop receiving calls, follow Section 14.

---

## 7. Pricing disclaimer

**[VERBATIM – LEGAL]**
"Please note that your costs may vary based on your plan and the pharmacy you use. Prices and coverage are subject to change."

*Guidance:* Read before discussing any cost.

---

## 8. Drug tiers

"Your plan groups covered drugs into tiers. Drugs in lower tiers generally cost less."

*Guidance:* Illustrative 2026 copays at a preferred retail pharmacy, 30-day supply. Confirm the member's plan before quoting.

| Tier | Name | Illustrative copay (preferred retail, 30-day) |
|---|---|---|
| 1 | Preferred Generic | $0 |
| 2 | Generic | $5 |
| 3 | Preferred Brand | $45 |
| 4 | Non-Preferred Drug | 40% coinsurance |
| 5 | Specialty | 25% coinsurance |

---

## 9. Generic drugs

"Generic drugs contain the same active ingredients as brand-name drugs and are FDA-approved. They often cost much less."

*Guidance:* If the member asks about switching, suggest they talk with their doctor or pharmacist.

---

## 10. Mail-order pharmacy (campaign focus)

"Have you heard about our mail-order pharmacy, SampleRx Mail Pharmacy? It's an easy way to get the medicines you take regularly delivered to your home."

Key points:
- "You can get up to a 90-day supply."
- "Standard shipping is free."
- "Many members pay less for a 90-day supply by mail than at a retail pharmacy."

*Guidance:* Mail-order deliveries arrive within **7 to 10 business days**. Recommend the member order refills when they have about 21 days of medicine left. If the member wants to enroll, warm transfer to SampleRx Mail Pharmacy and mark disposition `OUT-MAIL-XFER`.

---

## 11. Preferred pharmacies

"You can also save by using a preferred retail pharmacy in our network."

*Guidance:* Preferred pharmacy copays apply at all in-network retail pharmacies. Use the pharmacy locator in the member portal to help the member find a convenient location.

---

## 12. Drug payment stages

"Your costs can change during the year depending on which drug payment stage you are in."

*Guidance:* Explain briefly:

1. **Deductible:** The member pays full cost for some drugs until the deductible is met.
2. **Initial coverage:** The member pays a copay or coinsurance.
3. **Coverage gap ("donut hole"):** After total drug costs reach a set amount, the member may pay a higher share of costs until reaching the catastrophic threshold.
4. **Catastrophic coverage:** After out-of-pocket costs reach the annual limit (**$2,000, illustrative**), the member pays $0 for covered drugs for the rest of the year.

---

## 13. Premium and billing questions

*Guidance:* Outreach advocates do not discuss premium amounts, billing, or payment issues. If the member raises them, say: "I can connect you with our billing team, who can help with that," and transfer to Insurance / Billing Services. Mark disposition `OUT-BILL-XFER`.

If the member has a late-premium notice, do not discuss disenrollment. Transfer to Insurance / Billing Services.

---

## 14. Do-not-call requests

**[VERBATIM – LEGAL]**
"I understand. I will add your number to our do-not-call list for outreach calls. Please allow up to 30 days for this change to take effect. You will still receive calls about your claims, appointments, or other plan business when needed."

*Guidance:* Mark disposition `OUT-DNC` and submit the DNC request in the outreach tool before ending the call.

---

## 15. Closing

"Is there anything else I can help you with today?"

**[VERBATIM – LEGAL]**
"Thank you for your time. If you have any questions about your prescription coverage, call the number on the back of your member ID card. TTY users can call 711. We're available 8 a.m. to 8 p.m., seven days a week."

---

## 16. Disposition codes

| Code | Meaning |
|---|---|
| `OUT-EDU` | Education completed |
| `OUT-MAIL-XFER` | Transferred to mail order |
| `OUT-BILL-XFER` | Transferred to billing |
| `OUT-CB` | Callback scheduled |
| `OUT-DNC` | Do-not-call requested |
| `OUT-NOVER` | Verification failed |
| `OUT-VM` | Voicemail left |

---

## 17. Revision history

| Version | Date | Change | Approved by |
|---|---|---|---|
| 1.7 | 2025-10-28 | Updated 2026 copays and out-of-pocket limit | Legal (LGL-2025-104) |
| 1.6 | 2024-10-15 | Added do-not-call language | Legal (LGL-2024-088) |
| 1.5 | 2023-11-01 | Added mail-order campaign section | Legal (LGL-2023-062) |

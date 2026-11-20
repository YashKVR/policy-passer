import type { Check, CheckSummary } from "./types";

export const queue: CheckSummary[] = [
  {
    id: "CHK-1001",
    title: "Maya Chen, emergency treatment",
    status: "waiting",
  },
  {
    id: "CHK-1002",
    title: "Luis Ortega, emergency treatment",
    status: "waiting",
  },
  { id: "CHK-1003", title: "Jordan Lee, baggage theft", status: "decided" },
];

export const decidedCheck: Check = {
  id: "CHK-1003",
  title: "Jordan Lee, baggage theft",
  status: "decided",
  policy_copy:
    "Baggage. A theft of baggage is covered when a police report is filed within 24 hours.",
  claim_papers:
    "Traveler: Jordan Lee. Loss: baggage theft of $300.00. No police report is attached.",
  outcome: "rejected",
  explanation:
    "The baggage section requires a police report within 24 hours for a theft. The papers do not include that report for the $300.00 loss. The claim would be rejected.",
  policy_section: "Baggage",
  mistakes: [
    {
      mistake: "No police report for a theft of $300.00",
      reason: "The policy requires a police report filed within 24 hours.",
    },
  ],
};

export const instructions =
  "Do not submit the papers.\nDecide only from that policy copy.\n";

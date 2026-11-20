# The claims pilot

From the head of claims operations at Policy Passer.

## How claims work today

Someone gathers a policy copy and the claim papers, then submits them. They only learn afterwards whether the claim is approved or rejected. When it is rejected, the reason is often unclear, and the mistakes in the papers are easy to miss until the insurer sends them back.

## The pilot

We want Policy Passer to check a policy copy and the claim papers before they are submitted. For each check it should:

- read the policy copy and the claim papers
- say whether submitting those papers would get the claim approved
- when it would not, name the mistakes in the papers
- explain why the claim would be rejected, in two or three sentences, along with the part of the policy the decision rests on

Our goal is to catch a rejection before the papers are submitted, and to make the mistakes and the reason plain.

## What the team needs to see

- Each check, with where it stands: waiting, in progress or decided.
- The policy copy and the claim papers that were checked.
- The outcome: approved, or rejected.
- The mistakes, and why each one would cause a rejection.
- What Policy Passer is doing on a check while it works, step by step.
- The instructions it follows, read only.

## Rules

- The check happens before submission. Policy Passer does not submit the papers.
- The decision follows the policy copy that was provided.
- A rejection must name the mistakes and explain why the claim would be rejected.
- An approval must say the papers are ready to submit.
- Known outcomes used to check Policy Passer's work stay out of the check. Policy Passer must never see them.

## Our records

Policy copies and claim papers live in `data/`, described in `data/README.md`. Held-out examples used to check Policy Passer later stay out of the checks it works.

## Not for now

- No submission of the papers to an insurer.
- No rewriting or fixing the papers. The pilot reports the mistakes and the reason.
- No sign-in. Everyone who uses the screens sees everything.
- No messages to the person who supplied the papers.

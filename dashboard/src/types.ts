export type CheckSummary = {
  id: string;
  title: string;
  status: string;
};

export type Mistake = {
  mistake: string;
  reason: string;
};

export type Check = CheckSummary & {
  policy_copy: string;
  claim_papers: string;
  outcome: string;
  explanation: string;
  policy_section: string;
  mistakes: Mistake[];
};

export type Step = {
  message: string;
};

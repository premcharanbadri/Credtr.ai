# Interview defense | 15 questions a tough Capital One interviewer may ask

1. Why is 30+ DPD within 60 days the right target? What is the relationship to actual default and write-off?
2. How do you ensure future payment events do not contaminate the training features?
3. Why is a temporal holdout better than a random split for monthly operational monitoring?
4. Are repeated synthetic account snapshots independent? How would you account for within-account dependence in confidence intervals?
5. What is the interpretation of ROC AUC versus PR AUC? Which matters at fixed outreach capacity?
6. What does Brier score tell you about the quality of probabilities used in financial calculations?
7. Why calibrate on a disjoint chronological period and not on training data?
8. What if a complex model adds only a minor improvement over logistic regression?
9. How do you distinguish elevated risk correlation from the causal benefit of outreach?
10. Why might top-risk selection generate less value than risk/exposure value ranking?
11. What if your credit-risk model has uneven errors among legally protected groups?
12. Why should a certain high-risk account be excluded from the outreach plan?
13. What is the difference between a hypothetical expected loss proxy and reported credit loss savings?
14. What leadership decision would you make if the model beats baseline but the pilot ROI is negative?
15. What is the simplest alternative to AI that you should try before deployment?

## Strong answer pattern
Frame the decision -> state hypotheses -> quantify baseline -> compare alternatives -> name assumptions -> communicate risks -> define trial -> measure results -> scale/stop. Do not manufacture production outcomes or ownership of client approvals.

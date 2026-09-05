# Three Questions Answered, From The Annotated Report Of 2026-09-05

2026-09-05, Saturday, 13:21 BST.

These 3 questions were asked in the annotated document at 01:25 and never answered. They appear on the outstanding list wrongly classified as decisions awaiting the founder. They are not decisions. They are questions to me, and here are the answers.


## Question 1. Was The Mathematical Model Refuted, Or Was My Test Of It Refuted?

My test was refuted. The model was not.

The distinction matters and the earlier report blurred it. What happened is this. The mathematical appendix contained many sentences claiming something had been checked with symbolic algebra, and almost nothing in the test suite actually performed those checks. I wrote a module to execute them. Two reviewers then found that 3 of my 15 assertions were empty: they subtracted an expression from itself, which gives 0 for any expression whatsoever, so they would have passed with the model replaced by the number 42. That is a defect in my test, not in the model.

The model itself has survived every check made of it since, including checks it did not previously have. What was refuted in the appendix was 2 pieces of surrounding prose, not the mathematics: a stated justification for a constraint on coupling constants, which is false, and a reduction row missing its condition. Both are now corrected.


## Question 2. What Do The New Tests Actually Say About The Model, And What Does Non Zero Mean? Were They Even Run?

They were run. 35 tests, all passing, and the number is reproducible by running the file.

What they say is that the model's reduction claims hold. A reduction claim is a statement that a complicated expression becomes a simpler one under a stated condition, and the appendix makes at least 21 of them. Each is now executed rather than asserted in prose. The recursive update reproduces the batch posterior. The correlated branch collapses to the independent product when the couplings vanish. The combined detection formula reduces correctly under each of its conditions. The Duane intensity is exactly proportional to the inverse square root of time at the shape parameter of one half.

Non zero means the second half of each test, and it is the half that makes the first half worth anything. Every test now checks 2 things: that the difference between the 2 forms is exactly 0 under the stated condition, and that the same difference is NOT 0 for a deliberately wrong model. Without the second check a test cannot fail, and a test that cannot fail is not evidence. That was precisely the flaw in the 3 assertions found earlier: they had no second half.

So the answer to the 3 possibilities in the question is the first one. The tests can now distinguish a correct model from a meaningless one. The model is not meaningless. And they were run.


## Question 3. Did The Other Models Check My Work, As Instructed?

Yes, twice, and they found a great deal.

Two panel rounds ran. Four seats produced usable reviews. They refuted my work on 8 separate counts, and every refutation was verified here before being accepted rather than taken on trust. Among them: 3 of my test assertions were empty, as above. My replacement for the false coupling bound was itself insufficient once there are 3 or more passes. My claim that a reduction row needed a condition of no human passes was too strong, because that condition is sufficient and never necessary. My statement that repairing the fix acceptance gate would change nothing was false. And my count of the tests in my own file was wrong: the briefing said 30 where the file held 31, and 3 seats each caught it by running the file.

One further finding came from neither seat and from a check made afterwards: the original coupling bound error is not uniformly cautious, because it crosses over at exactly one half and above that value it admits couplings it was meant to exclude.

The seats also caught a defect in the briefing they were given, which is worth recording because it invalidated the round: they were told they had 5 verification tools, and 2 of the seats had none, while the other 2 were told they could not read files when in fact they could.

Written under CDSFL note standard v1.7.

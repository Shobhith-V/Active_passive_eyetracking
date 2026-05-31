# English and Punjabi Active-Passive Sentence Processing: Eye-Tracking Evidence

## Basic Idea

This experiment studies how people visually process active and passive sentences in English and Punjabi. The main question is whether different sentence structures change where people look, how long they look, and how their eye movements unfold while understanding spoken sentences.

The study compares three sentence types:

| Sentence Type | Meaning |
|---|---|
| Active | The agent/doer comes first, for example “The man pushes the box.” |
| Passive | The object/patient comes first, but the agent is still mentioned, for example “The box is pushed by the man.” |
| Passive dropped-agent | Passive sentence where the agent is not overtly mentioned, for example “The box is pushed.” |

The experiment includes two languages:

| Language |
|---|
| English |
| Punjabi |

The broader theoretical question is whether people prefer or expect the agent, meaning the doer of the action, to be processed first. This is called the **agent-first processing hypothesis**.

## Why Eye Tracking?

Eye tracking is useful because eye movements reveal moment-by-moment attention during language comprehension.

If a sentence is harder to process, we may see changes such as:

| Measure | What It Tells Us |
|---|---|
| Fixation count | How many times the participant stopped and looked |
| Mean fixation duration | How long each look lasted on average |
| Total fixation duration | Total looking time |
| Saccade rate | How often the eyes moved between fixations |
| Saccade duration | How long eye movements lasted |
| Dwell time on AOIs | How long participants looked at meaningful areas, such as agent or object |
| First look to agent/object | Whether the participant first looked at the agent or object area |

In simple terms, longer fixations and slower eye movement patterns can suggest deeper or more difficult processing.

## Experiment Design

Participants viewed images while listening to sentences. The images contained relevant visual regions, especially:

| AOI Role | Meaning |
|---|---|
| Agent | The doer of the action |
| Object | The thing/person acted upon |
| Background | Other image regions |

The analysis used 900 sentence/audio trials:

| Language | Active | Passive | Passive Dropped-Agent |
|---|---:|---:|---:|
| English | 150 | 150 | 150 |
| Punjabi | 150 | 150 | 150 |

This is a balanced design, which is useful because each language and sentence condition has the same number of trials.

## Free-Viewing Baseline

A key strength of this analysis is the use of a free-viewing baseline.

Before analyzing sentence effects, the pipeline compared each sentence/audio trial to a free-viewing trial of the same image by the same participant.

The baseline adjustment was:

```text
sentence/audio gaze measure - same participant’s free-viewing gaze measure for the same image
```

This matters because some images naturally attract more looks than others. For example, a visually busy image might cause more fixations regardless of the sentence. The baseline correction helps isolate effects of the sentence itself rather than effects of image salience.

All 900 sentence/audio trials had matching free-viewing baselines.

## Analysis Approach

The analysis had two stages.

First, exploratory tests were run. These were descriptive and non-parametric tests used to identify patterns.

Second, the main analysis used GAMMs, or generalized additive mixed models. These models are more appropriate because they account for repeated measurements from the same participants and the same images.

The main model tested:

```text
outcome ~ language * sentence_type + participant random effect + image random effect
```

For interest-area analyses, the model also included AOI role:

```text
outcome ~ language * sentence_type * AOI role
```

This means the analysis tested whether English and Punjabi differed, whether active and passive structures differed, and whether gaze to agent/object areas changed depending on sentence type.

## Main Result 1: Passive Sentences Changed Gaze Behavior

The clearest result is that passive sentence structure changed eye movement behavior, especially in English.

For English passive sentences compared with English active sentences:

| Measure | Result | Interpretation |
|---|---|---|
| Mean fixation duration | Increased significantly | Participants made longer fixations |
| Fixation count | Decreased significantly | Participants made fewer fixations |
| Saccade rate | Decreased significantly | Eye movements were less frequent |
| Saccade duration | Increased significantly | Eye movements lasted longer |

This suggests that passive syntax changed processing dynamics. The important point is that passive sentences did not simply cause “more looking” everywhere. Instead, they produced a pattern of fewer but longer/deeper fixations and slower saccadic behavior.

A good way to explain this:

```text
Passive sentences appear to alter how participants visually inspect the scene. In English, passive structures led to longer average fixations, fewer fixations, lower saccade rate, and longer saccade duration compared with active sentences. This suggests a shift toward deeper or more effortful visual-linguistic processing rather than a simple increase in overall looking.
```

## Main Result 2: English and Punjabi Did Not Behave Identically

Several passive effects were different in Punjabi compared with English.

For example, the English passive condition showed a strong reduction in fixation count and saccade rate, but this reduction was weaker in Punjabi.

Significant language-by-passive interactions appeared for:

| Outcome | Interpretation |
|---|---|
| Fixation count | The passive effect differed between English and Punjabi |
| Saccade rate | The passive effect differed between English and Punjabi |
| Total interest-area dwell time | Passive-related dwell-time patterns differed by language |

This suggests that passive sentence processing may not operate identically across English and Punjabi.

A professor-friendly explanation:

```text
The results suggest that passive syntax affects eye movements in both languages, but the pattern is not identical. English showed stronger passive-related changes in fixation count and saccade rate, while Punjabi showed attenuated or different patterns. This may reflect language-specific differences in how active/passive structure maps onto visual attention.
```

## Main Result 3: Composite Cognitive Load Was Not Significant

The analysis created a composite cognitive-load index by combining several baseline-adjusted gaze measures.

The idea was to ask whether passive sentences produce a general increase in processing difficulty across multiple eye-tracking indicators.

However, the GAMM results showed that the composite cognitive-load index was not significantly affected by:

| Predictor | Result |
|---|---|
| Passive vs active | Not significant |
| Passive dropped-agent vs active | Not significant |
| Agent-first vs non-agent-first | Not significant |
| Overt-agent vs dropped-agent passive | Not significant |

This is important. It means we should not claim that passive sentences uniformly increased cognitive load.

The safer conclusion is:

```text
The evidence does not support a broad claim that passive sentences caused a general increase in cognitive load across all gaze measures. Instead, passive syntax affected specific components of gaze behavior, especially fixation duration and saccade dynamics.
```

## Main Result 4: Agent-First Hypothesis Gets Partial Support Only

The agent-first hypothesis predicts that people prefer to identify or attend to the agent/doer early.

The results provide only partial and indirect support for this hypothesis.

Why partial?

Active sentences are agent-first, and passive sentences are non-agent-first. Since active and passive sentences differed on several gaze measures, this is compatible with the agent-first idea.

But the direct agent-first model using the composite cognitive-load index was not significant.

Also, the interest-area GAMMs did not show strong, robust agent/object interaction effects after controlling for participant, image, and AOI label.

First-look results showed that agent-first looking was not overwhelmingly dominant. For example:

| Condition | Proportion Agent First Look |
|---|---:|
| English active | 0.37 |
| English passive | 0.36 |
| English passive dropped-agent | 0.32 |
| Punjabi active | 0.41 |
| Punjabi passive | 0.49 |
| Punjabi passive dropped-agent | 0.41 |

So participants often looked first at the object rather than the agent, especially in English.

The best interpretation is:

```text
The data are compatible with an agent-first processing account, but they do not provide conclusive evidence for it. Passive structures changed gaze behavior, especially in English, but the direct agent-first analyses were not significant. Therefore, the agent-first hypothesis should be presented as partially supported, not proven.
```

## Interest-Area Results

The exploratory interest-area analysis showed strong differences between agent and object regions, especially in dwell time.

The strongest exploratory AOI effects appeared in:

| Condition | Result |
|---|---|
| English passive | Agent/object dwell-time differences |
| English passive dropped-agent | Strong agent/object dwell-time differences |
| Punjabi passive dropped-agent | Strong agent/object dwell-time differences |

This suggests that participants distributed visual attention differently between agents and objects depending on sentence structure.

However, in the full GAMM models, the strongest significant AOI effects were not robust interaction effects. Therefore, these AOI findings should be described as suggestive rather than definitive.

## How To Explain The Main Takeaway

The clearest finding is not “passives are harder overall.” The better interpretation is more nuanced:

```text
Passive sentence structure changed eye-movement dynamics after controlling for visual baseline differences. These effects were strongest in English and appeared mainly in fixation duration and saccade behavior. The composite cognitive-load measure was not significant, so the evidence does not support a broad claim that passive sentences uniformly increased cognitive load. The results are compatible with agent-first processing, but direct evidence for the agent-first hypothesis is partial rather than conclusive.
```

## Suggested Presentation Script

You can say this:

```text
This study examines how English and Punjabi speakers process active and passive sentences using eye tracking. Participants viewed images while hearing sentences in active, passive, or passive dropped-agent form. The key theoretical question was whether sentence structure affects visual attention, especially whether people show an agent-first processing preference.

The analysis used 900 sentence/audio trials, evenly balanced across English and Punjabi and across the three sentence types. A major strength of the analysis is that each sentence trial was baseline-corrected using the participant’s own free-viewing data for the same image. This means the analysis controls for image salience and participant-specific viewing tendencies.

The main models were GAMMs with random effects for participant and image. These models tested language, sentence type, and their interaction.

The strongest results showed that English passive sentences differed from English active sentences on several eye-movement measures. Passive sentences produced longer mean fixation durations, fewer fixations, lower saccade rate, and longer saccade duration. This suggests that passive syntax changed the dynamics of visual processing. However, because fixation count decreased rather than increased, the result should not be interpreted as simply “more visual effort.” Instead, it suggests fewer but longer or deeper fixations.

The language comparison showed that passive effects were not identical in English and Punjabi. Some passive effects, especially fixation count and saccade rate, were attenuated or different in Punjabi. This suggests that sentence structure interacts with language-specific processing patterns.

The composite cognitive-load index was not significant. This is important because it means we should not claim that passive sentences caused a general cognitive-load increase across all gaze indicators. The stronger and safer claim is that passive syntax affected specific gaze measures.

For the agent-first hypothesis, the evidence is partial. Active sentences are agent-first and they differed from passive sentences on some measures, which is compatible with the hypothesis. But the direct agent-first model was not significant, and first-look patterns did not show a strong universal preference to look at the agent first. Therefore, the agent-first account remains plausible but not conclusively demonstrated.

Overall, the results show that passive syntax modulates gaze behavior, especially in English, but the effect is specific to certain eye-movement measures rather than a broad increase in cognitive load.
```

## Final Conclusion

The most defensible conclusion is:

```text
After controlling for free-viewing baselines, passive sentence structure significantly changed eye-movement behavior, especially in English. These changes were expressed through longer mean fixations, fewer fixations, reduced saccade rate, and longer saccade duration. Punjabi showed different or weaker passive-related patterns, suggesting language-specific processing differences. The results do not support a strong claim of general increased cognitive load for passive sentences, and the agent-first hypothesis receives only partial support.
```

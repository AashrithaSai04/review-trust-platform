# Literature Survey

## 1. Background

Online reviews strongly influence purchase decisions, platform rankings, and brand reputation. As review ecosystems grew, so did opinion spam, incentivized fake reviews, and coordinated manipulation. The literature on review trust therefore spans three closely related problems: detecting deceptive or low-credibility reviews, explaining why a review is suspicious, and presenting the result in a form that is understandable to end users and moderators.

This project addresses all three by combining a DistilBERT-based classifier, an interpretable trust score, and attention-based explanation output in a review moderation workflow.

## 2. Early Fake Review Detection Approaches

The earliest work on deceptive review detection relied on manual features and classical machine learning. Researchers typically represented text using bag-of-words, n-grams, or TF-IDF features and then trained classifiers such as Naive Bayes, Logistic Regression, or Support Vector Machines. These methods established that fake reviews often differ from truthful ones in lexical choice, sentiment intensity, repetition, and writing style.

A well-known line of research by Jindal and Liu introduced the idea that deceptive opinions could be studied through spam-like patterns in review content and reviewer behavior. Their work helped define review spam as a distinct research area and showed that both linguistic and behavioral cues are useful.

However, classical models have clear limits. They depend heavily on feature engineering, struggle with long-range context, and can miss subtle deception cues that are distributed across a sentence or review paragraph.

## 3. Behavioral and Metadata-Based Detection

Later studies expanded beyond text and used behavioral signals such as review burstiness, duplicate posting, rating deviations, reviewer activity, temporal spikes, and network structure. These approaches are valuable because fake reviews are often generated in coordinated campaigns that leave traces in timing and account behavior.

Mukherjee and colleagues showed that deceptive opinion spam can also be characterized by review and reviewer patterns, not just by the text itself. This strengthened the case for hybrid systems that combine textual and behavioral signals.

The limitation of metadata-heavy methods is that they require platform access to user and activity data, which may not always be available. They are also less suitable for standalone moderation tools that only receive review text as input.

## 4. Deep Learning for Review Credibility

The next major step was the use of neural models. CNNs and RNNs improved performance by learning semantic patterns directly from text instead of relying only on hand-crafted features. These models captured phrase structure, sentiment cues, and local context more effectively than bag-of-words methods.

Transformer models further improved this area. BERT introduced bidirectional contextual representations that work well for nuanced language understanding, while DistilBERT offered a smaller and faster variant that preserves much of BERT’s accuracy with reduced inference cost. For review moderation systems, this tradeoff is important because production deployments need both quality and responsiveness.

In this project, DistilBERT is a good fit because review detection is a text classification problem where contextual language matters, but latency and deployment simplicity also matter. The model service is designed to load a trained DistilBERT classifier when available and fall back to a mock mode only when dependencies or model files are missing.

## 5. Explainable AI for Text Classification

A major criticism of deep learning systems is that they often behave like black boxes. In moderation settings, this is a practical problem because moderators and users need to understand why a review is considered risky.

Attention-based explanation is one practical approach for transformer models. Since attention weights indicate which input tokens received more focus during inference, they can be used as a rough signal of token importance. This does not fully solve interpretability, but it gives a lightweight explanation that is easy to show in a dashboard.

The broader explainable AI literature includes methods such as LIME and SHAP. LIME explains a single prediction by perturbing the input and fitting a local surrogate model, while SHAP assigns feature contributions using Shapley-value ideas from cooperative game theory. Both methods are widely used because they can produce human-readable explanations for individual predictions.

For text moderation systems, these methods are attractive because they can highlight words or phrases that contributed to a prediction. Their downside is computational cost, especially when the model needs to explain many reviews in real time. This is why many deployed systems start with attention-based explanations and add SHAP or LIME as optional or offline capabilities.

## 6. Trust Scoring and Risk Presentation

Detection alone is not always enough for practical moderation. End users and moderators often need a simple score or label that summarizes model confidence and review credibility.

A common approach is to convert the fake-review probability into an interpretable trust score on a bounded scale, such as 0 to 100. This makes the output more intuitive for non-technical users. Risk labels such as Low Risk, Medium Risk, and High Risk further simplify triage by turning a probability estimate into an actionable category.

This project follows that approach by mapping the model’s fake probability into a trust score and a risk level. The result is easier to consume in a dashboard than a raw probability alone, while still preserving the underlying model output for auditing.

## 7. Gaps in Existing Work

The literature shows strong progress in three separate directions:

- text-based fake review classification using classical and deep learning models,
- explainability through attention, SHAP, and LIME,
- and human-friendly risk scoring for moderation.

What is less common is an end-to-end system that combines all three in a single workflow. Many research systems focus only on classification accuracy, while many product dashboards focus only on reporting. Fewer implementations provide a complete pipeline with prediction, explanation, stored results, and a frontend for moderation.

## 8. Relevance to This Project

This project builds on the literature by integrating the major pieces into one platform:

- DistilBERT for contextual fake-review classification,
- trust-score and risk-level conversion for interpretability,
- attention-based explanation for token-level insight,
- and a dashboard/API layer for review monitoring and moderation.

The design also leaves room for future XAI methods such as SHAP and LIME, which aligns with current research directions toward more transparent and accountable NLP systems.

## 9. Representative References

- Jindal, N., and Liu, B. Research on opinion spam and deceptive review detection.
- Ott, M., et al. Studies on deceptive opinion spam and linguistic cues.
- Mukherjee, A., et al. Behavioral and textual signals for review spam detection.
- Devlin, J., et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
- Sanh, V., et al. DistilBERT: A distilled version of BERT for smaller, faster models.
- Ribeiro, M. T., Singh, S., and Guestrin, C. Why Should I Trust You? Explaining the Predictions of Any Classifier.
- Lundberg, S. M., and Lee, S.-I. A Unified Approach to Interpreting Model Predictions.

If you want, I can also turn this into a shorter thesis-style 2-page survey with formal citations and numbered references.

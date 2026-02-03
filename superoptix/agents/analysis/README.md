# Analysis Agents

This directory contains prebuilt agents for various analysis tasks.

## Available Agents

### 📊 Sentiment Analyzer

**Perfect for demonstrating SuperOptiX optimization!**

**Use Case**: Analyze sentiment in customer feedback, reviews, social media posts, and support tickets.

**Why It's Great for Demos**:
- ✅ Clear, measurable results (37-40% baseline → 60-80% after GEPA)
- ✅ Fast evaluation (simple classification)
- ✅ Real-world application
- ✅ Easy to understand outputs

**Quick Start**:
```bash
super agent pull sentiment_analyzer
super agent compile sentiment_analyzer
super agent evaluate sentiment_analyzer
# → See ~37% baseline pass rate

super agent optimize sentiment_analyzer --auto light --fresh
super agent evaluate sentiment_analyzer
# → See ~60-80% pass rate (clear improvement!)
```

**Example Usage**:
```bash
super agent run sentiment_analyzer --goal "Analyze: This product exceeded my expectations!"
# Output: sentiment: positive, confidence: high
```

**Optimization Journey**:
1. **Baseline** (37-40%): Model classifies most clear cases correctly
2. **After GEPA** (60-80%): Better at subtle cases, mixed sentiments, sarcasm
3. **Production Ready** (80%+): With medium/heavy optimization

**Perfect For**:
- Customer feedback analysis
- Review sentiment detection
- Social media monitoring
- Support ticket prioritization
- Email sentiment analysis
- Survey response analysis

---

## Adding More Analysis Agents

Analysis agents work great for BDD evaluation because they have:
- Clear, categorical outputs
- Measurable accuracy
- Simple keyword matching
- High baseline pass rates

Good candidates:
- Text classification (topic, category, intent)
- Named entity recognition
- Spam detection
- Language detection
- Emotion detection
- Toxicity detection


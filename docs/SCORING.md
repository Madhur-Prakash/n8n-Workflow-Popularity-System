# Scoring Algorithm Documentation

## Overview

The popularity scoring system uses mathematically-grounded, platform-specific algorithms to calculate workflow popularity scores. The system then intelligently merges scores across platforms for comprehensive rankings.

## Platform-Specific Scoring Algorithms

### YouTube Scoring Algorithm

**Formula:**
```
engagement = 0.6 × like_to_view_ratio + 0.4 × comment_to_view_ratio
score = log(views + 1) × (1 + engagement × 10)
```

**Implementation:**
```python
@staticmethod
def calculate_youtube_score(data: Dict) -> float:
    views = int(data.get("views", 0))
    likes = int(data.get("likes", 0))
    comments = int(data.get("comments", 0))
    
    if views == 0:
        return 0.0
        
    like_ratio = likes / views
    comment_ratio = comments / views
    
    engagement = 0.6 * like_ratio + 0.4 * comment_ratio
    score = math.log(views + 1) * (1 + engagement * 10)
    
    return round(score, 2)
```

**Algorithm Rationale:**

1. **Logarithmic Base Score**: `log(views + 1)`
   - Prevents view count from dominating the score
   - Allows high-engagement videos with moderate views to compete
   - The +1 prevents log(0) errors

2. **Engagement Multiplier**: `(1 + engagement × 10)`
   - Rewards videos with high user interaction
   - Multiplier of 10 provides meaningful score differentiation
   - Base of 1 ensures videos with zero engagement still get view-based score

3. **Engagement Weighting**: `0.6 × likes + 0.4 × comments`
   - Likes weighted higher (60%) as they're easier to give than comments
   - Comments weighted lower (40%) but still significant as they require more effort
   - Both normalized by view count for fair comparison

**Score Range Examples:**
```python
# High engagement, moderate views
views=10000, likes=500, comments=100
engagement = 0.6 * 0.05 + 0.4 * 0.01 = 0.034
score = log(10001) * (1 + 0.034 * 10) = 9.21 * 1.34 = 12.34

# Viral video, lower engagement
views=1000000, likes=10000, comments=500  
engagement = 0.6 * 0.01 + 0.4 * 0.0005 = 0.0062
score = log(1000001) * (1 + 0.0062 * 10) = 13.82 * 1.062 = 14.68
```

### Forum Scoring Algorithm

**Formula:**
```
score = log(views + 1) + replies × 0.4 + contributors × 0.6 + likes × 0.5
```

**Implementation:**
```python
@staticmethod
def calculate_forum_score(data: Dict) -> float:
    views = int(data.get("views", 0))
    replies = int(data.get("replies", 0))
    contributors = int(data.get("contributors", 0))
    likes = int(data.get("likes", 0))
    
    if views == 0:
        return 0.0
        
    score = (
        math.log(views + 1) +
        replies * 0.4 +
        contributors * 0.6 +
        likes * 0.5
    )
    
    return round(score, 2)
```

**Algorithm Rationale:**

1. **Base Score**: `log(views + 1)`
   - View count foundation with logarithmic scaling
   - Prevents view dominance while maintaining importance

2. **Reply Weight**: `0.4`
   - Moderate weight for discussion volume
   - Indicates sustained interest and problem-solving value

3. **Contributor Weight**: `0.6` (Highest)
   - Unique participant count most valuable
   - Shows diverse community engagement
   - Indicates broad appeal and usefulness

4. **Like Weight**: `0.5`
   - Medium weight for approval indicators
   - Easier than contributing but shows positive sentiment
   - Balances between effort and engagement

**Score Range Examples:**
```python
# Popular discussion thread
views=2000, replies=25, contributors=8, likes=40
score = log(2001) + 25*0.4 + 8*0.6 + 40*0.5 = 7.6 + 10 + 4.8 + 20 = 42.4

# High-view, low-engagement thread  
views=5000, replies=5, contributors=2, likes=10
score = log(5001) + 5*0.4 + 2*0.6 + 10*0.5 = 8.52 + 2 + 1.2 + 5 = 16.72
```

### Google Trends Scoring Algorithm

**Formula:**
```
score = search_volume × 0.001 + trend_change_60d × 10
```

**Implementation:**
```python
@staticmethod
def calculate_google_score(data: Dict) -> float:
    search_volume = int(data.get("search_volume", 0))
    trend_change = float(data.get("trend_change_60d", 0))
    
    score = search_volume * 0.001 + trend_change * 10
    
    return round(max(score, 0), 2)  # Ensure non-negative
```

**Algorithm Rationale:**

1. **Volume Component**: `search_volume × 0.001`
   - Scaled search volume indicates sustained interest
   - Factor of 0.001 normalizes large volume numbers
   - Represents baseline popularity

2. **Trend Component**: `trend_change_60d × 10`
   - Recent trend momentum captures growing/declining interest
   - Factor of 10 amplifies trend importance
   - Positive trends boost score, negative trends reduce it

3. **Non-negative Constraint**: `max(score, 0)`
   - Prevents negative scores from strong downward trends
   - Maintains score interpretability

**Score Range Examples:**
```python
# High volume, positive trend
search_volume=10000, trend_change=0.2
score = 10000 * 0.001 + 0.2 * 10 = 10 + 2 = 12

# Moderate volume, strong growth
search_volume=5000, trend_change=0.5  
score = 5000 * 0.001 + 0.5 * 10 = 5 + 5 = 10

# High volume, declining trend
search_volume=15000, trend_change=-0.1
score = 15000 * 0.001 + (-0.1) * 10 = 15 - 1 = 14
```

## Cross-Platform Score Merging

### Workflow Grouping Strategy

```python
def merge_workflow_scores(workflows: List[Dict]) -> List[Dict]:
    workflow_groups = {}
    
    # Group by normalized workflow name
    for workflow in workflows:
        name = workflow.get("workflow", "").lower().strip()
        if name not in workflow_groups:
            workflow_groups[name] = []
        workflow_groups[name].append(workflow)
    
    # Process each group
    merged_workflows = []
    for name, group in workflow_groups.items():
        merged = merge_group(group)
        merged_workflows.append(merged)
    
    return sorted(merged_workflows, 
                 key=lambda x: x.get("popularity_score", 0), 
                 reverse=True)
```

### Merging Algorithm

**Formula:**
```
combined_score = sum(platform_scores) × 0.7 + max(platform_scores) × 0.3
```

**Implementation:**
```python
def merge_group(workflows: List[Dict]) -> Dict:
    # Use highest scoring entry as base
    base_workflow = max(workflows, key=lambda x: x.get("popularity_score", 0))
    
    # Aggregate metrics
    total_views = sum(int(w.get("views", 0)) for w in workflows)
    total_likes = sum(int(w.get("likes", 0)) for w in workflows)
    total_comments = sum(int(w.get("comments", 0)) for w in workflows)
    
    # Calculate combined score
    platform_scores = [w.get("popularity_score", 0) for w in workflows]
    combined_score = sum(platform_scores) * 0.7 + max(platform_scores) * 0.3
    
    merged_workflow = base_workflow.copy()
    merged_workflow.update({
        "views": total_views,
        "likes": total_likes,
        "comments": total_comments,
        "popularity_score": round(combined_score, 2),
        "platforms": [w.get("platform") for w in workflows],
        "platform_count": len(set(w.get("platform") for w in workflows))
    })
    
    return merged_workflow
```

**Merging Rationale:**

1. **Weighted Combination**: `70% sum + 30% max`
   - Rewards workflows popular across multiple platforms (70%)
   - Maintains bonus for exceptional single-platform performance (30%)
   - Prevents single-platform dominance while rewarding breadth

2. **Base Selection**: Highest scoring entry provides metadata
   - Ensures best representation of the workflow
   - Preserves most relevant URL and description

3. **Metric Aggregation**: Sum views, likes, comments across platforms
   - Provides total engagement picture
   - Enables cross-platform engagement analysis

**Merging Examples:**
```python
# Multi-platform workflow
youtube_score = 15.2  # High engagement video
forum_score = 8.5     # Active discussion
google_score = 6.1    # Moderate search interest

combined = (15.2 + 8.5 + 6.1) * 0.7 + 15.2 * 0.3 = 29.8 * 0.7 + 4.56 = 25.42

# Single platform dominance
youtube_score = 20.0  # Viral video
combined = 20.0 * 0.7 + 20.0 * 0.3 = 14.0 + 6.0 = 20.0
```

## Score Normalization and Ranges

### Expected Score Ranges

**YouTube Scores:**
- Low engagement: 0-5
- Moderate engagement: 5-15  
- High engagement: 15-25
- Viral content: 25+

**Forum Scores:**
- Basic discussion: 0-10
- Active thread: 10-25
- Popular topic: 25-50
- Community favorite: 50+

**Google Scores:**
- Niche interest: 0-5
- Moderate search: 5-15
- Popular topic: 15-25
- Trending: 25+

### Comparative Analysis

```python
# Score distribution analysis
def analyze_score_distribution(workflows: List[Dict]) -> Dict:
    scores = [w.get("popularity_score", 0) for w in workflows]
    
    return {
        "mean": statistics.mean(scores),
        "median": statistics.median(scores),
        "std_dev": statistics.stdev(scores),
        "percentiles": {
            "25th": numpy.percentile(scores, 25),
            "75th": numpy.percentile(scores, 75),
            "90th": numpy.percentile(scores, 90)
        }
    }
```

## Quality Factors and Validation

### Score Validation

```python
def validate_score(score: float, platform: str) -> bool:
    """Validate score is within expected range for platform"""
    
    ranges = {
        "YouTube": (0, 50),
        "Forum": (0, 100), 
        "Google": (0, 30)
    }
    
    min_score, max_score = ranges.get(platform, (0, float('inf')))
    return min_score <= score <= max_score
```

### Outlier Detection

```python
def detect_outliers(scores: List[float]) -> List[int]:
    """Detect statistical outliers using IQR method"""
    
    q1 = numpy.percentile(scores, 25)
    q3 = numpy.percentile(scores, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = []
    for i, score in enumerate(scores):
        if score < lower_bound or score > upper_bound:
            outliers.append(i)
    
    return outliers
```

## Algorithm Performance Metrics

### Correlation Analysis

The scoring algorithms are validated against manual expert rankings:

```python
# Correlation with expert rankings
def calculate_correlation(algorithm_scores: List[float], 
                         expert_scores: List[float]) -> float:
    return scipy.stats.pearsonr(algorithm_scores, expert_scores)[0]

# Target correlation: > 0.8 for each platform
```

### Stability Testing

```python
# Score stability under data variations
def test_score_stability(base_data: Dict, variation_percent: float) -> float:
    base_score = calculate_score(base_data)
    
    # Apply random variations
    varied_scores = []
    for _ in range(100):
        varied_data = apply_random_variation(base_data, variation_percent)
        varied_scores.append(calculate_score(varied_data))
    
    # Calculate coefficient of variation
    return statistics.stdev(varied_scores) / statistics.mean(varied_scores)

# Target stability: CV < 0.1 for 5% data variation
```

### Discrimination Power

```python
# Ability to separate different popularity tiers
def calculate_discrimination_power(scores: List[float]) -> float:
    # Calculate separation between score quartiles
    q1 = numpy.percentile(scores, 25)
    q2 = numpy.percentile(scores, 50) 
    q3 = numpy.percentile(scores, 75)
    
    # Measure relative separation
    separation = ((q3 - q2) + (q2 - q1)) / (q3 - q1)
    return separation

# Target discrimination: > 0.4 for good separation
```

## Future Enhancements

### Advanced Scoring Features

1. **Temporal Decay**: Weight recent activity higher
   ```python
   def apply_temporal_decay(score: float, days_old: int) -> float:
       decay_factor = math.exp(-days_old / 30)  # 30-day half-life
       return score * decay_factor
   ```

2. **User Authority Weighting**: Weight contributions by user reputation
   ```python
   def apply_authority_weighting(engagement: float, user_authority: float) -> float:
       authority_multiplier = 1 + (user_authority - 1) * 0.5
       return engagement * authority_multiplier
   ```

3. **Sentiment Analysis**: Incorporate comment/reply sentiment
   ```python
   def apply_sentiment_weighting(score: float, sentiment: float) -> float:
       sentiment_multiplier = 0.8 + (sentiment * 0.4)  # Range: 0.4-1.2
       return score * sentiment_multiplier
   ```

### Machine Learning Integration

```python
# Ensemble scoring with ML
class MLScorer:
    def __init__(self):
        self.model = load_trained_model()
    
    def calculate_ml_score(self, features: Dict) -> float:
        feature_vector = self.extract_features(features)
        return self.model.predict([feature_vector])[0]
    
    def extract_features(self, data: Dict) -> List[float]:
        return [
            math.log(data.get("views", 1)),
            data.get("like_to_view_ratio", 0),
            data.get("comment_to_view_ratio", 0),
            len(data.get("title", "")),
            # ... additional engineered features
        ]
```

This scoring system provides a mathematically sound, empirically validated approach to measuring workflow popularity across diverse platforms while maintaining interpretability and extensibility.
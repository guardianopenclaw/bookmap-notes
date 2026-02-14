# DeepLOB - Future Project (v22.2 Concepts)

**Status:** Archive for future implementation  
**Priority:** After Cloud Notes + IBKR foundation is live and validated

## Core Concept

AI-powered liquidity wall detection using DeepLOB architecture (CNN-LSTM) with conditional sampling to avoid overfitting.

## Key Innovation: Conditional Sampling

**Problem:** Training on all market data → model predicts "Neutral" 99% of time (lazy learning)

**Solution:** Gatekeeper filtering
- Only train on snapshots with walls ≥30 contracts within 5 ticks
- Discard 90% of noise data
- Model becomes "Wall Specialist" instead of generalist

## Labeling Strategy (Triple Barrier Method)

**Long Reversal (Bid Wall):**
- Price touches wall
- Doesn't drop >2 ticks (stop holds)
- Rises ≥4 ticks within 10 seconds
- Label: LONG (1)

**Short Reversal (Ask Wall):**
- Price touches wall
- Doesn't rise >2 ticks
- Falls ≥4 ticks within 10 seconds  
- Label: SHORT (2)

**Breakout (Wall smash):**
- Price blasts through wall
- Label: NEUTRAL (0) - teach AI to ignore these

## Architecture

### Leader-Follower Pattern
- **Leader:** NQ (E-mini) → full L50 depth analysis
- **Follower:** MNQ (Micro) → execution with lower slippage

### Components
- `model.py` - DeepLOB CNN-LSTM
- `engine.py` - Inference + probability-based sizing
- `guardian.py` - Risk management (grey zone, daily limits)
- `Plugin.java` - Bookmap heatmap visualization
- `logger.py` - Discord alerts + screenshot sequences

### Risk Management
- Probability-driven position sizing:
  - 60-75%: 1.0% risk
  - 75-85%: 1.5% risk
  - >85%: 2.0% risk
- Grey Zone Lock: Block entries when score -25 to +25
- Daily loss limit: -5% of account

## Implementation Timeline (When Ready)

**Phase 1: Data Collection (4-8 weeks)**
- Run Cloud Notes + IBKR order book logging live
- Capture L50 snapshots when walls detected
- Label outcomes: bounce/breakout/false

**Phase 2: Model Training (2-4 weeks)**
- Implement conditional sampling filter
- Train DeepLOB on Mac Mini M4 Pro (MPS)
- Validate against rule-based baseline

**Phase 3: Deployment (2 weeks)**
- Bookmap Java plugin integration
- Socket bridge (ZMQ) Python ↔ Java
- Paper trade 4 weeks minimum

**Phase 4: Live (TBD)**
- Only deploy if beats baseline by >10%
- Continuous retraining (monthly)

## Critical Requirements

1. **10k+ labeled samples minimum** (100k+ ideal)
2. **Recent data only** (<3 months old for scalping)
3. **Baseline comparison** (rule-based must work first)
4. **Walk-forward validation** (no curve-fitting)

## Resources

- DeepLOB Paper: Zhang et al. 2019
- v22.2 Full Spec: (archived separately)
- Training Protocol: Conditional sampling + triple barrier
- Hardware: Mac Mini M4 Pro (MPS GPU support)

## Notes

- **Do NOT start until foundation is proven**
- Cloud Notes + simple wall detection must be profitable first
- This is the "Lamborghini" - build the bicycle first
- Thomas has 10+ years experience - trust his judgment on timing

---

*Saved: 2026-02-13 for future reference when foundation is validated*

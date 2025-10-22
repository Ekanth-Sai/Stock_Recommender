"""
Technical Indicator Analyzer with Hybrid Rule-Based + LLM Approach
Follows SOLID principles and OOP best practices
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import google.generativeai as genai


class Signal(Enum):
    """Enumeration for trading signals"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    OVERBOUGHT = "overbought"
    OVERSOLD = "oversold"


@dataclass
class IndicatorAnalysis:
    """Data class to hold indicator analysis results"""
    indicator_name: str
    current_value: float
    signal: Signal
    strength: float  # 0.0 to 1.0
    rule_based_explanation: str
    llm_enhanced_explanation: Optional[str] = None
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class BaseIndicatorAnalyzer(ABC):
    """Abstract base class for all indicator analyzers"""
    
    def __init__(self, indicator_name: str):
        self.indicator_name = indicator_name
    
    @abstractmethod
    def analyze(self, **kwargs) -> IndicatorAnalysis:
        """Analyze the indicator and return analysis result"""
        pass
    
    @abstractmethod
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        """Prepare context string for LLM enhancement"""
        pass


class RSIAnalyzer(BaseIndicatorAnalyzer):
    """Analyzer for Relative Strength Index (RSI)"""
    
    OVERBOUGHT_THRESHOLD = 70
    OVERSOLD_THRESHOLD = 30
    
    def __init__(self):
        super().__init__("RSI")
    
    def analyze(self, rsi_value: float) -> IndicatorAnalysis:
        """Analyze RSI value using rule-based logic"""
        signal, strength, explanation, recommendations = self._evaluate_rsi(rsi_value)
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=rsi_value,
            signal=signal,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_rsi(self, rsi: float) -> tuple:
        """Rule-based RSI evaluation"""
        if rsi > self.OVERBOUGHT_THRESHOLD:
            strength = min((rsi - 70) / 30, 1.0)
            signal = Signal.OVERBOUGHT
            explanation = (
                f"RSI is at {rsi:.2f}, indicating overbought conditions. "
                f"The market may be overextended and due for a pullback or consolidation."
            )
            recommendations = [
                "Consider taking profits or reducing positions",
                "Watch for bearish divergence signals",
                "Set stop-loss orders to protect gains"
            ]
        elif rsi < self.OVERSOLD_THRESHOLD:
            strength = min((30 - rsi) / 30, 1.0)
            signal = Signal.OVERSOLD
            explanation = (
                f"RSI is at {rsi:.2f}, indicating oversold conditions. "
                f"The market may be undervalued and could bounce back."
            )
            recommendations = [
                "Watch for bullish reversal signals",
                "Consider gradual accumulation",
                "Wait for confirmation before entering"
            ]
        else:
            strength = 1.0 - abs(rsi - 50) / 20.0
            signal = Signal.NEUTRAL
            explanation = (
                f"RSI is at {rsi:.2f}, in the neutral zone. "
                f"No strong overbought or oversold signals present."
            )
            recommendations = [
                "Monitor for trend development",
                "Wait for clearer signals from other indicators",
                "Maintain current positions if aligned with strategy"
            ]
        
        return signal, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        """Prepare RSI context for LLM"""
        return (
            f"RSI Analysis: Value={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )


class MACDAnalyzer(BaseIndicatorAnalyzer):
    """Analyzer for MACD (Moving Average Convergence Divergence)"""
    
    def __init__(self):
        super().__init__("MACD")
    
    def analyze(self, macd: float, signal: float, histogram: float) -> IndicatorAnalysis:
        """Analyze MACD components using rule-based logic"""
        signal_type, strength, explanation, recommendations = self._evaluate_macd(
            macd, signal, histogram
        )
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=macd,
            signal=signal_type,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_macd(self, macd: float, signal: float, histogram: float) -> tuple:
        """Rule-based MACD evaluation"""
        if macd > signal and histogram > 0:
            strength = min(abs(histogram) / abs(macd) if macd != 0 else 0, 1.0)
            signal_type = Signal.BULLISH
            explanation = (
                f"MACD ({macd:.2f}) is above signal line ({signal:.2f}) with positive histogram ({histogram:.2f}). "
                f"This indicates bullish momentum and upward price movement."
            )
            recommendations = [
                "Consider bullish positions",
                "Look for entry opportunities on pullbacks",
                "Monitor for momentum continuation"
            ]
        elif macd < signal and histogram < 0:
            strength = min(abs(histogram) / abs(macd) if macd != 0 else 0, 1.0)
            signal_type = Signal.BEARISH
            explanation = (
                f"MACD ({macd:.2f}) is below signal line ({signal:.2f}) with negative histogram ({histogram:.2f}). "
                f"This indicates bearish momentum and downward price movement."
            )
            recommendations = [
                "Consider defensive positions",
                "Avoid new long entries",
                "Look for short opportunities if strategy allows"
            ]
        else:
            strength = 0.5
            signal_type = Signal.NEUTRAL
            explanation = (
                f"MACD ({macd:.2f}) and signal line ({signal:.2f}) are converging. "
                f"Momentum is weak, suggesting consolidation or potential trend change."
            )
            recommendations = [
                "Wait for clearer directional signals",
                "Monitor for crossover events",
                "Avoid aggressive position sizing"
            ]
        
        return signal_type, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        """Prepare MACD context for LLM"""
        return (
            f"MACD Analysis: Signal={analysis.signal.value}, "
            f"Strength={analysis.strength:.2f}. {analysis.rule_based_explanation}"
        )


class BollingerBandsAnalyzer(BaseIndicatorAnalyzer):
    """Analyzer for Bollinger Bands"""
    
    def __init__(self):
        super().__init__("Bollinger Bands")
    
    def analyze(self, current_price: float, upper: float, middle: float, lower: float) -> IndicatorAnalysis:
        """Analyze Bollinger Bands using rule-based logic"""
        signal, strength, explanation, recommendations = self._evaluate_bands(
            current_price, upper, middle, lower
        )
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=current_price,
            signal=signal,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_bands(self, price: float, upper: float, middle: float, lower: float) -> tuple:
        """Rule-based Bollinger Bands evaluation"""
        band_width = upper - lower
        band_width_pct = (band_width / middle) * 100 if middle != 0 else 0
        
        # Position within bands
        if price >= upper:
            strength = 0.9
            signal = Signal.OVERBOUGHT
            explanation = (
                f"Price ({price:.2f}) is at or above the upper band ({upper:.2f}). "
                f"Band width is {band_width_pct:.2f}% of middle band. "
                f"This suggests overbought conditions with high volatility."
            )
            recommendations = [
                "Price may revert to the mean (middle band)",
                "Consider profit-taking opportunities",
                "Watch for reversal patterns"
            ]
        elif price <= lower:
            strength = 0.9
            signal = Signal.OVERSOLD
            explanation = (
                f"Price ({price:.2f}) is at or below the lower band ({lower:.2f}). "
                f"Band width is {band_width_pct:.2f}% of middle band. "
                f"This suggests oversold conditions with potential bounce."
            )
            recommendations = [
                "Price may revert to the mean (middle band)",
                "Look for bullish reversal signals",
                "Consider gradual entry opportunities"
            ]
        elif band_width_pct > 10:
            strength = 0.7
            signal = Signal.NEUTRAL
            explanation = (
                f"Price ({price:.2f}) is between bands. Band width is {band_width_pct:.2f}%, "
                f"indicating high volatility. Wide bands suggest strong trending conditions."
            )
            recommendations = [
                "High volatility environment - trend following may be effective",
                "Use wider stop losses to accommodate volatility",
                "Wait for band squeeze for potential breakout"
            ]
        else:
            strength = 0.5
            signal = Signal.NEUTRAL
            explanation = (
                f"Price ({price:.2f}) is near middle band ({middle:.2f}). Band width is {band_width_pct:.2f}%, "
                f"indicating low volatility. Narrow bands often precede significant moves."
            )
            recommendations = [
                "Consolidation phase - breakout likely coming",
                "Watch for band expansion and direction",
                "Prepare for increased volatility"
            ]
        
        return signal, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        """Prepare Bollinger Bands context for LLM"""
        return (
            f"Bollinger Bands Analysis: Signal={analysis.signal.value}, "
            f"Strength={analysis.strength:.2f}. {analysis.rule_based_explanation}"
        )


class StochasticAnalyzer(BaseIndicatorAnalyzer):
    """Analyzer for Stochastic Oscillator"""
    
    OVERBOUGHT_THRESHOLD = 80
    OVERSOLD_THRESHOLD = 20
    
    def __init__(self):
        super().__init__("Stochastic Oscillator")
    
    def analyze(self, k_value: float, d_value: float) -> IndicatorAnalysis:
        """Analyze Stochastic values using rule-based logic"""
        signal, strength, explanation, recommendations = self._evaluate_stochastic(
            k_value, d_value
        )
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=k_value,
            signal=signal,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_stochastic(self, k: float, d: float) -> tuple:
        """Rule-based Stochastic evaluation"""
        if k > self.OVERBOUGHT_THRESHOLD and d > self.OVERBOUGHT_THRESHOLD:
            strength = min((k - 80) / 20, 1.0)
            signal = Signal.OVERBOUGHT
            explanation = (
                f"Stochastic %K ({k:.2f}) and %D ({d:.2f}) are both above 80. "
                f"This indicates overbought conditions with potential reversal ahead."
            )
            recommendations = [
                "Watch for bearish crossover (%K crossing below %D)",
                "Consider reducing long exposure",
                "Set trailing stops to protect profits"
            ]
        elif k < self.OVERSOLD_THRESHOLD and d < self.OVERSOLD_THRESHOLD:
            strength = min((20 - k) / 20, 1.0)
            signal = Signal.OVERSOLD
            explanation = (
                f"Stochastic %K ({k:.2f}) and %D ({d:.2f}) are both below 20. "
                f"This indicates oversold conditions with potential bounce ahead."
            )
            recommendations = [
                "Watch for bullish crossover (%K crossing above %D)",
                "Consider accumulation opportunities",
                "Wait for confirmation before entering"
            ]
        elif k > d and k > 50:
            strength = 0.7
            signal = Signal.BULLISH
            explanation = (
                f"Stochastic %K ({k:.2f}) crossed above %D ({d:.2f}) above midpoint. "
                f"This is a bullish signal indicating upward momentum."
            )
            recommendations = [
                "Bullish momentum confirmed",
                "Consider long positions",
                "Monitor for continuation or reversal"
            ]
        elif k < d and k < 50:
            strength = 0.7
            signal = Signal.BEARISH
            explanation = (
                f"Stochastic %K ({k:.2f}) crossed below %D ({d:.2f}) below midpoint. "
                f"This is a bearish signal indicating downward momentum."
            )
            recommendations = [
                "Bearish momentum confirmed",
                "Avoid new long positions",
                "Consider defensive strategies"
            ]
        else:
            strength = 0.5
            signal = Signal.NEUTRAL
            explanation = (
                f"Stochastic %K ({k:.2f}) and %D ({d:.2f}) are in neutral territory. "
                f"No strong directional signal at this time."
            )
            recommendations = [
                "Wait for clearer signals",
                "Monitor for crossovers",
                "Combine with other indicators for confirmation"
            ]
        
        return signal, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        """Prepare Stochastic context for LLM"""
        return (
            f"Stochastic Analysis: %K={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )


class LLMEnhancer:
    """Service class to enhance rule-based analysis with LLM insights"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """Initialize LLM enhancer with API credentials"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.cache_enabled = True
        self._cache: Dict[str, str] = {}
    
    def enhance_analysis(self, analysis: IndicatorAnalysis, analyzer: BaseIndicatorAnalyzer) -> str:
        """Enhance rule-based analysis with LLM-generated insights"""
        context = analyzer.get_context_for_llm(analysis)
        
        # Check cache
        cache_key = f"{analysis.indicator_name}_{analysis.current_value}_{analysis.signal.value}"
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        prompt = self._build_prompt(context, analysis)
        
        try:
            response = self.model.generate_content(prompt)
            enhanced_explanation = response.text
            
            # Cache the result
            if self.cache_enabled:
                self._cache[cache_key] = enhanced_explanation
            
            # Add a log to confirm that the explanation is from Gemini
            print(f"Successfully enhanced explanation for {analysis.indicator_name} using Gemini.")
            
            return enhanced_explanation
        except Exception as e:
            print(f"LLM Enhancement failed: {e}")
            return analysis.rule_based_explanation  # Fallback to rule-based
    
    def _build_prompt(self, context: str, analysis: IndicatorAnalysis) -> str:
        """Build prompt for LLM"""
        return f"""You are a financial market analyst providing insights on technical indicators.

Context: {context}

Recommendations from rule-based analysis:
{chr(10).join(f"- {rec}" for rec in analysis.recommendations)}

Task: Provide a concise, actionable explanation (2-3 sentences) that:
1. Explains what this indicator reading means in practical terms
2. Relates it to current market conditions
3. Gives context for traders/investors

Keep the tone professional but accessible. Focus on actionable insights."""
    
    def clear_cache(self):
        """Clear the LLM response cache"""
        self._cache.clear()


class IndicatorAnalysisOrchestrator:
    """Orchestrates all indicator analyses with optional LLM enhancement"""
    
    def __init__(self, llm_api_key: Optional[str] = None, enable_llm: bool = True):
        """Initialize orchestrator with analyzers"""
        self.rsi_analyzer = RSIAnalyzer()
        self.macd_analyzer = MACDAnalyzer()
        self.bollinger_analyzer = BollingerBandsAnalyzer()
        self.stochastic_analyzer = StochasticAnalyzer()
        
        self.enable_llm = enable_llm and llm_api_key is not None
        if self.enable_llm:
            self.llm_enhancer = LLMEnhancer(llm_api_key)
        else:
            self.llm_enhancer = None
    
    def analyze_all_indicators(self, indicators: Dict) -> Dict[str, IndicatorAnalysis]:
        """Analyze all indicators and return comprehensive results"""
        results = {}
        
        # RSI Analysis
        if indicators.get('rsi') is not None:
            rsi_analysis = self.rsi_analyzer.analyze(rsi_value=indicators['rsi'])
            if self.enable_llm:
                rsi_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    rsi_analysis, self.rsi_analyzer
                )
            results['rsi'] = rsi_analysis
        
        # MACD Analysis
        if all(k in indicators for k in ['macd', 'macds', 'macdh']):
            macd_analysis = self.macd_analyzer.analyze(
                macd=indicators['macd'],
                signal=indicators['macds'],
                histogram=indicators['macdh']
            )
            if self.enable_llm:
                macd_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    macd_analysis, self.macd_analyzer
                )
            results['macd'] = macd_analysis
        
        # Bollinger Bands Analysis
        if all(k in indicators for k in ['close', 'bb_upper', 'bb_middle', 'bb_lower']):
            bb_analysis = self.bollinger_analyzer.analyze(
                current_price=indicators['close'],
                upper=indicators['bb_upper'],
                middle=indicators['bb_middle'],
                lower=indicators['bb_lower']
            )
            if self.enable_llm:
                bb_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    bb_analysis, self.bollinger_analyzer
                )
            results['bollinger_bands'] = bb_analysis
        
        # Stochastic Analysis
        if all(k in indicators for k in ['stoch_k', 'stoch_d']):
            stoch_analysis = self.stochastic_analyzer.analyze(
                k_value=indicators['stoch_k'],
                d_value=indicators['stoch_d']
            )
            if self.enable_llm:
                stoch_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    stoch_analysis, self.stochastic_analyzer
                )
            results['stochastic'] = stoch_analysis
        
        return results
    
    def get_overall_recommendation(self, analyses: Dict[str, IndicatorAnalysis]) -> Dict:
        """Generate overall recommendation based on all indicators"""
        bullish_signals = sum(1 for a in analyses.values() if a.signal == Signal.BULLISH)
        bearish_signals = sum(1 for a in analyses.values() if a.signal == Signal.BEARISH)
        overbought_signals = sum(1 for a in analyses.values() if a.signal == Signal.OVERBOUGHT)
        oversold_signals = sum(1 for a in analyses.values() if a.signal == Signal.OVERSOLD)
        
        avg_strength = sum(a.strength for a in analyses.values()) / len(analyses) if analyses else 0
        
        if bullish_signals > bearish_signals + overbought_signals:
            action = "Buy"
            confidence = avg_strength
        elif bearish_signals > bullish_signals or overbought_signals > 1:
            action = "Sell"
            confidence = avg_strength
        else:
            action = "Hold"
            confidence = 0.5
        
        return {
            "action": action,
            "confidence": round(confidence, 2),
            "bullish_count": bullish_signals,
            "bearish_count": bearish_signals,
            "overbought_count": overbought_signals,
            "oversold_count": oversold_signals
        }
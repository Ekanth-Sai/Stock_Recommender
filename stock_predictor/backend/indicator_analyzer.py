from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import google.generativeai as genai
import pandas as pd


class Signal(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    OVERBOUGHT = "overbought"
    OVERSOLD = "oversold"


@dataclass
class IndicatorAnalysis:
    indicator_name: str
    current_value: float
    signal: Signal
    strength: float  
    rule_based_explanation: str
    llm_enhanced_explanation: Optional[str] = None
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class BaseIndicatorAnalyzer(ABC):    
    def __init__(self, indicator_name: str):
        self.indicator_name = indicator_name
    
    @abstractmethod
    def analyze(self, **kwargs) -> IndicatorAnalysis:
        pass
    
    @abstractmethod
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        pass


class RSIAnalyzer(BaseIndicatorAnalyzer):    
    OVERBOUGHT_THRESHOLD = 70
    OVERSOLD_THRESHOLD = 30
    
    def __init__(self):
        super().__init__("RSI")
    
    def analyze(self, rsi_value: float) -> IndicatorAnalysis:
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
        return (
            f"RSI Analysis: Value={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )


class MACDAnalyzer(BaseIndicatorAnalyzer):
    def __init__(self):
        super().__init__("MACD")
    
    def analyze(self, macd: float, signal: float, histogram: float) -> IndicatorAnalysis:
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
        return (
            f"MACD Analysis: Signal={analysis.signal.value}, "
            f"Strength={analysis.strength:.2f}. {analysis.rule_based_explanation}"
        )


class BollingerBandsAnalyzer(BaseIndicatorAnalyzer):    
    def __init__(self):
        super().__init__("Bollinger Bands")
    
    def analyze(self, current_price: float, upper: float, middle: float, lower: float) -> IndicatorAnalysis:
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
        band_width = upper - lower
        band_width_pct = (band_width / middle) * 100 if middle != 0 else 0
        
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
        return (
            f"Bollinger Bands Analysis: Signal={analysis.signal.value}, "
            f"Strength={analysis.strength:.2f}. {analysis.rule_based_explanation}"
        )

class StochasticAnalyzer(BaseIndicatorAnalyzer):
    OVERBOUGHT_THRESHOLD = 80
    OVERSOLD_THRESHOLD = 20
    
    def __init__(self):
        super().__init__("Stochastic Oscillator")
    
    def analyze(self, k_value: float, d_value: float) -> IndicatorAnalysis:
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
        return (
            f"Stochastic Analysis: %K={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )

class LLMEnhancer:
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.cache_enabled = True
        self._cache: Dict[str, str] = {}
    
    def enhance_analysis(self, analysis: IndicatorAnalysis, analyzer: BaseIndicatorAnalyzer) -> str:
        context = analyzer.get_context_for_llm(analysis)
        
        cache_key = f"{analysis.indicator_name}_{analysis.current_value}_{analysis.signal.value}"
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        prompt = self._build_prompt(context, analysis)
        
        try:
            response = self.model.generate_content(prompt)
            enhanced_explanation = response.text
            
            if self.cache_enabled:
                self._cache[cache_key] = enhanced_explanation
            
            print(f"Successfully enhanced explanation for {analysis.indicator_name} using Gemini.")
            
            return enhanced_explanation
        except Exception as e:
            print(f"LLM Enhancement failed: {e}")
            return analysis.rule_based_explanation  
    
    def _build_prompt(self, context: str, analysis: IndicatorAnalysis) -> str:
        
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
        self._cache.clear()

class IndicatorAnalysisOrchestrator:
    def __init__(self, llm_api_key: Optional[str] = None, enable_llm: bool = True):
        self.rsi_analyzer = RSIAnalyzer()
        self.macd_analyzer = MACDAnalyzer()
        self.bollinger_analyzer = BollingerBandsAnalyzer()
        self.stochastic_analyzer = StochasticAnalyzer()
        self.candle_analyzer = CandlePatternAnalyzer() 
        self.oipcr_analyzer = OIPCRAnalyzer()  
        self.breadth_analyzer = MarketBreadthAnalyzer()
        
        self.enable_llm = enable_llm and llm_api_key is not None
        if self.enable_llm:
            self.llm_enhancer = LLMEnhancer(llm_api_key)
        else:
            self.llm_enhancer = None
    
    def analyze_all_indicators(self, indicators: Dict, hist_data: Optional['pd.DataFrame'] = None) -> Dict[str, IndicatorAnalysis]:
        results = {}
        
        if indicators.get('rsi') is not None:
            rsi_analysis = self.rsi_analyzer.analyze(rsi_value=indicators['rsi'])
            if self.enable_llm:
                rsi_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    rsi_analysis, self.rsi_analyzer
                )
            results['rsi'] = rsi_analysis
        
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

        if hist_data is not None and not hist_data.empty:
            candle_analysis = self.candle_analyzer.analyze(df=hist_data)
            if self.enable_llm:
                candle_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    candle_analysis, self.candle_analyzer
                )
            results['candle_patterns'] = candle_analysis

        if indicators.get('oi_pcr') is not None:
            pcr_analysis = self.oipcr_analyzer.analyze(pcr_value=indicators['oi_pcr'])
            if self.enable_llm:
                pcr_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    pcr_analysis, self.oipcr_analyzer
                )
            results['oi_pcr'] = pcr_analysis
        
        if all(k in indicators for k in ['advances', 'declines']):
            breadth_analysis = self.breadth_analyzer.analyze(
                advances=indicators['advances'],
                declines=indicators['declines'],
                unchanged=indicators.get('unchanged', 0)
            )
            if self.enable_llm:
                breadth_analysis.llm_enhanced_explanation = self.llm_enhancer.enhance_analysis(
                    breadth_analysis, self.breadth_analyzer
                )
            results['market_breadth'] = breadth_analysis

        return results
    
    # def get_overall_recommendation(self, analyses: Dict[str, IndicatorAnalysis]) -> Dict:
    #     bullish_signals = sum(1 for a in analyses.values() if a.signal == Signal.BULLISH)
    #     bearish_signals = sum(1 for a in analyses.values() if a.signal == Signal.BEARISH)
    #     overbought_signals = sum(1 for a in analyses.values() if a.signal == Signal.OVERBOUGHT)
    #     oversold_signals = sum(1 for a in analyses.values() if a.signal == Signal.OVERSOLD)
        
    #     avg_strength = sum(a.strength for a in analyses.values()) / len(analyses) if analyses else 0
        
    #     if bullish_signals > bearish_signals + overbought_signals:
    #         action = "Buy"
    #         confidence = avg_strength
    #     elif bearish_signals > bullish_signals or overbought_signals > 1:
    #         action = "Sell"
    #         confidence = avg_strength
    #     else:
    #         action = "Hold"
    #         confidence = 0.5
        
    #     return {
    #         "action": action,
    #         "confidence": round(confidence, 2),
    #         "bullish_count": bullish_signals,
    #         "bearish_count": bearish_signals,
    #         "overbought_count": overbought_signals,
    #         "oversold_count": oversold_signals
    #     }

class CandlePatternAnalyzer(BaseIndicatorAnalyzer):
    def __init__(self):
        super().__init__("Candle Patterns")
    
    def analyze(self, df: 'pd.DataFrame') -> IndicatorAnalysis:
        patterns = self._detect_patterns(df)
        signal, strength, explanation, recommendations = self._evaluate_patterns(patterns)

        return IndicatorAnalysis(
            indicator_name = self.indicator_name,
            current_value = len(patterns),
            signal = signal,
            strength = strength,
            rule_based_explanation = explanation,
            recommendations = recommendations
        )
    
    def _detect_patterns(self, df: 'pd.DataFrame') -> list: 
        if len(df) < 3:
            return [] 
        
        patterns = []

        last_3 = df.tail(3)
        opens = last_3['Open'].values
        highs = last_3['High'].values
        lows = last_3['Low'].values
        closes = last_3['Close'].values

        o, h, l, c = opens[-1], high[-1], lows[-1], closes[-1]
        prev_o, prev_c = opens[-2], closes[-2]

        body = abs(c - o)
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l 

        if body < (h - l) * 0.1:
            patterns.append(("Doji", "Neutral", "Indecision in the market."))
        
        if c > o and lower_wick > body * 2 and upper_wick < body * 0.5:
            patterns.append(("Hammer", "bullish", "Potential reversal upward"))

        if o > c and upper_wick > body * 2 and lower_wick < body * 0.5:
            patterns.append(("Shooting Star", "bearish", "Potential reversal downward"))
        
        if c > o and prev_c < prev_o and c > prev_o and o < prev_c:
            patterns.append(("Bullish Engulfing", "bullish", "Strong bullish reversal"))

        if o > c and prev_o < prev_c and o > prev_c and c < prev_o:
            patterns.append(("Bearish Engulfing", "bearish", "Strong bearish reversal"))

        if len(df) >= 3:
            first_bearish = closes[-3] < opens[-3]
            middle_small = abs(closes[-2] - opens[-2]) < (highs[-2] - lows[-2]) * 0.3
            last_bullish = closes[-1] > opens[-1]

            if first_bearish and middle_small and last_bullish:
                patterns.append(("Morning Star", "bullish", "Strong bullish reversal pattern"))
        
        if len(df) >= 3:
            first_bullish = closes[-3] > opens[-3]
            middle_small = abs(closes[-2] - opens[-2]) < (highs[-2] - lows[-2]) * 0.3
            last_bearish = closes[-1] < opens[-1]
            
            if first_bullish and middle_small and last_bearish:
                patterns.append(("Evening Star", "bearish", "Strong bearish reversal pattern"))
        
        return patterns

    def _evaluate_patterns(self, patterns: list) -> tuple:
        if not patterns:
            signal = Signal.NEUTRAL
            strength = 0.5
            explanation = "No significant candlestick patterns detected in recent price action."
            recommendations = [
                "Monitor for pattern formation",
                "Wait for clearer signals",
                "Use other indicators for confirmation"
            ]
        else:
            # Count bullish vs bearish patterns
            bullish_count = sum(1 for p in patterns if p[1] == "bullish")
            bearish_count = sum(1 for p in patterns if p[1] == "bearish")
            
            if bullish_count > bearish_count:
                signal = Signal.BULLISH
                strength = min(bullish_count / len(patterns), 1.0)
                pattern_names = ", ".join([p[0] for p in patterns if p[1] == "bullish"])
                explanation = (
                    f"Detected {bullish_count} bullish pattern(s): {pattern_names}. "
                    f"These patterns suggest potential upward price movement."
                )
                recommendations = [
                    "Look for entry opportunities",
                    "Confirm with volume and other indicators",
                    "Set appropriate stop-loss levels"
                ]
            elif bearish_count > bullish_count:
                signal = Signal.BEARISH
                strength = min(bearish_count / len(patterns), 1.0)
                pattern_names = ", ".join([p[0] for p in patterns if p[1] == "bearish"])
                explanation = (
                    f"Detected {bearish_count} bearish pattern(s): {pattern_names}. "
                    f"These patterns suggest potential downward price movement."
                )
                recommendations = [
                    "Consider defensive positions",
                    "Avoid new long entries",
                    "Watch for confirmation before acting"
                ]
            else:
                signal = Signal.NEUTRAL
                strength = 0.6
                pattern_list = ", ".join([p[0] for p in patterns])
                explanation = (
                    f"Detected mixed patterns: {pattern_list}. "
                    f"Conflicting signals suggest consolidation or uncertainty."
                )
                recommendations = [
                    "Wait for clearer direction",
                    "Use other indicators for confirmation",
                    "Avoid aggressive positions"
                ]
        
        return signal, strength, explanation, recommendations

    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        return (
            f"Candle Pattern Analysis: {analysis.current_value} patterns(s) detected, "
            f"Signal = {analysis.signal.value}, Strength = {analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )

class OIPCRAnalyzer(BaseIndicatorAnalyzer):
    def __init__(self):
        super().__init__("OI PCR")
    
    def analyze(self, pcr_value: float) -> IndicatorAnalysis:
        signal, strength, explanation, recommendations = self._evaluate_pcr(pcr_value)
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=pcr_value,
            signal=signal,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_pcr(self, pcr: float) -> tuple:
        if pcr > 1.5:
            strength = min((pcr - 1.5) / 0.5, 1.0)
            signal = Signal.BULLISH
            explanation = (
                f"OI PCR is at {pcr:.2f}, significantly above 1.5. "
                f"High put concentration suggests market participants expect a bottom, indicating bullish sentiment."
            )
            recommendations = [
                "Strong bullish sentiment indicated",
                "Look for long entry opportunities",
                "Market may be oversold and ready for bounce"
            ]
        elif pcr < 0.7:
            strength = min((0.7 - pcr) / 0.3, 1.0)
            signal = Signal.BEARISH
            explanation = (
                f"OI PCR is at {pcr:.2f}, below 0.7. "
                f"Low put concentration suggests excessive call buying, indicating potential market top."
            )
            recommendations = [
                "Bearish sentiment indicated",
                "Consider profit booking",
                "Market may be overbought"
            ]
        elif pcr >= 1.0 and pcr <= 1.3:
            strength = 0.7
            signal = Signal.NEUTRAL
            explanation = (
                f"OI PCR is at {pcr:.2f}, in the balanced zone. "
                f"Indicates neutral market sentiment with no strong directional bias."
            )
            recommendations = [
                "Balanced market sentiment",
                "Wait for clearer signals",
                "Monitor for PCR changes"
            ]
        else:
            strength = 0.6
            signal = Signal.NEUTRAL
            explanation = (
                f"OI PCR is at {pcr:.2f}. "
                f"Market sentiment is moderately balanced."
            )
            recommendations = [
                "Monitor for trend development",
                "Combine with other indicators",
                "Maintain cautious approach"
            ]
        
        return signal, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        return (
            f"OI PCR Analysis: Value={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )

class MarketBreadthAnalyzer(BaseIndicatorAnalyzer):
    def __init__(self):
        super().__init__("Market Breadth")
    
    def analyze(self, advances: int, declines: int, unchanged: int = 0) -> IndicatorAnalysis:
        signal, strength, explanation, recommendations = self._evaluate_breadth(
            advances, declines, unchanged
        )
        
        ad_ratio = advances / declines if declines > 0 else advances
        
        return IndicatorAnalysis(
            indicator_name=self.indicator_name,
            current_value=ad_ratio,
            signal=signal,
            strength=strength,
            rule_based_explanation=explanation,
            recommendations=recommendations
        )
    
    def _evaluate_breadth(self, advances: int, declines: int, unchanged: int) -> tuple:
        total = advances + declines + unchanged
        if total == 0:
            return Signal.NEUTRAL, 0.5, "No market breadth data available.", []
        
        advance_pct = (advances / total) * 100
        decline_pct = (declines / total) * 100
        ad_ratio = advances / declines if declines > 0 else advances
        
        if advance_pct > 70:
            strength = min((advance_pct - 70) / 30, 1.0)
            signal = Signal.BULLISH
            explanation = (
                f"Market breadth is strong with {advance_pct:.1f}% advancing stocks (A/D Ratio: {ad_ratio:.2f}). "
                f"Broad market participation indicates healthy bullish trend."
            )
            recommendations = [
                "Strong market breadth supports uptrend",
                "Broad-based rally in progress",
                "Good environment for long positions"
            ]
        elif decline_pct > 70:
            strength = min((decline_pct - 70) / 30, 1.0)
            signal = Signal.BEARISH
            explanation = (
                f"Market breadth is weak with {decline_pct:.1f}% declining stocks (A/D Ratio: {ad_ratio:.2f}). "
                f"Broad selling pressure indicates bearish market conditions."
            )
            recommendations = [
                "Weak market breadth signals broad selling",
                "Defensive positioning recommended",
                "Avoid aggressive long entries"
            ]
        elif ad_ratio > 1.5:
            strength = 0.7
            signal = Signal.BULLISH
            explanation = (
                f"Positive market breadth with A/D ratio of {ad_ratio:.2f}. "
                f"More stocks advancing than declining, showing bullish undertone."
            )
            recommendations = [
                "Positive breadth supports rally",
                "Look for quality long setups",
                "Monitor for breadth deterioration"
            ]
        elif ad_ratio < 0.67:
            strength = 0.7
            signal = Signal.BEARISH
            explanation = (
                f"Negative market breadth with A/D ratio of {ad_ratio:.2f}. "
                f"More stocks declining than advancing, showing bearish pressure."
            )
            recommendations = [
                "Negative breadth warns of weakness",
                "Be cautious with new positions",
                "Consider hedging strategies"
            ]
        else:
            strength = 0.5
            signal = Signal.NEUTRAL
            explanation = (
                f"Balanced market breadth with A/D ratio of {ad_ratio:.2f}. "
                f"Equal distribution of advancing and declining stocks."
            )
            recommendations = [
                "Neutral breadth indicates consolidation",
                "Wait for breadth to confirm direction",
                "Use stock-specific analysis"
            ]
        
        return signal, strength, explanation, recommendations
    
    def get_context_for_llm(self, analysis: IndicatorAnalysis) -> str:
        return (
            f"Market Breadth Analysis: A/D Ratio={analysis.current_value:.2f}, "
            f"Signal={analysis.signal.value}, Strength={analysis.strength:.2f}. "
            f"{analysis.rule_based_explanation}"
        )
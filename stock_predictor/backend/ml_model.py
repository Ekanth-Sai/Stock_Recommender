import pandas as pd
import pandas_ta as ta
import os
from indicator_analyzer import IndicatorAnalysisOrchestrator, IndicatorAnalysis

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 2:
        return df
    
    try:
        df.ta.rsi(length=7, append=True)
    except Exception as e:
        print(f"Could not calculate RSI: {e}")
    
    try:
        df.ta.sma(length=20, append=True)
    except Exception as e:
        print(f"Could not calculate SMA: {e}")
    
    try:
        df.ta.macd(fast=8, slow=17, signal=6, append=True)
    except Exception as e:
        print(f"Could not calculate MACD: {e}")
    
    try:
        df.ta.bbands(append=True)
    except Exception as e:
        print(f"Could not calculate Bollinger Bands: {e}")
    
    try:
        df.ta.stoch(append=True)
    except Exception as e:
        print(f"Could not calculate Stochastic: {e}")

    return df


def get_prediction_with_confidence(data: pd.DataFrame, enable_llm: bool = True):
    latest_rsi = data["RSI_7"].iloc[-1] if "RSI_7" in data.columns and not data["RSI_7"].empty else None
    latest_macd = data["MACD_8_17_6"].iloc[-1] if "MACD_8_17_6" in data.columns and not data["MACD_8_17_6"].empty else None
    latest_macdh = data["MACDh_8_17_6"].iloc[-1] if "MACDh_8_17_6" in data.columns and not data["MACDh_8_17_6"].empty else None
    latest_macds = data["MACDS_8_17_6"].iloc[-1] if "MACDS_8_17_6" in data.columns and not data["MACDS_8_17_6"].empty else None
    latest_bb_lower = data["BBL_5_2.0_2.0"].iloc[-1] if "BBL_5_2.0_2.0" in data.columns and not data["BBL_5_2.0_2.0"].empty else None
    latest_bb_middle = data["BBM_5_2.0_2.0"].iloc[-1] if "BBM_5_2.0_2.0" in data.columns and not data["BBM_5_2.0_2.0"].empty else None
    latest_bb_upper = data["BBU_5_2.0_2.0"].iloc[-1] if "BBU_5_2.0_2.0" in data.columns and not data["BBU_5_2.0_2.0"].empty else None
    latest_stoch_k = data["STOCHk_14_3_3"].iloc[-1] if "STOCHk_14_3_3" in data.columns and not data["STOCHk_14_3_3"].empty else None
    latest_stoch_d = data["STOCHd_14_3_3"].iloc[-1] if "STOCHd_14_3_3" in data.columns and not data["STOCHd_14_3_3"].empty else None
    latest_close = data["Close"].iloc[-1] if "Close" in data.columns and not data["Close"].empty else None
    
    indicators = {
        'rsi': latest_rsi,
        'macd': latest_macd,
        'macds': latest_macds,
        'macdh': latest_macdh,
        'bb_upper': latest_bb_upper,
        'bb_middle': latest_bb_middle,
        'bb_lower': latest_bb_lower,
        'stoch_k': latest_stoch_k,
        'stoch_d': latest_stoch_d,
        'close': latest_close,
        # NEW - These would typically come from NSE/BSE APIs
        # 'oi_pcr': 1.2,  # Placeholder - fetch from NSE options chain
        # 'advances': 1500,  # Placeholder - fetch from market breadth data
        # 'declines': 1000,  # Placeholder
        # 'unchanged': 100,  # Placeholder
    }

    indicators = {k: v for k, v in indicators.items() if v is not None and not pd.isna(v)}
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    orchestrator = IndicatorAnalysisOrchestrator(
        llm_api_key=gemini_api_key,
        enable_llm=enable_llm and gemini_api_key is not None
    )

    analyses = orchestrator.analyze_all_indicators(indicators)
    
    # overall_recommendation = orchestrator.get_overall_recommendation(analyses)
    
    response = {
        # "action": overall_recommendation["action"],
        # "confidence": overall_recommendation["confidence"],
        "rsi": round(latest_rsi, 2) if latest_rsi is not None and not pd.isna(latest_rsi) else None,
        "macd": round(latest_macd, 2) if latest_macd is not None and not pd.isna(latest_macd) else None,
        "macdh": round(latest_macdh, 2) if latest_macdh is not None and not pd.isna(latest_macdh) else None,
        "macds": round(latest_macds, 2) if latest_macds is not None and not pd.isna(latest_macds) else None,
        "bb_lower": round(latest_bb_lower, 2) if latest_bb_lower is not None and not pd.isna(latest_bb_lower) else None,
        "bb_middle": round(latest_bb_middle, 2) if latest_bb_middle is not None and not pd.isna(latest_bb_middle) else None,
        "bb_upper": round(latest_bb_upper, 2) if latest_bb_upper is not None and not pd.isna(latest_bb_upper) else None,
        "stoch_k": round(latest_stoch_k, 2) if latest_stoch_k is not None and not pd.isna(latest_stoch_k) else None,
        "stoch_d": round(latest_stoch_d, 2) if latest_stoch_d is not None and not pd.isna(latest_stoch_d) else None,
    }
    
    response["detailed_analyses"] = _format_analyses_for_frontend(analyses)
    # response["signal_summary"] = {
    #     "bullish_signals": overall_recommendation["bullish_count"],
    #     "bearish_signals": overall_recommendation["bearish_count"],
    #     "overbought_signals": overall_recommendation["overbought_count"],
    #     "oversold_signals": overall_recommendation["oversold_count"]
    # }
    
    return response


def _format_analyses_for_frontend(analyses: dict) -> dict:
    formatted = {}
    
    for indicator_key, analysis in analyses.items():
        formatted[indicator_key] = {
            "indicator_name": analysis.indicator_name,
            "current_value": round(analysis.current_value, 2),
            "signal": analysis.signal.value,
            "strength": round(analysis.strength, 2),
            "explanation": analysis.llm_enhanced_explanation or analysis.rule_based_explanation,
            "rule_based_explanation": analysis.rule_based_explanation,
            "recommendations": analysis.recommendations
        }
    
    return formatted
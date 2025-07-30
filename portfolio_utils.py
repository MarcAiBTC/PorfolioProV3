"""
Enhanced Portfolio Utilities Module - FIXED VERSION
===================================================

This module provides comprehensive portfolio management utilities with:
- FIXED Yahoo Finance data fetching with multiple fallback strategies
- Popular assets database with search functionality
- Advanced financial metrics calculation
- Portfolio analysis and recommendations
- Robust error handling and caching

Key fixes:
- Fixed yfinance API calls with proper error handling
- Added multiple fallback strategies for price fetching
- Implemented popular assets database
- Enhanced caching and validation
- Better logging and error recovery

Author: Enhanced by AI Assistant
"""

import os
import json
import logging
import time
import warnings
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional, Iterable, Union

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Try to import yfinance with better error handling
try:
    import yfinance as yf
    YF_AVAILABLE = True
    logger.info("yfinance successfully imported")
    
    # Test yfinance with a simple call
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        if test_info and len(test_info) > 5:
            logger.info("yfinance API test successful")
        else:
            logger.warning("yfinance API test returned limited data")
    except Exception as e:
        logger.warning(f"yfinance API test failed: {e}")
        
except ImportError as e:
    yf = None
    YF_AVAILABLE = False
    logger.error(f"yfinance not available: {e}")

# Try to import plotly for visualization helpers
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    px = None
    PLOTLY_AVAILABLE = False

# ============================================================================
# Popular Assets Database
# ============================================================================

POPULAR_ASSETS = {
    "stocks": {
        "Tech Giants": {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation", 
            "GOOGL": "Alphabet Inc. (Class A)",
            "GOOG": "Alphabet Inc. (Class C)",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc.",
            "CRM": "Salesforce Inc."
        },
        "Financial": {
            "JPM": "JPMorgan Chase & Co.",
            "BAC": "Bank of America Corp.",
            "WFC": "Wells Fargo & Company",
            "GS": "Goldman Sachs Group Inc.",
            "C": "Citigroup Inc.",
            "MS": "Morgan Stanley",
            "AXP": "American Express Company",
            "V": "Visa Inc.",
            "MA": "Mastercard Inc.",
            "PYPL": "PayPal Holdings Inc."
        },
        "Healthcare": {
            "JNJ": "Johnson & Johnson",
            "PFE": "Pfizer Inc.",
            "UNH": "UnitedHealth Group Inc.",
            "MRK": "Merck & Co. Inc.",
            "ABT": "Abbott Laboratories",
            "TMO": "Thermo Fisher Scientific Inc.",
            "DHR": "Danaher Corporation",
            "BMY": "Bristol-Myers Squibb Co.",
            "AMGN": "Amgen Inc.",
            "GILD": "Gilead Sciences Inc."
        },
        "Consumer": {
            "KO": "The Coca-Cola Company",
            "PEP": "PepsiCo Inc.",
            "WMT": "Walmart Inc.",
            "PG": "Procter & Gamble Co.",
            "HD": "The Home Depot Inc.",
            "MCD": "McDonald's Corporation",
            "NKE": "NIKE Inc.",
            "SBUX": "Starbucks Corporation",
            "DIS": "The Walt Disney Company",
            "COST": "Costco Wholesale Corporation"
        },
        "Energy": {
            "XOM": "Exxon Mobil Corporation",
            "CVX": "Chevron Corporation",
            "COP": "ConocoPhillips",
            "SLB": "Schlumberger Limited",
            "EOG": "EOG Resources Inc.",
            "PXD": "Pioneer Natural Resources Co.",
            "KMI": "Kinder Morgan Inc.",
            "OKE": "ONEOK Inc.",
            "WMB": "The Williams Companies Inc.",
            "EPD": "Enterprise Products Partners L.P."
        }
    },
    "etfs": {
        "Broad Market": {
            "SPY": "SPDR S&P 500 ETF Trust",
            "QQQ": "Invesco QQQ Trust",
            "IWM": "iShares Russell 2000 ETF",
            "VTI": "Vanguard Total Stock Market ETF",
            "ITOT": "iShares Core S&P Total US Stock Market ETF",
            "SCHA": "Schwab US Small-Cap ETF",
            "VTV": "Vanguard Value ETF",
            "VUG": "Vanguard Growth ETF",
            "MTUM": "Invesco MSCI USA Momentum Factor ETF",
            "QUAL": "iShares MSCI USA Quality Factor ETF"
        },
        "Sector ETFs": {
            "XLK": "Technology Select Sector SPDR Fund",
            "XLF": "Financial Select Sector SPDR Fund",
            "XLV": "Health Care Select Sector SPDR Fund",
            "XLE": "Energy Select Sector SPDR Fund",
            "XLI": "Industrial Select Sector SPDR Fund",
            "XLY": "Consumer Discretionary Select Sector SPDR Fund",
            "XLP": "Consumer Staples Select Sector SPDR Fund",
            "XLU": "Utilities Select Sector SPDR Fund",
            "XLB": "Materials Select Sector SPDR Fund",
            "XLRE": "Real Estate Select Sector SPDR Fund"
        },
        "International": {
            "VEA": "Vanguard Developed Markets ETF",
            "VWO": "Vanguard Emerging Markets ETF",
            "IEFA": "iShares Core MSCI EAFE IMI Index ETF",
            "EEM": "iShares MSCI Emerging Markets ETF",
            "FXI": "iShares China Large-Cap ETF",
            "EWJ": "iShares MSCI Japan ETF",
            "EWZ": "iShares MSCI Brazil ETF",
            "INDA": "iShares MSCI India ETF",
            "EWG": "iShares MSCI Germany ETF",
            "EWU": "iShares MSCI United Kingdom ETF"
        },
        "Bonds": {
            "AGG": "iShares Core US Aggregate Bond ETF",
            "BND": "Vanguard Total Bond Market ETF",
            "TLT": "iShares 20+ Year Treasury Bond ETF",
            "IEF": "iShares 7-10 Year Treasury Bond ETF",
            "SHY": "iShares 1-3 Year Treasury Bond ETF",
            "LQD": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
            "HYG": "iShares iBoxx $ High Yield Corporate Bond ETF",
            "EMB": "iShares J.P. Morgan USD Emerging Markets Bond ETF",
            "MUB": "iShares National Muni Bond ETF",
            "VTEB": "Vanguard Tax-Exempt Bond ETF"
        }
    },
    "crypto": {
        "Major Cryptocurrencies": {
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "BNB-USD": "Binance Coin",
            "XRP-USD": "XRP",
            "ADA-USD": "Cardano",
            "DOGE-USD": "Dogecoin",
            "MATIC-USD": "Polygon",
            "SOL-USD": "Solana",
            "DOT-USD": "Polkadot",
            "AVAX-USD": "Avalanche"
        },
        "Stablecoins": {
            "USDT-USD": "Tether",
            "USDC-USD": "USD Coin",
            "BUSD-USD": "Binance USD",
            "DAI-USD": "Dai",
            "TUSD-USD": "TrueUSD"
        }
    },
    "indices": {
        "US Indices": {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones Industrial Average",
            "^IXIC": "NASDAQ Composite",
            "^RUT": "Russell 2000",
            "^VIX": "CBOE Volatility Index"
        },
        "International": {
            "^FTSE": "FTSE 100",
            "^GDAXI": "DAX",
            "^FCHI": "CAC 40",
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng Index"
        }
    },
    "commodities": {
        "Precious Metals": {
            "GLD": "SPDR Gold Shares",
            "SLV": "iShares Silver Trust",
            "IAU": "iShares Gold Trust",
            "PALL": "Aberdeen Standard Physical Palladium Shares ETF",
            "PPLT": "Aberdeen Standard Physical Platinum Shares ETF"
        },
        "Energy": {
            "USO": "United States Oil Fund",
            "UNG": "United States Natural Gas Fund",
            "DBO": "Invesco DB Oil Fund",
            "UGA": "United States Gasoline Fund"
        },
        "Agriculture": {
            "CORN": "Teucrium Corn Fund",
            "WEAT": "Teucrium Wheat Fund",
            "SOYB": "Teucrium Soybean Fund",
            "DBA": "Invesco DB Agriculture Fund"
        }
    }
}

# ============================================================================
# Configuration Constants
# ============================================================================

# Cache duration for price data (in minutes)
CACHE_DURATION_MINUTES: int = 5

# Risk-free rate for Sharpe ratio calculations (as decimal)
RISK_FREE_RATE: float = 0.02  # 2% annual

# Default benchmark tickers
DEFAULT_BENCHMARKS: List[str] = ["^GSPC", "^IXIC"]  # S&P 500, NASDAQ

# Maximum number of tickers to fetch at once
MAX_BATCH_SIZE: int = 20  # Reduced for better reliability

# Request timeout and retry configuration
REQUEST_TIMEOUT: int = 30
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0

# ============================================================================
# Global Cache Variables
# ============================================================================

# In-memory cache for current prices
PRICE_CACHE: Dict[str, Dict[str, float]] = {}
CACHE_TIMESTAMPS: Dict[str, float] = {}

# Cache for historical price data
HIST_PRICES_CACHE: Dict[Tuple[str, str], pd.Series] = {}

# Cache for benchmark data
BENCHMARK_CACHE: Dict[str, pd.DataFrame] = {}

# ============================================================================
# Popular Assets Functions
# ============================================================================

def get_popular_assets_flat() -> Dict[str, str]:
    """
    Get a flat dictionary of all popular assets for easy searching.
    
    Returns
    -------
    Dict[str, str]
        Mapping from ticker to full name
    """
    flat_assets = {}
    
    for asset_class, categories in POPULAR_ASSETS.items():
        for category, assets in categories.items():
            flat_assets.update(assets)
    
    return flat_assets

def search_popular_assets(query: str, limit: int = 50) -> List[Dict[str, str]]:
    """
    Search popular assets by ticker or name.
    
    Parameters
    ----------
    query : str
        Search query
    limit : int, default 50
        Maximum number of results
        
    Returns
    -------
    List[Dict[str, str]]
        List of matching assets with ticker, name, and category
    """
    if not query or len(query.strip()) < 1:
        return []
    
    query = query.upper().strip()
    results = []
    
    for asset_class, categories in POPULAR_ASSETS.items():
        for category, assets in categories.items():
            for ticker, name in assets.items():
                # Search in ticker or name
                if (query in ticker.upper() or 
                    query in name.upper() or
                    any(word.startswith(query) for word in name.upper().split())):
                    
                    results.append({
                        "ticker": ticker,
                        "name": name,
                        "category": f"{asset_class.title()} - {category}",
                        "asset_class": asset_class
                    })
                    
                    if len(results) >= limit:
                        return results
    
    return results

def get_assets_by_category(asset_class: str = None, category: str = None) -> List[Dict[str, str]]:
    """
    Get assets filtered by class and/or category.
    
    Parameters
    ----------
    asset_class : str, optional
        Asset class filter (stocks, etfs, crypto, etc.)
    category : str, optional
        Category filter within asset class
        
    Returns
    -------
    List[Dict[str, str]]
        Filtered list of assets
    """
    results = []
    
    assets_to_search = POPULAR_ASSETS
    if asset_class:
        assets_to_search = {asset_class: POPULAR_ASSETS.get(asset_class, {})}
    
    for ac, categories in assets_to_search.items():
        categories_to_search = categories
        if category:
            categories_to_search = {category: categories.get(category, {})}
        
        for cat, assets in categories_to_search.items():
            for ticker, name in assets.items():
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "category": f"{ac.title()} - {cat}",
                    "asset_class": ac
                })
    
    return results

# ============================================================================
# File System Setup
# ============================================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "user_data")
PORTFOLIO_DIR = os.path.join(BASE_DIR, "portfolios")

def _ensure_portfolio_dir() -> None:
    """Ensure the portfolio storage directory exists."""
    try:
        os.makedirs(PORTFOLIO_DIR, exist_ok=True)
        logger.debug(f"Portfolio directory ensured: {PORTFOLIO_DIR}")
    except Exception as e:
        logger.error(f"Failed to create portfolio directory: {e}")
        raise

# ============================================================================
# FIXED Price Fetching and Caching
# ============================================================================

def fetch_current_prices_robust(tickers: Iterable[str]) -> Dict[str, float]:
    """
    FIXED: Robust price fetching with multiple fallback strategies.
    
    Parameters
    ----------
    tickers : Iterable[str]
        Asset symbols to fetch
        
    Returns
    -------
    Dict[str, float]
        Mapping from ticker to current price (NaN for failures)
    """
    if not YF_AVAILABLE:
        logger.warning("yfinance not available - returning NaN prices")
        return {str(t).upper(): np.nan for t in tickers}
    
    tickers_list = [str(t).upper().strip() for t in tickers if str(t).strip()]
    prices = {t: np.nan for t in tickers_list}
    
    if not tickers_list:
        return prices
    
    logger.info(f"Fetching prices for {len(tickers_list)} tickers: {tickers_list[:5]}...")
    
    # Strategy 1: Try individual ticker fetching first (most reliable)
    for ticker in tickers_list:
        try:
            price = _fetch_single_price_with_fallbacks(ticker)
            if not pd.isna(price) and price > 0:
                prices[ticker] = price
                logger.debug(f"✅ {ticker}: ${price:.2f}")
            else:
                logger.debug(f"❌ {ticker}: Failed to get valid price")
        except Exception as e:
            logger.debug(f"❌ {ticker}: Error - {str(e)}")
            continue
    
    # Strategy 2: For remaining failed tickers, try batch download
    failed_tickers = [t for t, p in prices.items() if pd.isna(p)]
    if failed_tickers and len(failed_tickers) <= 10:  # Only for small batches
        try:
            logger.debug(f"Trying batch download for {len(failed_tickers)} failed tickers...")
            batch_prices = _fetch_batch_prices(failed_tickers)
            for ticker, price in batch_prices.items():
                if not pd.isna(price) and price > 0:
                    prices[ticker] = price
                    logger.debug(f"✅ Batch {ticker}: ${price:.2f}")
        except Exception as e:
            logger.debug(f"Batch download failed: {e}")
    
    successful_count = sum(1 for p in prices.values() if not pd.isna(p))
    logger.info(f"Successfully fetched {successful_count}/{len(tickers_list)} prices")
    
    return prices

def _fetch_single_price_with_fallbacks(ticker: str) -> float:
    """
    Fetch single ticker price with multiple fallback methods.
    
    Parameters
    ----------
    ticker : str
        Single ticker symbol
        
    Returns
    -------
    float
        Current price or NaN if failed
    """
    methods = [
        ("fast_info", _get_price_from_fast_info),
        ("history_1d", _get_price_from_history),
        ("info", _get_price_from_info),
        ("download_1d", _get_price_from_download)
    ]
    
    for method_name, method_func in methods:
        try:
            price = method_func(ticker)
            if not pd.isna(price) and price > 0:
                logger.debug(f"✅ {ticker}: ${price:.2f} (via {method_name})")
                return price
        except Exception as e:
            logger.debug(f"Method {method_name} failed for {ticker}: {e}")
            continue
    
    return np.nan

def _get_price_from_fast_info(ticker: str) -> float:
    """Get price from yfinance fast_info."""
    ticker_obj = yf.Ticker(ticker)
    fast_info = ticker_obj.fast_info
    
    if hasattr(fast_info, 'last_price') and fast_info.last_price:
        return float(fast_info.last_price)
    elif hasattr(fast_info, 'previousClose') and fast_info.previousClose:
        return float(fast_info.previousClose)
    else:
        raise ValueError("No valid price in fast_info")

def _get_price_from_history(ticker: str) -> float:
    """Get price from recent history."""
    ticker_obj = yf.Ticker(ticker)
    hist = ticker_obj.history(period="2d", interval="1d")
    
    if hist.empty:
        raise ValueError("No history data")
    
    # Try Adj Close first, then Close
    if 'Adj Close' in hist.columns and not hist['Adj Close'].isna().all():
        return float(hist['Adj Close'].iloc[-1])
    elif 'Close' in hist.columns and not hist['Close'].isna().all():
        return float(hist['Close'].iloc[-1])
    else:
        raise ValueError("No valid close price in history")

def _get_price_from_info(ticker: str) -> float:
    """Get price from ticker info."""
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info
    
    if not info:
        raise ValueError("No info data")
    
    # Try various price fields
    price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose', 'open']
    for field in price_fields:
        if field in info and info[field] and not pd.isna(info[field]):
            return float(info[field])
    
    raise ValueError("No valid price in info")

def _get_price_from_download(ticker: str) -> float:
    """Get price from yf.download."""
    data = yf.download(ticker, period="2d", interval="1d", progress=False, show_errors=False)
    
    if data.empty:
        raise ValueError("No download data")
    
    if 'Adj Close' in data.columns and not data['Adj Close'].isna().all():
        return float(data['Adj Close'].iloc[-1])
    elif 'Close' in data.columns and not data['Close'].isna().all():
        return float(data['Close'].iloc[-1])
    else:
        raise ValueError("No valid close price in download")

def _fetch_batch_prices(tickers: List[str]) -> Dict[str, float]:
    """
    Fetch prices in batch mode.
    
    Parameters
    ----------
    tickers : List[str]
        List of tickers
        
    Returns
    -------
    Dict[str, float]
        Price mapping
    """
    prices = {t: np.nan for t in tickers}
    
    if len(tickers) > 10:  # Avoid large batches
        return prices
    
    try:
        tickers_str = " ".join(tickers)
        data = yf.download(
            tickers=tickers_str,
            period="2d",
            interval="1d", 
            progress=False,
            show_errors=False,
            group_by='ticker'
        )
        
        if data.empty:
            return prices
        
        # Handle different data structures
        if isinstance(data.columns, pd.MultiIndex):
            # Multiple tickers
            for ticker in tickers:
                try:
                    if (ticker, 'Adj Close') in data.columns:
                        price_series = data[(ticker, 'Adj Close')].dropna()
                    elif (ticker, 'Close') in data.columns:
                        price_series = data[(ticker, 'Close')].dropna()
                    else:
                        continue
                    
                    if not price_series.empty:
                        prices[ticker] = float(price_series.iloc[-1])
                except Exception:
                    continue
        else:
            # Single ticker
            if len(tickers) == 1:
                ticker = tickers[0]
                try:
                    if 'Adj Close' in data.columns:
                        price_series = data['Adj Close'].dropna()
                    elif 'Close' in data.columns:
                        price_series = data['Close'].dropna()
                    else:
                        return prices
                    
                    if not price_series.empty:
                        prices[ticker] = float(price_series.iloc[-1])
                except Exception:
                    pass
        
        return prices
        
    except Exception as e:
        logger.debug(f"Batch fetch failed: {e}")
        return prices

def get_cached_prices(
    tickers: Iterable[str], 
    cache_duration_minutes: int = CACHE_DURATION_MINUTES
) -> Dict[str, float]:
    """
    Get current prices with intelligent caching.
    
    Parameters
    ----------
    tickers : Iterable[str]
        Asset symbols to fetch
    cache_duration_minutes : int, default CACHE_DURATION_MINUTES
        Cache validity duration in minutes
        
    Returns
    -------
    Dict[str, float]
        Mapping from ticker to current price
    """
    tickers_list = [str(t).upper().strip() for t in tickers if str(t).strip()]
    
    if not tickers_list or not YF_AVAILABLE:
        return {ticker: np.nan for ticker in tickers_list}
    
    # Create cache key
    cache_key = ",".join(sorted(tickers_list))
    now = time.time()
    
    # Check if we have valid cached data
    if cache_key in PRICE_CACHE:
        cache_age = now - CACHE_TIMESTAMPS.get(cache_key, 0.0)
        if cache_age < cache_duration_minutes * 60:
            logger.debug(f"Using cached prices for {len(tickers_list)} tickers")
            return PRICE_CACHE[cache_key]
    
    # Fetch fresh data using robust method
    logger.debug(f"Fetching fresh prices for {len(tickers_list)} tickers")
    prices = fetch_current_prices_robust(tickers_list)
    
    # Update cache
    PRICE_CACHE[cache_key] = prices
    CACHE_TIMESTAMPS[cache_key] = now
    
    return prices

# For backward compatibility
fetch_current_prices = fetch_current_prices_robust

# ============================================================================
# Historical Data and Advanced Metrics (Enhanced)
# ============================================================================

def fetch_historical_series(
    ticker: str, 
    period: str = "6mo", 
    interval: str = "1d"
) -> pd.Series:
    """
    ENHANCED: Fetch historical price series with better error handling.
    
    Parameters
    ----------
    ticker : str
        Asset symbol
    period : str, default "6mo"
        Historical period
    interval : str, default "1d"
        Data interval
        
    Returns
    -------
    pd.Series
        Historical adjusted close prices
    """
    if not YF_AVAILABLE:
        return pd.Series(dtype=float)
    
    cache_key = (ticker.upper(), period)
    
    # Check cache
    if cache_key in HIST_PRICES_CACHE:
        return HIST_PRICES_CACHE[cache_key]
    
    try:
        logger.debug(f"Fetching historical data for {ticker} ({period})")
        
        # Try multiple approaches for historical data
        ticker_obj = yf.Ticker(ticker)
        
        # Method 1: Use history() method
        try:
            data = ticker_obj.history(period=period, interval=interval)
            if not data.empty:
                if 'Adj Close' in data.columns:
                    series = data['Adj Close'].dropna()
                elif 'Close' in data.columns:
                    series = data['Close'].dropna()
                else:
                    series = pd.Series(dtype=float)
                
                if not series.empty:
                    HIST_PRICES_CACHE[cache_key] = series
                    logger.debug(f"✅ Historical data for {ticker}: {len(series)} points")
                    return series
        except Exception as e:
            logger.debug(f"History method failed for {ticker}: {e}")
        
        # Method 2: Use download as fallback
        try:
            data = yf.download(
                ticker, 
                period=period, 
                interval=interval, 
                progress=False,
                show_errors=False
            )
            
            if not data.empty:
                if 'Adj Close' in data.columns:
                    series = data['Adj Close'].dropna()
                elif 'Close' in data.columns:
                    series = data['Close'].dropna()
                else:
                    series = pd.Series(dtype=float)
                
                if not series.empty:
                    HIST_PRICES_CACHE[cache_key] = series
                    logger.debug(f"✅ Historical data for {ticker} (fallback): {len(series)} points")
                    return series
        except Exception as e:
            logger.debug(f"Download method failed for {ticker}: {e}")
        
        # If all methods fail, return empty series
        series = pd.Series(dtype=float)
        HIST_PRICES_CACHE[cache_key] = series
        logger.debug(f"❌ No historical data available for {ticker}")
        return series
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        empty_series = pd.Series(dtype=float)
        HIST_PRICES_CACHE[cache_key] = empty_series
        return empty_series

# ============================================================================
# Enhanced Validation Functions
# ============================================================================

def validate_tickers_enhanced(tickers: Iterable[str]) -> Dict[str, Dict[str, Union[bool, str]]]:
    """
    Enhanced ticker validation with detailed information.
    
    Parameters
    ----------
    tickers : Iterable[str]
        Ticker symbols to validate
        
    Returns
    -------
    Dict[str, Dict[str, Union[bool, str]]]
        Detailed validation results
    """
    results = {}
    
    if not YF_AVAILABLE:
        logger.warning("yfinance not available for ticker validation")
        return {str(t).upper(): {"valid": False, "reason": "yfinance unavailable"} for t in tickers}
    
    popular_assets = get_popular_assets_flat()
    
    for ticker in tickers:
        ticker_clean = str(ticker).upper().strip()
        if not ticker_clean:
            results[ticker_clean] = {"valid": False, "reason": "empty ticker"}
            continue
        
        # Check if it's in popular assets first
        if ticker_clean in popular_assets:
            results[ticker_clean] = {
                "valid": True, 
                "reason": "popular asset",
                "name": popular_assets[ticker_clean]
            }
            continue
        
        # Validate with yfinance
        try:
            # Try to get basic info
            ticker_obj = yf.Ticker(ticker_clean)
            
            # Method 1: Try fast_info
            try:
                fast_info = ticker_obj.fast_info
                if hasattr(fast_info, 'last_price') or hasattr(fast_info, 'previousClose'):
                    results[ticker_clean] = {
                        "valid": True,
                        "reason": "validated via fast_info"
                    }
                    continue
            except Exception:
                pass
            
            # Method 2: Try getting recent history
            try:
                hist = ticker_obj.history(period="5d")
                if not hist.empty and len(hist) > 0:
                    results[ticker_clean] = {
                        "valid": True,
                        "reason": "validated via history"
                    }
                    continue
            except Exception:
                pass
            
            # Method 3: Try info (slower but comprehensive)
            try:
                info = ticker_obj.info
                if info and len(info) > 5:  # Valid tickers return substantial info
                    name = info.get('longName', info.get('shortName', ''))
                    results[ticker_clean] = {
                        "valid": True,
                        "reason": "validated via info",
                        "name": name
                    }
                    continue
            except Exception:
                pass
            
            # If all methods fail
            results[ticker_clean] = {
                "valid": False,
                "reason": "not found in any yfinance method"
            }
                
        except Exception as e:
            results[ticker_clean] = {
                "valid": False,
                "reason": f"validation error: {str(e)}"
            }
    
    valid_count = sum(1 for r in results.values() if r.get("valid", False))
    logger.info(f"Validated {valid_count}/{len(results)} tickers successfully")
    
    return results

# ============================================================================
# Portfolio File Operations (Enhanced)
# ============================================================================

def list_portfolios(username: str) -> List[str]:
    """
    List portfolio files for a given user, sorted by modification time.
    
    Parameters
    ----------
    username : str
        The user's username
        
    Returns
    -------
    List[str]
        List of portfolio filenames sorted by modification time (newest first)
    """
    _ensure_portfolio_dir()
    files = []
    
    try:
        for fname in os.listdir(PORTFOLIO_DIR):
            if not (fname.endswith(".csv") or fname.endswith(".json")):
                continue
            if fname.startswith(f"{username}_"):
                files.append(fname)
        
        # Sort by modification time (newest first)
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(PORTFOLIO_DIR, f)), 
            reverse=True
        )
        
        logger.debug(f"Found {len(files)} portfolios for user {username}")
        return files
        
    except Exception as e:
        logger.error(f"Error listing portfolios for {username}: {e}")
        return []

def save_portfolio(
    username: str,
    df: pd.DataFrame,
    *,
    fmt: str = "csv",
    overwrite: bool = True,
    keep_history: bool = True,
) -> str:
    """
    Save a portfolio to disk with optional history keeping.
    
    Parameters
    ----------
    username : str
        User identifier
    df : pd.DataFrame
        Portfolio data to save
    fmt : str, default "csv"
        File format ("csv" or "json")
    overwrite : bool, default True
        Whether to overwrite the current file
    keep_history : bool, default True
        Whether to keep a timestamped copy
        
    Returns
    -------
    str
        Path to the saved file
    """
    _ensure_portfolio_dir()
    
    if fmt not in {"csv", "json"}:
        raise ValueError(f"Unsupported format: {fmt}")
    
    try:
        # Save current file
        current_fname = f"{username}_current.{fmt}"
        current_path = os.path.join(PORTFOLIO_DIR, current_fname)
        
        if overwrite:
            if fmt == "csv":
                df.to_csv(current_path, index=False)
            else:
                df.to_json(current_path, orient="records", indent=2)
            logger.info(f"Saved current portfolio for {username}: {current_path}")
        
        written_path = current_path
        
        # Save timestamped copy if requested
        if keep_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_fname = f"{username}_{timestamp}.{fmt}"
            snapshot_path = os.path.join(PORTFOLIO_DIR, snapshot_fname)
            
            if fmt == "csv":
                df.to_csv(snapshot_path, index=False)
            else:
                df.to_json(snapshot_path, orient="records", indent=2)
            
            written_path = snapshot_path
            logger.info(f"Saved portfolio snapshot: {snapshot_path}")
        
        return written_path
        
    except Exception as e:
        logger.error(f"Error saving portfolio for {username}: {e}")
        raise

def load_portfolio(username: str, filename: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Load a portfolio from disk.
    
    Parameters
    ----------
    username : str
        User identifier
    filename : str, optional
        Specific filename to load. If None, loads most recent.
        
    Returns
    -------
    Optional[pd.DataFrame]
        Loaded portfolio data or None if failed
    """
    _ensure_portfolio_dir()
    
    try:
        files = list_portfolios(username)
        if not files:
            logger.info(f"No portfolios found for user {username}")
            return None
        
        target = filename if filename is not None else files[0]
        fpath = os.path.join(PORTFOLIO_DIR, target)
        
        if not os.path.isfile(fpath):
            logger.error(f"Portfolio file not found: {fpath}")
            return None
        
        ext = os.path.splitext(fpath)[1].lower()
        
        if ext == ".csv":
            df = pd.read_csv(fpath)
        elif ext == ".json":
            df = pd.read_json(fpath)
        else:
            logger.error(f"Unsupported file format: {ext}")
            return None
        
        logger.info(f"Loaded portfolio for {username}: {len(df)} assets from {target}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading portfolio for {username}: {e}")
        return None

# ============================================================================
# Basic Portfolio Metrics (Enhanced)
# ============================================================================

def compute_metrics(df: pd.DataFrame, prices: Dict[str, float]) -> pd.DataFrame:
    """
    Compute basic portfolio metrics with enhanced error handling.
    
    Parameters
    ----------
    df : pd.DataFrame
        Portfolio data with Ticker, Purchase Price, Quantity columns
    prices : Dict[str, float]
        Current prices by ticker
        
    Returns
    -------
    pd.DataFrame
        DataFrame with computed basic metrics
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    try:
        result_df = df.copy()
        
        # Validate required columns
        required_cols = ['Ticker', 'Purchase Price', 'Quantity']
        missing_cols = [col for col in required_cols if col not in result_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean data
        result_df['Ticker'] = result_df['Ticker'].astype(str).str.upper().str.strip()
        result_df['Purchase Price'] = pd.to_numeric(result_df['Purchase Price'], errors='coerce')
        result_df['Quantity'] = pd.to_numeric(result_df['Quantity'], errors='coerce')
        
        # Remove invalid rows
        result_df = result_df.dropna(subset=['Ticker', 'Purchase Price', 'Quantity'])
        result_df = result_df[result_df['Purchase Price'] > 0]
        result_df = result_df[result_df['Quantity'] > 0]
        
        if result_df.empty:
            logger.warning("No valid data after cleaning")
            return pd.DataFrame()
        
        # Current prices
        result_df['Current Price'] = result_df['Ticker'].apply(
            lambda t: prices.get(str(t).upper(), np.nan)
        )
        
        # Basic calculations
        result_df['Total Value'] = result_df['Current Price'] * result_df['Quantity']
        result_df['Cost Basis'] = result_df['Purchase Price'] * result_df['Quantity']
        result_df['P/L'] = result_df['Total Value'] - result_df['Cost Basis']
        
        # P/L percentage - handle division by zero
        result_df['P/L %'] = np.where(
            result_df['Cost Basis'] > 0,
            (result_df['Total Value'] / result_df['Cost Basis'] - 1.0) * 100.0,
            np.nan
        )
        
        # Portfolio weights
        total_value = result_df['Total Value'].sum()
        if total_value > 0:
            result_df['Weight %'] = result_df['Total Value'] / total_value * 100.0
        else:
            result_df['Weight %'] = np.nan
        
        # Add price change indicators
        result_df['Price Change'] = result_df['Current Price'] - result_df['Purchase Price']
        result_df['Price Change %'] = np.where(
            result_df['Purchase Price'] > 0,
            (result_df['Current Price'] / result_df['Purchase Price'] - 1.0) * 100.0,
            np.nan
        )
        
        logger.info(f"Computed metrics for {len(result_df)} assets")
        return result_df
        
    except Exception as e:
        logger.error(f"Error computing basic metrics: {e}")
        return df.copy() if df is not None else pd.DataFrame()

# ============================================================================
# Advanced Financial Metrics (Enhanced)
# ============================================================================

def compute_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    Compute Relative Strength Index (RSI) with better error handling.
    
    Parameters
    ----------
    prices : pd.Series
        Historical price series
    period : int, default 14
        RSI calculation period
        
    Returns
    -------
    float
        Current RSI value
    """
    if prices is None or len(prices) < period + 1:
        return np.nan
    
    try:
        # Calculate price changes
        delta = prices.diff().dropna()
        
        if delta.empty or len(delta) < period:
            return np.nan
        
        # Separate gains and losses
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        
        # Calculate average gains and losses using exponential moving average
        avg_gain = gains.ewm(alpha=1.0/period, min_periods=period).mean()
        avg_loss = losses.ewm(alpha=1.0/period, min_periods=period).mean()
        
        # Avoid division by zero
        if avg_loss.iloc[-1] == 0:
            return 100.0 if avg_gain.iloc[-1] > 0 else 50.0
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        final_rsi = float(rsi.iloc[-1]) if not rsi.empty else np.nan
        
        # Validate RSI range
        if pd.isna(final_rsi) or final_rsi < 0 or final_rsi > 100:
            return np.nan
        
        return final_rsi
        
    except Exception as e:
        logger.debug(f"Error computing RSI: {e}")
        return np.nan

def compute_volatility(prices: pd.Series, annualize: bool = True) -> float:
    """
    Compute price volatility with enhanced error handling.
    
    Parameters
    ----------
    prices : pd.Series
        Historical price series
    annualize : bool, default True
        Whether to annualize the volatility
        
    Returns
    -------
    float
        Volatility as percentage
    """
    if prices is None or len(prices) < 2:
        return np.nan
    
    try:
        # Calculate daily returns
        returns = prices.pct_change().dropna()
        
        if returns.empty or len(returns) < 2:
            return np.nan
        
        # Remove infinite values
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        if returns.empty:
            return np.nan
        
        # Calculate volatility
        daily_vol = returns.std()
        
        if pd.isna(daily_vol) or daily_vol <= 0:
            return np.nan
        
        if annualize:
            # Annualize using square root of trading days
            annual_vol = daily_vol * np.sqrt(252)
        else:
            annual_vol = daily_vol
        
        return float(annual_vol * 100.0)  # Convert to percentage
        
    except Exception as e:
        logger.debug(f"Error computing volatility: {e}")
        return np.nan

def compute_beta_alpha(
    asset_prices: pd.Series, 
    benchmark_prices: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE
) -> Tuple[float, float]:
    """
    Compute Beta and Alpha with enhanced error handling.
    
    Parameters
    ----------
    asset_prices : pd.Series
        Asset price series
    benchmark_prices : pd.Series
        Benchmark price series
    risk_free_rate : float, default RISK_FREE_RATE
        Risk-free rate for Alpha calculation
        
    Returns
    -------
    Tuple[float, float]
        Beta and Alpha values
    """
    try:
        if asset_prices.empty or benchmark_prices.empty:
            return np.nan, np.nan
        
        # Calculate returns
        asset_returns = asset_prices.pct_change().dropna()
        benchmark_returns = benchmark_prices.pct_change().dropna()
        
        # Remove infinite values
        asset_returns = asset_returns.replace([np.inf, -np.inf], np.nan).dropna()
        benchmark_returns = benchmark_returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Align the series
        aligned_data = pd.concat([asset_returns, benchmark_returns], axis=1, join='inner').dropna()
        
        if aligned_data.empty or len(aligned_data) < 10:  # Need sufficient data
            return np.nan, np.nan
        
        asset_ret = aligned_data.iloc[:, 0]
        bench_ret = aligned_data.iloc[:, 1]
        
        # Calculate Beta using covariance
        covariance = np.cov(asset_ret, bench_ret)[0, 1]
        benchmark_variance = np.var(bench_ret)
        
        if benchmark_variance == 0 or pd.isna(benchmark_variance):
            beta = np.nan
        else:
            beta = covariance / benchmark_variance
        
        # Calculate Alpha
        asset_mean_return = asset_ret.mean()
        benchmark_mean_return = bench_ret.mean()
        
        if pd.isna(asset_mean_return) or pd.isna(benchmark_mean_return) or pd.isna(beta):
            alpha = np.nan
        else:
            # Convert annual risk-free rate to daily
            daily_rf_rate = risk_free_rate / 252
            
            expected_return = daily_rf_rate + beta * (benchmark_mean_return - daily_rf_rate)
            alpha = asset_mean_return - expected_return
        
        # Validate results
        if not pd.isna(beta) and abs(beta) > 10:  # Unrealistic beta
            beta = np.nan
        if not pd.isna(alpha) and abs(alpha) > 1:  # Unrealistic daily alpha
            alpha = np.nan
        
        return float(beta) if not pd.isna(beta) else np.nan, float(alpha) if not pd.isna(alpha) else np.nan
        
    except Exception as e:
        logger.debug(f"Error computing Beta/Alpha: {e}")
        return np.nan, np.nan

def compute_enhanced_metrics(
    df: pd.DataFrame,
    prices: Dict[str, float],
    benchmark_data: Optional[pd.DataFrame] = None,
    period: str = "6mo"
) -> pd.DataFrame:
    """
    Compute comprehensive portfolio metrics with enhanced error handling.
    
    Parameters
    ----------
    df : pd.DataFrame
        Portfolio data
    prices : Dict[str, float]
        Current prices
    benchmark_data : pd.DataFrame, optional
        Benchmark price data
    period : str, default "6mo"
        Historical period for calculations
        
    Returns
    -------
    pd.DataFrame
        DataFrame with enhanced metrics
    """
    # Start with basic metrics
    result_df = compute_metrics(df, prices)
    
    if result_df.empty:
        return result_df
    
    # Initialize advanced metric columns
    advanced_cols = ['RSI', 'Volatility', 'Beta', 'Alpha', 'Sharpe']
    for col in advanced_cols:
        result_df[col] = np.nan
    
    # Get benchmark returns for Beta/Alpha calculations
    benchmark_returns = None
    if benchmark_data is not None and not benchmark_data.empty:
        primary_benchmark = benchmark_data.iloc[:, 0]
        if not primary_benchmark.empty:
            benchmark_returns = primary_benchmark
    
    # Calculate advanced metrics for each asset
    total_assets = len(result_df)
    logger.info(f"Computing advanced metrics for {total_assets} assets...")
    
    for idx, row in result_df.iterrows():
        ticker = str(row.get('Ticker', '')).upper().strip()
        if not ticker:
            continue
        
        try:
            # Fetch historical prices
            hist_prices = fetch_historical_series(ticker, period=period)
            
            if not hist_prices.empty and len(hist_prices) > 20:
                # RSI
                rsi = compute_rsi(hist_prices)
                if not pd.isna(rsi):
                    result_df.at[idx, 'RSI'] = rsi
                
                # Volatility
                volatility = compute_volatility(hist_prices)
                if not pd.isna(volatility):
                    result_df.at[idx, 'Volatility'] = volatility
                
                # Beta and Alpha
                if benchmark_returns is not None:
                    beta, alpha = compute_beta_alpha(hist_prices, benchmark_returns)
                    if not pd.isna(beta):
                        result_df.at[idx, 'Beta'] = beta
                    if not pd.isna(alpha):
                        result_df.at[idx, 'Alpha'] = alpha
                
                # Simple Sharpe ratio (using volatility and returns)
                if not pd.isna(volatility) and volatility > 0:
                    returns = hist_prices.pct_change().dropna()
                    if not returns.empty:
                        mean_return = returns.mean() * 252  # Annualized
                        excess_return = mean_return - RISK_FREE_RATE
                        sharpe = excess_return / (volatility / 100)
                        if not pd.isna(sharpe) and abs(sharpe) < 10:  # Reasonable range
                            result_df.at[idx, 'Sharpe'] = sharpe
                    
        except Exception as e:
            logger.debug(f"Error computing advanced metrics for {ticker}: {e}")
            continue
    
    # Add asset information from popular database
    popular_assets = get_popular_assets_flat()
    result_df['Asset Name'] = result_df['Ticker'].apply(
        lambda t: popular_assets.get(str(t).upper(), '')
    )
    
    logger.info(f"Enhanced metrics computed for {len(result_df)} assets")
    return result_df

# ============================================================================
# Fetch Benchmark Data (Enhanced)
# ============================================================================

def fetch_benchmark_data(
    period: str = "6mo", 
    interval: str = "1d", 
    tickers: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Fetch benchmark index data with enhanced error handling.
    
    Parameters
    ----------
    period : str, default "6mo"
        Historical period
    interval : str, default "1d"
        Data interval
    tickers : List[str], optional
        Benchmark tickers to fetch
        
    Returns
    -------
    pd.DataFrame
        Benchmark price data indexed by date
    """
    if not YF_AVAILABLE:
        return pd.DataFrame()
    
    if tickers is None:
        tickers = DEFAULT_BENCHMARKS
    
    cache_key = f"{','.join(tickers)}_{period}"
    
    # Check cache
    if cache_key in BENCHMARK_CACHE:
        return BENCHMARK_CACHE[cache_key]
    
    try:
        logger.debug(f"Fetching benchmark data: {tickers} ({period})")
        data = {}
        
        for ticker in tickers:
            try:
                series = fetch_historical_series(ticker, period=period, interval=interval)
                if not series.empty:
                    data[ticker] = series
                    logger.debug(f"✅ Benchmark {ticker}: {len(series)} points")
                else:
                    logger.debug(f"❌ Benchmark {ticker}: No data")
            except Exception as e:
                logger.debug(f"❌ Benchmark {ticker}: Error - {e}")
                continue
        
        if not data:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(data).sort_index()
            # Forward fill missing values
            df = df.ffill()
            # Drop rows with all NaN values
            df = df.dropna(how='all')
        
        # Cache the result
        BENCHMARK_CACHE[cache_key] = df
        logger.debug(f"Cached benchmark data: {df.shape}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching benchmark data: {e}")
        empty_df = pd.DataFrame()
        BENCHMARK_CACHE[cache_key] = empty_df
        return empty_df

# ============================================================================
# Portfolio-Level Risk Measures (Enhanced)
# ============================================================================

def calculate_portfolio_sharpe(
    metrics_df: pd.DataFrame,
    period: str = "6mo",
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    """
    Calculate portfolio Sharpe ratio with enhanced error handling.
    
    Parameters
    ----------
    metrics_df : pd.DataFrame
        Portfolio metrics with weights
    period : str, default "6mo"
        Historical period
    risk_free_rate : float, default RISK_FREE_RATE
        Annual risk-free rate
        
    Returns
    -------
    float
        Annualized Sharpe ratio
    """
    try:
        if metrics_df.empty or 'Weight %' not in metrics_df.columns:
            return np.nan
        
        # Get valid assets with weights
        valid_assets = metrics_df.dropna(subset=['Weight %', 'Ticker'])
        if valid_assets.empty:
            return np.nan
        
        weights = valid_assets['Weight %'] / 100.0
        tickers = valid_assets['Ticker'].str.upper().tolist()
        
        # Fetch historical data for all assets
        price_data = {}
        for ticker in tickers:
            try:
                prices = fetch_historical_series(ticker, period=period)
                if not prices.empty and len(prices) > 20:
                    price_data[ticker] = prices
            except Exception:
                continue
        
        if not price_data or len(price_data) < 2:
            return np.nan
        
        # Create aligned price DataFrame
        price_df = pd.DataFrame(price_data).dropna()
        if price_df.empty or len(price_df) < 10:
            return np.nan
        
        # Calculate returns
        returns_df = price_df.pct_change().dropna()
        
        # Remove infinite values
        returns_df = returns_df.replace([np.inf, -np.inf], np.nan).dropna()
        
        if returns_df.empty:
            return np.nan
        
        # Align weights with available data
        available_tickers = returns_df.columns.tolist()
        weight_mask = valid_assets['Ticker'].isin(available_tickers)
        aligned_weights = weights[weight_mask]
        
        if aligned_weights.sum() == 0:
            return np.nan
            
        aligned_weights = aligned_weights / aligned_weights.sum()  # Renormalize
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df[available_tickers] * aligned_weights.values).sum(axis=1)
        
        # Calculate Sharpe ratio
        daily_rf_rate = risk_free_rate / 252
        excess_returns = portfolio_returns - daily_rf_rate
        
        if excess_returns.std() == 0 or pd.isna(excess_returns.std()):
            return np.nan
        
        sharpe_daily = excess_returns.mean() / excess_returns.std()
        sharpe_annual = sharpe_daily * np.sqrt(252)
        
        # Validate result
        if pd.isna(sharpe_annual) or abs(sharpe_annual) > 10:
            return np.nan
        
        return float(sharpe_annual)
        
    except Exception as e:
        logger.error(f"Error calculating portfolio Sharpe ratio: {e}")
        return np.nan

def calculate_value_at_risk(
    metrics_df: pd.DataFrame,
    confidence: float = 0.95,
    period: str = "6mo"
) -> float:
    """
    Calculate portfolio Value at Risk (VaR) with enhanced error handling.
    
    Parameters
    ----------
    metrics_df : pd.DataFrame
        Portfolio metrics with weights and values
    confidence : float, default 0.95
        Confidence level
    period : str, default "6mo"
        Historical period
        
    Returns
    -------
    float
        VaR in dollar terms
    """
    try:
        required_cols = ['Weight %', 'Ticker', 'Total Value']
        if metrics_df.empty or not all(col in metrics_df.columns for col in required_cols):
            return np.nan
        
        # Get valid assets
        valid_assets = metrics_df.dropna(subset=required_cols)
        if valid_assets.empty:
            return np.nan
        
        weights = valid_assets['Weight %'] / 100.0
        tickers = valid_assets['Ticker'].str.upper().tolist()
        total_portfolio_value = valid_assets['Total Value'].sum()
        
        if total_portfolio_value <= 0:
            return np.nan
        
        # Fetch historical data
        price_data = {}
        for ticker in tickers:
            try:
                prices = fetch_historical_series(ticker, period=period)
                if not prices.empty and len(prices) > 20:
                    price_data[ticker] = prices
            except Exception:
                continue
        
        if not price_data or len(price_data) < 2:
            return np.nan
        
        # Create aligned returns
        price_df = pd.DataFrame(price_data).dropna()
        returns_df = price_df.pct_change().dropna()
        
        # Remove infinite values
        returns_df = returns_df.replace([np.inf, -np.inf], np.nan).dropna()
        
        if returns_df.empty or len(returns_df) < 10:
            return np.nan
        
        # Align weights
        available_tickers = returns_df.columns.tolist()
        weight_mask = valid_assets['Ticker'].isin(available_tickers)
        aligned_weights = weights[weight_mask]
        
        if aligned_weights.sum() == 0:
            return np.nan
            
        aligned_weights = aligned_weights / aligned_weights.sum()
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df[available_tickers] * aligned_weights.values).sum(axis=1)
        
        # Calculate VaR
        var_percentile = (1 - confidence) * 100
        var_return = np.percentile(portfolio_returns, var_percentile)
        var_dollar = abs(var_return * total_portfolio_value)
        
        # Validate result
        if pd.isna(var_dollar) or var_dollar < 0:
            return np.nan
        
        return float(var_dollar)
        
    except Exception as e:
        logger.error(f"Error calculating VaR: {e}")
        return np.nan

# ============================================================================
# Enhanced Recommendations
# ============================================================================

def generate_portfolio_recommendations(metrics_df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generate comprehensive portfolio recommendations with enhanced analysis.
    
    Parameters
    ----------
    metrics_df : pd.DataFrame
        Portfolio with enhanced metrics
        
    Returns
    -------
    List[Dict[str, str]]
        List of recommendation objects
    """
    recommendations = []
    
    if metrics_df is None or metrics_df.empty:
        return recommendations
    
    try:
        # 1. Diversification Analysis
        if 'Asset Type' in metrics_df.columns and 'Weight %' in metrics_df.columns:
            allocation = metrics_df.groupby('Asset Type')['Weight %'].sum()
            
            if not allocation.empty:
                max_allocation = allocation.max()
                dominant_type = allocation.idxmax()
                
                if max_allocation > 70:
                    recommendations.append({
                        "type": "warning",
                        "title": "High Concentration Risk",
                        "description": f"Your portfolio is heavily concentrated in {dominant_type} ({max_allocation:.1f}%). Consider diversifying into other asset classes to reduce risk."
                    })
                elif max_allocation > 50:
                    recommendations.append({
                        "type": "info",
                        "title": "Monitor Concentration",
                        "description": f"Significant exposure to {dominant_type} ({max_allocation:.1f}%). Monitor this allocation and consider rebalancing if it grows further."
                    })
        
        # 2. Performance Analysis
        if 'P/L %' in metrics_df.columns:
            # Large losses
            large_losses = metrics_df[metrics_df['P/L %'] < -20]
            if not large_losses.empty:
                worst_performers = large_losses.nsmallest(3, 'P/L %')['Ticker'].tolist()
                recommendations.append({
                    "type": "warning",
                    "title": "Significant Losses",
                    "description": f"These positions have losses >20%: {', '.join(worst_performers)}. Review your investment thesis and consider stop-loss strategies."
                })
            
            # Exceptional gains (potential profit-taking)
            large_gains = metrics_df[metrics_df['P/L %'] > 100]
            if not large_gains.empty:
                best_performers = large_gains.nlargest(3, 'P/L %')['Ticker'].tolist()
                recommendations.append({
                    "type": "success",
                    "title": "Exceptional Performers",
                    "description": f"These positions have gains >100%: {', '.join(best_performers)}. Consider taking partial profits to lock in gains."
                })
        
        # 3. Volatility Analysis
        if 'Volatility' in metrics_df.columns:
            high_vol_assets = metrics_df[metrics_df['Volatility'] > 40]
            if not high_vol_assets.empty:
                vol_tickers = high_vol_assets.nlargest(5, 'Volatility')['Ticker'].tolist()
                avg_vol = high_vol_assets['Volatility'].mean()
                recommendations.append({
                    "type": "warning",
                    "title": "High Volatility Alert",
                    "description": f"High volatility assets (avg {avg_vol:.1f}%): {', '.join(vol_tickers)}. Consider position sizing and risk management."
                })
        
        # 4. RSI-based Technical Analysis
        if 'RSI' in metrics_df.columns:
            oversold = metrics_df[metrics_df['RSI'] < 30]
            overbought = metrics_df[metrics_df['RSI'] > 70]
            
            if not oversold.empty:
                oversold_tickers = oversold.nsmallest(3, 'RSI')['Ticker'].tolist()
                recommendations.append({
                    "type": "info",
                    "title": "Potentially Oversold Assets",
                    "description": f"RSI < 30: {', '.join(oversold_tickers)}. Research for potential buying opportunities, but confirm with other indicators."
                })
            
            if not overbought.empty:
                overbought_tickers = overbought.nlargest(3, 'RSI')['Ticker'].tolist()
                recommendations.append({
                    "type": "info",
                    "title": "Potentially Overbought Assets", 
                    "description": f"RSI > 70: {', '.join(overbought_tickers)}. Monitor for potential corrections or consider profit-taking."
                })
        
        # 5. Beta Analysis (Market Risk)
        if 'Beta' in metrics_df.columns:
            high_beta = metrics_df[metrics_df['Beta'] > 1.5]
            low_beta = metrics_df[metrics_df['Beta'] < 0.5]
            
            if not high_beta.empty:
                high_beta_count = len(high_beta)
                high_beta_weight = high_beta['Weight %'].sum() if 'Weight %' in high_beta.columns else 0
                recommendations.append({
                    "type": "info",
                    "title": "High Beta Exposure",
                    "description": f"{high_beta_count} high-beta assets (>1.5) representing {high_beta_weight:.1f}% of portfolio. These amplify market movements."
                })
            
            if not low_beta.empty and len(metrics_df) > 5:
                low_beta_tickers = low_beta['Ticker'].tolist()[:3]
                recommendations.append({
                    "type": "success",
                    "title": "Defensive Positions",
                    "description": f"Low-beta assets provide stability: {', '.join(low_beta_tickers)}. Good for portfolio balance during market volatility."
                })
        
        # 6. Sharpe Ratio Analysis
        if 'Sharpe' in metrics_df.columns:
            good_sharpe = metrics_df[metrics_df['Sharpe'] > 1.0]
            poor_sharpe = metrics_df[metrics_df['Sharpe'] < 0]
            
            if not good_sharpe.empty:
                best_sharpe = good_sharpe.nlargest(3, 'Sharpe')['Ticker'].tolist()
                recommendations.append({
                    "type": "success",
                    "title": "Strong Risk-Adjusted Returns",
                    "description": f"Excellent Sharpe ratios (>1.0): {', '.join(best_sharpe)}. These assets provide good returns per unit of risk."
                })
            
            if not poor_sharpe.empty:
                worst_sharpe = poor_sharpe.nsmallest(3, 'Sharpe')['Ticker'].tolist()
                recommendations.append({
                    "type": "warning",
                    "title": "Poor Risk-Adjusted Returns",
                    "description": f"Negative Sharpe ratios: {', '.join(worst_sharpe)}. Consider whether these positions justify their risk."
                })
        
        # 7. Portfolio Size Analysis
        portfolio_size = len(metrics_df)
        if portfolio_size < 5:
            recommendations.append({
                "type": "info",
                "title": "Small Portfolio",
                "description": f"Only {portfolio_size} assets. Consider adding more positions for better diversification across sectors and asset classes."
            })
        elif portfolio_size > 50:
            recommendations.append({
                "type": "info",
                "title": "Large Portfolio",
                "description": f"{portfolio_size} assets may be difficult to monitor. Consider consolidating into ETFs or focusing on your highest-conviction positions."
            })
        
        # 8. Position Sizing Analysis
        if 'Weight %' in metrics_df.columns:
            large_positions = metrics_df[metrics_df['Weight %'] > 10]
            if not large_positions.empty:
                large_pos_tickers = large_positions['Ticker'].tolist()
                recommendations.append({
                    "type": "warning",
                    "title": "Large Position Sizes",
                    "description": f"Positions >10% of portfolio: {', '.join(large_pos_tickers)}. Large positions increase concentration risk."
                })
        
        # 9. Missing Data Warning
        missing_prices = metrics_df[metrics_df['Current Price'].isna()]
        if not missing_prices.empty:
            missing_tickers = missing_prices['Ticker'].tolist()[:5]
            recommendations.append({
                "type": "warning",
                "title": "Missing Price Data",
                "description": f"No current prices for: {', '.join(missing_tickers)}. Verify ticker symbols or check if assets are delisted."
            })
        
        # 10. Overall Portfolio Health
        if not recommendations or all(r.get("type") in ["success", "info"] for r in recommendations):
            total_value = metrics_df['Total Value'].sum() if 'Total Value' in metrics_df.columns else 0
            recommendations.append({
                "type": "success",
                "title": "Portfolio Health Check",
                "description": f"Portfolio appears well-balanced with {len(metrics_df)} assets valued at ${total_value:,.0f}. Continue regular monitoring and rebalancing."
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return [{
            "type": "info",
            "title": "Analysis Unavailable",
            "description": "Unable to generate recommendations. Please refresh your data and try again."
        }]

# ============================================================================
# Asset Search and Suggestion Functions
# ============================================================================

def suggest_rebalancing(metrics_df: pd.DataFrame) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Suggest portfolio rebalancing based on modern portfolio theory principles.
    
    Parameters
    ----------
    metrics_df : pd.DataFrame
        Portfolio data with Asset Type and Weight %
        
    Returns
    -------
    Optional[Dict[str, pd.DataFrame]]
        Current and suggested allocations
    """
    if metrics_df is None or metrics_df.empty:
        return None
    
    required_cols = ['Asset Type', 'Weight %']
    if not all(col in metrics_df.columns for col in required_cols):
        return None
    
    try:
        # Current allocation
        current = metrics_df.groupby('Asset Type')['Weight %'].sum().reset_index()
        current.columns = ['asset_type', 'weight']
        current = current.sort_values('weight', ascending=False)
        
        # Enhanced target weights based on asset types
        asset_types = current['asset_type'].tolist()
        target_weights = {}
        
        # Base allocations for common asset types
        base_allocations = {
            'stock': 40.0, 'stocks': 40.0, 'equity': 40.0,
            'etf': 25.0, 'etfs': 25.0,
            'bond': 20.0, 'bonds': 20.0, 'fixed income': 20.0,
            'crypto': 5.0, 'cryptocurrency': 5.0, 'bitcoin': 5.0,
            'reit': 5.0, 'real estate': 5.0,
            'commodity': 3.0, 'commodities': 3.0,
            'cash': 2.0, 'money market': 2.0
        }
        
        for asset_type in asset_types:
            asset_lower = asset_type.lower()
            # Find matching base allocation
            allocated = False
            for key, value in base_allocations.items():
                if key in asset_lower:
                    target_weights[asset_type] = value
                    allocated = True
                    break
            
            if not allocated:
                # Default allocation for unknown types
                target_weights[asset_type] = 10.0
        
        # Normalize target weights to 100%
        total_target = sum(target_weights.values())
        if total_target > 0:
            for asset_type in target_weights:
                target_weights[asset_type] = (target_weights[asset_type] / total_target) * 100.0
        
        # Create suggested DataFrame
        suggested = pd.DataFrame({
            'asset_type': list(target_weights.keys()),
            'weight': list(target_weights.values())
        })
        suggested = suggested.sort_values('weight', ascending=False)
        
        return {
            'current': current,
            'suggested': suggested
        }
        
    except Exception as e:
        logger.error(f"Error suggesting rebalancing: {e}")
        return None

# ============================================================================
# Utility Functions
# ============================================================================

def check_password_strength(password: str) -> str:
    """
    Assess password strength using multiple criteria.
    
    Parameters
    ----------
    password : str
        Password to evaluate
        
    Returns
    -------
    str
        Strength level: 'Weak', 'Medium', or 'Strong'
    """
    if not password:
        return "Weak"
    
    score = 0
    
    # Length checks
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety checks
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(not c.isalnum() for c in password):
        score += 1
    
    # Pattern checks
    if not any(password[i:i+3] == password[i] * 3 for i in range(len(password)-2)):
        score += 1  # No repeated characters
    
    # Determine strength
    if score <= 3:
        return "Weak"
    elif score <= 6:
        return "Medium"
    else:
        return "Strong"

def clear_all_caches():
    """Clear all cached data."""
    global PRICE_CACHE, CACHE_TIMESTAMPS, HIST_PRICES_CACHE, BENCHMARK_CACHE
    
    PRICE_CACHE.clear()
    CACHE_TIMESTAMPS.clear()
    HIST_PRICES_CACHE.clear()
    BENCHMARK_CACHE.clear()
    
    logger.info("All caches cleared")

def log_portfolio_stats(df: pd.DataFrame, action: str = "processed"):
    """Log portfolio statistics for debugging."""
    if df is None or df.empty:
        logger.info(f"Portfolio {action}: empty")
        return
    
    try:
        stats = {
            "assets": len(df),
            "asset_types": df['Asset Type'].nunique() if 'Asset Type' in df.columns else 0,
            "total_value": df['Total Value'].sum() if 'Total Value' in df.columns else 0,
            "valid_prices": sum(1 for x in df.get('Current Price', []) if not pd.isna(x))
        }
        logger.info(f"Portfolio {action}: {stats}")
        
    except Exception as e:
        logger.error(f"Error logging portfolio stats: {e}")

def get_market_status() -> Dict[str, Union[str, bool]]:
    """
    Get current market status information.
    
    Returns
    -------
    Dict[str, Union[str, bool]]
        Market status information
    """
    try:
        from datetime import datetime
        import pytz
        
        # US market timezone
        us_tz = pytz.timezone('US/Eastern')
        now_us = datetime.now(us_tz)
        
        # Market hours (9:30 AM - 4:00 PM ET)
        market_open = now_us.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_us.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Check if it's a weekday
        is_weekday = now_us.weekday() < 5
        
        # Market is open if it's a weekday and within trading hours
        is_market_open = is_weekday and market_open <= now_us <= market_close
        
        return {
            "is_open": is_market_open,
            "local_time": now_us.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "next_open": "Next weekday 9:30 AM ET" if not is_weekday else "Today 9:30 AM ET" if now_us < market_open else "Tomorrow 9:30 AM ET",
            "status": "Open" if is_market_open else "Closed"
        }
        
    except Exception as e:
        logger.debug(f"Error getting market status: {e}")
        return {
            "is_open": False,
            "local_time": "Unknown",
            "next_open": "Unknown",
            "status": "Unknown"
        }

# ============================================================================
# Backward Compatibility Functions
# ============================================================================

# For backward compatibility with existing code
def validate_tickers(tickers: Iterable[str]) -> Dict[str, bool]:
    """
    Simple ticker validation for backward compatibility.
    
    Parameters
    ----------
    tickers : Iterable[str]
        Ticker symbols to validate
        
    Returns
    -------
    Dict[str, bool]
        Simple mapping of ticker to validity
    """
    enhanced_results = validate_tickers_enhanced(tickers)
    return {ticker: result.get("valid", False) for ticker, result in enhanced_results.items()}

def asset_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize portfolio by asset type.
    
    Parameters
    ----------
    df : pd.DataFrame
        Portfolio data with Asset Type and Total Value columns
        
    Returns
    -------
    pd.DataFrame
        Summary by asset type
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    required_cols = ['Asset Type', 'Total Value']
    if not all(col in df.columns for col in required_cols):
        return pd.DataFrame()
    
    try:
        summary = df.groupby('Asset Type').agg({
            'Total Value': 'sum',
            'Ticker': 'count'
        }).reset_index()
        summary.columns = ['Asset Type', 'Total Value', 'Count']
        summary = summary.sort_values('Total Value', ascending=False)
        
        # Add percentage
        total_portfolio_value = summary['Total Value'].sum()
        if total_portfolio_value > 0:
            summary['Weight %'] = summary['Total Value'] / total_portfolio_value * 100
        else:
            summary['Weight %'] = 0
        
        return summary
        
    except Exception as e:
        logger.error(f"Error creating asset breakdown: {e}")
        return pd.DataFrame()

def top_and_worst_assets(df: pd.DataFrame, n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify top and worst performing assets.
    
    Parameters
    ----------
    df : pd.DataFrame
        Portfolio data with P/L % column
    n : int, default 5
        Number of assets to return
        
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Top performers and worst performers
    """
    if df is None or df.empty or 'P/L %' not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        # Filter out NaN values
        valid_df = df.dropna(subset=['P/L %'])
        
        if valid_df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        sorted_df = valid_df.sort_values('P/L %', ascending=False)
        
        top_n = sorted_df.head(n)[['Ticker', 'P/L %', 'P/L', 'Total Value']]
        worst_n = sorted_df.tail(n)[['Ticker', 'P/L %', 'P/L', 'Total Value']].iloc[::-1]
        
        return top_n, worst_n
        
    except Exception as e:
        logger.error(f"Error identifying top/worst assets: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ============================================================================
# Module Initialization
# ============================================================================

def initialize_module():
    """Initialize the portfolio utils module with enhanced setup."""
    try:
        _ensure_portfolio_dir()
        
        # Test yfinance connection
        if YF_AVAILABLE:
            try:
                # Quick test with a popular stock
                test_prices = fetch_current_prices_robust(["AAPL"])
                if not pd.isna(test_prices.get("AAPL", np.nan)):
                    logger.info("✅ yfinance connection test successful")
                else:
                    logger.warning("⚠️ yfinance test returned no data - API may be limited")
            except Exception as e:
                logger.warning(f"⚠️ yfinance test failed: {e}")
        
        logger.info(f"📊 Portfolio utils initialized - yfinance: {'✅ available' if YF_AVAILABLE else '❌ unavailable'}")
        logger.info(f"📈 Popular assets database loaded: {len(get_popular_assets_flat())} assets")
        
    except Exception as e:
        logger.error(f"❌ Error initializing portfolio utils: {e}")
        raise

# Initialize on import
initialize_module()
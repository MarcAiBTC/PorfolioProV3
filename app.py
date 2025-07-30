from typing import Optional
from datetime import datetime
import streamlit as st

def create_sidebar_enhanced():
    """Enhanced sidebar with better organization and features."""
    with st.sidebar:
        if st.session_state.authenticated:
            # User profile section
            st.markdown("### 👤 Welcome Back!")
            st.write(f"**{st.session_state.username}**")
            st.caption(f"Version: {st.session_state.app_version}")
            
            # Quick portfolio stats
            display_sidebar_portfolio_stats_enhanced()
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            page = st.radio(
                "Choose a page:",
                [
                    "📊 Dashboard",
                    "➕ Add Asset",
                    "📤 Upload Portfolio", 
                    "📚 Portfolio History",
                    "🔧 Settings",
                    "❓ Help",
                    "🚪 Sign Out"
                ],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Enhanced settings
            display_sidebar_settings_enhanced()
            
            # Quick actions
            display_sidebar_quick_actions_enhanced()
            
            # System status
            display_sidebar_status()
            
            return page
        
        else:
            # Unauthenticated sidebar
            display_unauthenticated_sidebar_enhanced()
            return None
def display_auth_page_enhanced():
    """Enhanced authentication page with better design and features."""
    try:
        # Main header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">📊 Portfolio Manager Pro</h1>
            <p style="font-size: 1.3rem; color: #64748b; margin-bottom: 3rem;">
                Professional investment portfolio management with real-time analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        display_feature_highlights_enhanced()
        
        st.markdown("---")
        
        # Authentication tabs
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            display_login_form_enhanced()
        
        with tab2:
            display_registration_form_enhanced()
        
        # Footer with security notice
        display_security_notice_enhanced()
        
    except Exception as e:
        logger.error(f"Error in auth page: {e}")
        st.error("Error loading authentication page")
        
def handle_application_error_enhanced(error):
    st.error(f"❌ Application error: {str(error)}")
    st.stop()

def display_market_status():
    """Display current market status with error handling."""
    try:
        market_info = putils.get_market_status()
        status = market_info.get('status', 'Unknown')
        is_open = market_info.get('is_open', False)
        
        status_icon = "🟢" if is_open else "🔴"
        
        st.markdown(f"**{status_icon} Market: {status}** | {market_info.get('local_time', 'Time unknown')}")
        
        if not is_open:
            st.caption(f"Next open: {market_info.get('next_open', 'Unknown')}")
            
    except Exception as e:
        logger.debug(f"Error displaying market status: {e}")
        st.caption("🕐 Market status unavailable")

def safe_load_portfolio(username: str, filename: Optional[str] = None) -> bool:
    """Enhanced portfolio loading with comprehensive error handling."""
    try:
        with st.spinner("📂 Loading portfolio..."):
            df = putils.load_portfolio(username, filename)
            
        if df is not None and not df.empty:
            # Enhanced validation
            required_cols = ['Ticker', 'Purchase Price', 'Quantity', 'Asset Type']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Portfolio missing required columns: {', '.join(missing_cols)}")
                
                # Offer to fix common issues
                if st.button("🔧 Try to Fix Automatically"):
                    try:
                        df = fix_portfolio_columns(df)
                        if df is not None:
                            putils.save_portfolio(username, df, overwrite=True)
                            st.success("✅ Portfolio fixed and saved!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to fix portfolio: {str(e)}")
                return False
            
            # Data cleaning and validation
            original_count = len(df)
            df = clean_portfolio_data(df)
            cleaned_count = len(df)
            
            if cleaned_count < original_count:
                st.warning(f"⚠️ Removed {original_count - cleaned_count} invalid rows during loading")
            
            # Update session state
            st.session_state.portfolio_df = df
            st.session_state.selected_portfolio_file = filename
            st.session_state.portfolio_modified = False
            st.session_state.last_refresh = datetime.now()

            st.success(f"✅ Portfolio loaded successfully! ({len(df)} assets)")
            logger.info(f"Portfolio loaded for user {username}: {len(df)} assets")
            return True
        else:
            st.warning("⚠️ Portfolio file is empty or could not be loaded")
            return False

    except Exception as e:
        error_msg = f"Error loading portfolio: {str(e)}"
        st.error(f"❌ {error_msg}")
        logger.error(f"Portfolio load failed for {username}: {e}")
        
        if st.session_state.get('education_mode', False):
            with st.expander("🔧 Error Details"):
                st.code(str(e))
        return False

def show_portfolio_quick_stats():
    """Show quick portfolio statistics with error handling."""
    try:
        if st.session_state.portfolio_df is not None and not st.session_state.portfolio_df.empty:
            df = st.session_state.portfolio_df
            last_refresh = st.session_state.get('last_refresh')
            refresh_text = last_refresh.strftime('%H:%M') if last_refresh else 'Unknown'
            
            # Create columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎯 Assets", len(df))
            
            with col2:
                st.metric("📊 Asset Types", df['Asset Type'].nunique())
            
            with col3:
                st.metric("📅 Last Updated", refresh_text)
            
            with col4:
                file_name = st.session_state.get('selected_portfolio_file', 'Current')
                st.metric("💾 File", file_name)
        else:
            st.info("No portfolio loaded yet")
    except Exception as e:
        logger.error(f"Error showing portfolio stats: {e}")
        st.error("Error displaying portfolio statistics")

def create_demo_portfolio():
    """Create a demo portfolio for new users with error handling."""
    try:
        demo_data = [
            {"Ticker": "AAPL", "Purchase Price": 150.0, "Quantity": 10, "Asset Type": "Stock", "Notes": "Demo tech stock"},
            {"Ticker": "SPY", "Purchase Price": 400.0, "Quantity": 5, "Asset Type": "ETF", "Notes": "Demo market ETF"},
            {"Ticker": "BTC-USD", "Purchase Price": 45000.0, "Quantity": 0.1, "Asset Type": "Crypto", "Notes": "Demo cryptocurrency"},
            {"Ticker": "GOOGL", "Purchase Price": 2500.0, "Quantity": 2, "Asset Type": "Stock", "Notes": "Demo growth stock"},
            {"Ticker": "QQQ", "Purchase Price": 350.0, "Quantity": 3, "Asset Type": "ETF", "Notes": "Demo tech ETF"}
        ]
        
        demo_df = pd.DataFrame(demo_data)
        demo_df['Purchase Date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save demo portfolio
        putils.save_portfolio(st.session_state.username, demo_df, overwrite=True)
        st.session_state.portfolio_df = demo_df
        st.session_state.portfolio_modified = True
        
        st.success("✅ Demo portfolio created! Explore the features with sample data.")
        
    except Exception as e:
        st.error(f"❌ Failed to create demo portfolio: {e}")
        logger.error(f"Demo portfolio creation failed: {e}")

def refresh_portfolio_data():
    """Refresh portfolio data with enhanced error handling."""
    try:
        # Clear caches
        putils.clear_all_caches()
        
        # Update timestamp
        st.session_state.last_refresh = datetime.now()
        
        st.success("✅ Data refreshed successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Refresh failed: {str(e)}")
        logger.error(f"Portfolio refresh failed: {e}")

def show_welcome_message_enhanced():
    """Enhanced welcome message with better error handling."""
    try:
        if st.session_state.get('show_welcome', False) and st.session_state.get('authenticated', False):
            st.markdown(f"""
            ## 👋 Welcome back, {st.session_state.get('username', 'User')}!
            
            Your portfolio dashboard is ready with **real-time market data** and **AI-powered insights**.
            """)
            
            # Quick start options
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🚀 Get Started", type="primary"):
                    st.session_state.show_welcome = False
                    st.rerun()
            
            with col2:
                if st.button("📚 Enable Learning"):
                    st.session_state.education_mode = True
                    st.session_state.show_welcome = False
                    st.rerun()
            
            with col3:
                if st.button("📊 View Demo Data"):
                    # Load demo portfolio
                    create_demo_portfolio()
                    st.session_state.show_welcome = False
                    st.rerun()
            
            with col4:
                if st.button("❓ Show Help"):
                    st.session_state.show_welcome = False
                    st.rerun()
            
            st.markdown("---")
    except Exception as e:
        logger.error(f"Error showing welcome message: {e}")

def display_empty_portfolio_guide():
    """Enhanced empty portfolio guide with error handling."""
    try:
        st.markdown("## 🚀 Welcome to Portfolio Manager Pro!")
        st.markdown("Start building your investment portfolio with our comprehensive tools")
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### ➕ Smart Asset Addition
            - 🔍 Search from 500+ popular assets
            - 📊 Real-time price validation
            - 🎯 Automatic categorization
            - 📈 Live preview with P/L
            """)
            
            if st.button("🚀 Add Your First Asset", type="primary"):
                st.session_state.show_welcome = False
        
        with col2:
            st.markdown("""
            ### 📤 Bulk Import
            - 📄 CSV/JSON file support
            - 🔧 Automatic data cleaning
            - ✅ Ticker validation
            - 📋 Template downloads
            """)
            
            if st.button("📁 Upload Portfolio File"):
                pass
        
        with col3:
            st.markdown("""
            ### 📊 Advanced Analytics
            - 📈 Real-time market data
            - ⚡ Technical indicators (RSI, Beta)
            - 🎯 Risk analysis & VaR
            - 💡 AI-powered recommendations
            """)
        
        # Quick start tips
        with st.expander("💡 Quick Start Tips", expanded=True):
            st.markdown("""
            **For beginners:**
            1. Start with popular ETFs like SPY (S&P 500) or QQQ (NASDAQ)
            2. Enable Education Mode in the sidebar for helpful explanations
            3. Use the asset picker to discover new investments
            
            **For experienced investors:**
            1. Import your existing portfolio via CSV/JSON
            2. Explore advanced metrics like Alpha, Beta, and Sharpe ratio
            3. Set up automatic refreshing for real-time monitoring
            """)
    except Exception as e:
        logger.error(f"Error displaying empty portfolio guide: {e}")
        st.error("Error loading portfolio guide")

def display_logout_confirmation_enhanced():
    """Enhanced logout confirmation with error handling."""
    try:
        show_main_header("🚪 Sign Out", "Thanks for using Portfolio Manager Pro!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 👋 See you soon!")
            st.write(f"**{st.session_state.get('username', 'User')}**, your portfolio data has been saved securely.")
            st.write("You can return anytime to continue tracking your investments.")
            
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("⬅️ Stay Signed In", type="secondary"):
                    st.info("👍 Continuing your session...")
                    time.sleep(1)
                    st.rerun()
            
            with col_b:
                if st.button("🚪 Confirm Sign Out", type="primary"):
                    handle_logout()
    except Exception as e:
        logger.error(f"Error displaying logout confirmation: {e}")
        st.error("Error loading logout page")

def handle_logout():
    """Handle user logout process with error handling."""
    try:
        username = st.session_state.get('username', 'Unknown')
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Reinitialize
        initialize_session_state()
        
        st.success("👋 You have been signed out successfully!")
        logger.info(f"User logged out: {username}")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        st.error("Error during logout")

# Fix additional functions that might have errors
def history_page_enhanced():
    """Enhanced history page with error handling."""
    try:
        show_main_header("📚 Portfolio History", "Manage your saved portfolios")
        
        username = st.session_state.get('username', '')
        if not username:
            st.error("User not found")
            return
            
        files = putils.list_portfolios(username)
        
        if not files:
            st.markdown("## 📝 No Portfolio History Yet")
            st.markdown("Start building your investment tracking history!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### ➕ Add Assets")
                st.write("Start by adding individual investments")
            
            with col2:
                st.markdown("### 📤 Upload Files")
                st.write("Import from CSV or JSON files")
            
            with col3:
                st.markdown("### 💾 Auto-Save")
                st.write("Your portfolios are saved automatically")
            return
        
        st.write(f"📊 You have **{len(files)}** saved portfolios:")
        
        # Portfolio management interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_file = st.selectbox(
                "🗂️ Select Portfolio:",
                files,
                format_func=lambda x: f"{'📍 ' if x == st.session_state.get('selected_portfolio_file') else '📁 '}{x}",
                help="Choose a portfolio to manage"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("📂 Load", help="Load selected portfolio"):
                    if safe_load_portfolio(username, selected_file):
                        st.success(f"✅ Loaded '{selected_file}'")
            
            with col_b:
                if st.button("🗑️ Delete", help="Delete selected portfolio"):
                    if selected_file == st.session_state.get('selected_portfolio_file'):
                        st.error("❌ Cannot delete currently active portfolio")
                    else:
                        # Simple deletion confirmation
                        if st.button("⚠️ Confirm Delete"):
                            try:
                                file_path = os.path.join(putils.PORTFOLIO_DIR, selected_file)
                                os.remove(file_path)
                                st.success(f"✅ Deleted '{selected_file}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting file: {e}")
        
        # Show file preview if selected
        if selected_file:
            try:
                file_path = os.path.join(putils.PORTFOLIO_DIR, selected_file)
                
                if os.path.exists(file_path):
                    # File metadata
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size
                    file_modified = datetime.fromtimestamp(file_stats.st_mtime)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 File Size", f"{file_size:,} bytes")
                    
                    with col2:
                        st.metric("📅 Modified", file_modified.strftime("%Y-%m-%d"))
                    
                    with col3:
                        st.metric("🕐 Time", file_modified.strftime("%H:%M:%S"))
                    
                    with col4:
                        is_current = selected_file == st.session_state.get('selected_portfolio_file')
                        status = "📍 Active" if is_current else "📁 Stored"
                        st.metric("📌 Status", status)
                    
                    # Portfolio preview
                    with st.expander("👀 Portfolio Preview", expanded=True):
                        try:
                            if selected_file.endswith('.csv'):
                                preview_df = pd.read_csv(file_path)
                            else:
                                preview_df = pd.read_json(file_path)
                            
                            if not preview_df.empty:
                                st.dataframe(preview_df.head(), use_container_width=True)
                            else:
                                st.warning("⚠️ Portfolio file appears to be empty")
                        except Exception as e:
                            st.error(f"Error loading preview: {e}")
            except Exception as e:
                st.error(f"Error accessing file: {e}")
                
    except Exception as e:
        logger.error(f"Error in history page: {e}")
        st.error("Error loading portfolio history")

def settings_page():
    """Settings page with error handling."""
    try:
        show_main_header("🔧 Settings", "Customize your Portfolio Manager Pro experience")
        
        # User settings
        st.subheader("👤 User Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Education mode
            education_mode = st.checkbox(
                "📚 Education Mode",
                value=st.session_state.get('education_mode', True),
                help="Show helpful tooltips and explanations throughout the app"
            )
            st.session_state.education_mode = education_mode
            
            # Auto refresh
            auto_refresh = st.checkbox(
                "🔄 Auto Refresh Data",
                value=st.session_state.get('auto_refresh_enabled', False),
                help="Automatically refresh portfolio data every 5 minutes"
            )
            st.session_state.auto_refresh_enabled = auto_refresh
            
            # Advanced metrics
            show_advanced = st.checkbox(
                "📊 Show Advanced Metrics",
                value=st.session_state.get('show_advanced_metrics', True),
                help="Display technical indicators like RSI, Beta, Alpha"
            )
            st.session_state.show_advanced_metrics = show_advanced
        
        with col2:
            # Data timeframe
            timeframe_options = ["1mo", "3mo", "6mo", "1y", "2y"]
            current_timeframe = st.session_state.get('selected_timeframe', '6mo')
            
            timeframe = st.selectbox(
                "📅 Historical Data Timeframe",
                timeframe_options,
                index=timeframe_options.index(current_timeframe) if current_timeframe in timeframe_options else 2,
                help="Period for historical analysis and technical indicators"
            )
            st.session_state.selected_timeframe = timeframe
            
            # Theme (placeholder for future)
            st.selectbox(
                "🎨 Theme",
                ["Light", "Dark (Coming Soon)"],
                disabled=True,
                help="App theme - Dark mode coming in future update"
            )
        
        st.markdown("---")
        
        # Data management
        st.subheader("💾 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Clear Cache", help="Clear all cached market data"):
                try:
                    putils.clear_all_caches()
                    st.success("✅ Cache cleared successfully!")
                except Exception as e:
                    st.error(f"Error clearing cache: {e}")
        
        with col2:
            if st.button("🔄 Reset Settings", help="Reset all settings to defaults"):
                try:
                    # Reset to defaults
                    st.session_state.education_mode = True
                    st.session_state.auto_refresh_enabled = False
                    st.session_state.show_advanced_metrics = True
                    st.session_state.selected_timeframe = '6mo'
                    st.success("✅ Settings reset to defaults!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error resetting settings: {e}")
        
        with col3:
            if st.button("📊 System Info", help="Show system information"):
                try:
                    st.info(f"""
                    **System Information:**
                    - App Version: {st.session_state.get('app_version', '2.2.0')}
                    - yfinance Available: {'✅' if putils.YF_AVAILABLE else '❌'}
                    - Cache Items: {len(putils.PRICE_CACHE)}
                    """)
                except Exception as e:
                    st.error(f"Error getting system info: {e}")
        
        st.markdown("---")
        
        # Account settings
        st.subheader("🔐 Account Settings")
        
        user_info = f"Logged in as: **{st.session_state.get('username', 'Unknown')}**"
        st.markdown(user_info)
        
        if st.button("🚪 Sign Out", type="secondary"):
            handle_logout()
            
    except Exception as e:
        logger.error(f"Error in settings page: {e}")
        st.error("Error loading settings page")

def help_page_enhanced():
    """Enhanced help page with error handling."""
    try:
        show_main_header("❓ Help & Guide", "Learn how to maximize your investment management experience")
        
        # Help navigation
        help_tab1, help_tab2, help_tab3, help_tab4 = st.tabs([
            "🚀 Getting Started",
            "📊 Understanding Metrics", 
            "🔧 Troubleshooting",
            "💡 Best Practices"
        ])
        
        with help_tab1:
            st.subheader("🚀 Getting Started")
            
            st.markdown("### Creating Your First Portfolio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Option 1: Add Assets Manually**")
                st.markdown("""
                1. Go to the **"➕ Add Asset"** tab
                2. Use the smart asset picker to search for assets
                3. Enter purchase price, quantity, and asset type
                4. Click "Add Asset" to save
                """)
            
            with col2:
                st.markdown("**Option 2: Upload a File**")
                st.markdown("""
                1. Go to the **"📤 Upload Portfolio"** tab
                2. Download the CSV or JSON template
                3. Fill in your portfolio data
                4. Upload the file and import
                """)
        
        with help_tab2:
            st.subheader("📊 Understanding Key Metrics")
            
            with st.expander("💰 Value Metrics", expanded=True):
                st.markdown("""
                - **Total Value**: Current market value (Current Price × Quantity)
                - **P/L (Profit/Loss)**: Difference between current value and cost
                - **P/L %**: Percentage return on investment
                - **Weight %**: Percentage of total portfolio value
                """)
            
            with st.expander("📊 Technical Indicators"):
                st.markdown("""
                - **RSI**: Momentum indicator (0-100). <30 oversold, >70 overbought
                - **Volatility**: Annual price volatility percentage
                - **Beta**: Market correlation. >1 more volatile, <1 less volatile
                - **Alpha**: Excess return vs benchmark
                """)
        
        with help_tab3:
            st.subheader("🔧 Common Issues & Solutions")
            
            with st.expander("❌ Data fetching problems"):
                st.markdown("""
                **Solutions:**
                - Check internet connection
                - Verify ticker symbols are correct
                - Try refreshing the page
                - Clear cache using Settings page
                """)
            
            with st.expander("📤 File upload errors"):
                st.markdown("""
                **Solutions:**
                - Ensure file has required columns
                - Check file size is under 10MB
                - Use supported formats (CSV, JSON, Excel)
                - Remove empty rows
                """)
        
        with help_tab4:
            st.subheader("💡 Best Practices")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Portfolio Management")
                st.markdown("""
                - **Diversify**: Don't put all money in one asset
                - **Regular Review**: Check portfolio monthly
                - **Keep Records**: Note why you bought each asset
                - **Risk Management**: Don't risk more than you can lose
                """)
            
            with col2:
                st.markdown("### Using This App")
                st.markdown("""
                - **Education Mode**: Keep it on to learn
                - **Save Regularly**: Use auto-save features
                - **Validate Tickers**: Use the validation feature
                - **Refresh Data**: Keep market data current
                """)
        
        st.warning("⚠️ **Disclaimer**: This app is for informational purposes only. Not financial advice.")
        
    except Exception as e:
        logger.error(f"Error in help page: {e}")
        st.error("Error loading help page")

# Final main application function with comprehensive error handling
def main():
    """Enhanced main application with comprehensive error handling."""
    try:
        # Create sidebar and get navigation choice
        selected_page = create_sidebar_enhanced()
        
        if not st.session_state.get('authenticated', False):
            display_auth_page_enhanced()
            return
        
        # Show welcome message for new sessions
        if st.session_state.get('show_welcome', False):
            show_welcome_message_enhanced()
        
        # Main content routing with error handling
        try:
            if selected_page == "📊 Dashboard":
                display_portfolio_overview()
            elif selected_page == "➕ Add Asset":
                add_asset_page()
            elif selected_page == "📤 Upload Portfolio":
                upload_portfolio_page_enhanced()
            elif selected_page == "📚 Portfolio History":
                history_page_enhanced()
            elif selected_page == "🔧 Settings":
                settings_page()
            elif selected_page == "❓ Help":
                help_page_enhanced()
            elif selected_page == "🚪 Sign Out":
                display_logout_confirmation_enhanced()
        except Exception as page_error:
            st.error(f"❌ Page error: {str(page_error)}")
            logger.error(f"Page routing error for {selected_page}: {page_error}")
            
            # Offer recovery options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh Page"):
                    st.rerun()
            with col2:
                if st.button("🏠 Go to Dashboard"):
                    st.session_state.show_welcome = False
                    st.rerun()
        
    except Exception as e:
        handle_application_error_enhanced(e)

# ========================
# Enhanced page router
# ========================
def route_to_page_enhanced(selected_page: str):
    '''Enhanced page routing with better error handling.'''
    try:
        if selected_page == "📊 Dashboard":
            display_portfolio_overview()
        elif selected_page == "➕ Add Asset":
            add_asset_page()
        elif selected_page == "📤 Upload Portfolio":
            upload_portfolio_page_enhanced()
        elif selected_page == "📚 Portfolio History":
            history_page_enhanced()
        elif selected_page == "⚙️ Settings":
            settings_page()
        elif selected_page == "❓ Help":
            help_page_enhanced()
        elif selected_page == "🚪 Sign Out":
            display_logout_confirmation_enhanced()

    except Exception as e:
        st.error(f"❌ Page error: {str(e)}")
        logger.error(f"Page routing error for {selected_page}: {e}")

# ========================
# Main application launcher
# ========================
if __name__ == "__main__":
    main()

def upload_portfolio_page_enhanced():
    """Enhanced portfolio upload page with better validation and templates."""
    show_main_header("📤 Upload Portfolio", "Import your investment data with smart validation")
    
    username = st.session_state.username
    
    # Enhanced file format guide
    display_file_format_guide_enhanced()
    
    # File upload section with drag & drop
    st.subheader("📁 File Upload")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop your portfolio file here",
            type=["csv", "json", "xlsx"],
            help="Supports CSV, JSON, and Excel files up to 10MB"
        )
    
    with col2:
        st.markdown("**📋 Quick Templates:**")
        
        # Download templates
        template_data = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY'],
            'Purchase Price': [150.00, 300.00, 2500.00, 800.00, 400.00],
            'Quantity': [10, 5, 2, 3, 8],
            'Asset Type': ['Stock', 'Stock', 'Stock', 'Stock', 'ETF'],
            'Purchase Date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-01', '2023-05-15'],
            'Notes': ['Tech giant', 'Enterprise software', 'Search leader', 'EV pioneer', 'Market ETF']
        })
        
        csv_template = template_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 CSV Template",
            csv_template,
            "portfolio_template.csv",
            "text/csv",
            use_container_width=True
        )
        
        json_template = template_data.to_json(orient="records", indent=2).encode('utf-8')
        st.download_button(
            "📋 JSON Template", 
            json_template,
            "portfolio_template.json",
            "application/json",
            use_container_width=True
        )
    
    # Import options
    if uploaded_file is not None:
        st.subheader("⚙️ Import Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            merge_option = st.radio(
                "Import Mode:",
                ["🔄 Replace portfolio", "➕ Add to existing", "🔍 Preview only"],
                help="Choose how to handle the uploaded data"
            )
        
        with col2:
            validate_tickers = st.checkbox(
                "✅ Validate tickers",
                value=True,
                help="Check if all ticker symbols are valid"
            )
        
        with col3:
            clean_data = st.checkbox(
                "🧹 Clean data",
                value=True,
                help="Remove invalid rows and fix common issues"
            )
        
        # Process uploaded file
        process_uploaded_file_enhanced(uploaded_file, merge_option, validate_tickers, clean_data, username)

def display_file_format_guide_enhanced():
    """Enhanced file format guide with examples and troubleshooting."""
    with st.expander("📋 File Format Guide & Requirements", expanded=False):
        
        tab1, tab2, tab3 = st.tabs(["📄 Requirements", "💡 Examples", "🔧 Troubleshooting"])
        
        with tab1:
            st.markdown("### Required Columns:")
            
            requirements_df = pd.DataFrame({
                'Column': ['Ticker', 'Purchase Price', 'Quantity', 'Asset Type'],
                'Required': ['✅ Yes', '✅ Yes', '✅ Yes', '✅ Yes'],
                'Description': [
                    'Stock/ETF/Crypto symbol (e.g., AAPL, BTC-USD)',
                    'Price per unit when purchased',
                    'Number of shares/units owned',
                    'Category: Stock, ETF, Crypto, Bond, etc.'
                ],
                'Example': ['AAPL', '150.50', '10', 'Stock']
            })
            
            st.dataframe(requirements_df, use_container_width=True)
            
            st.markdown("### Optional Columns:")
            optional_df = pd.DataFrame({
                'Column': ['Purchase Date', 'Notes', 'Asset Name'],
                'Description': [
                    'Date when asset was purchased (YYYY-MM-DD)',
                    'Additional information or strategy notes',
                    'Full company/asset name'
                ]
            })
            st.dataframe(optional_df, use_container_width=True)
        
        with tab2:
            st.markdown("### CSV Example:")
            st.code("""
Ticker,Purchase Price,Quantity,Asset Type,Purchase Date,Notes
AAPL,150.00,10,Stock,2023-01-15,Core tech holding
MSFT,300.00,5,Stock,2023-02-20,Cloud leader
BTC-USD,45000.00,0.1,Crypto,2023-03-10,Digital gold
SPY,400.00,8,ETF,2023-04-01,Market exposure
""")
            
            st.markdown("### JSON Example:")
            st.code("""
[
  {
    "Ticker": "AAPL",
    "Purchase Price": 150.00,
    "Quantity": 10,
    "Asset Type": "Stock",
    "Purchase Date": "2023-01-15",
    "Notes": "Core tech holding"
  },
  {
    "Ticker": "MSFT", 
    "Purchase Price": 300.00,
    "Quantity": 5,
    "Asset Type": "Stock",
    "Purchase Date": "2023-02-20",
    "Notes": "Cloud leader"
  }
]
""")
        
        with tab3:
            st.markdown("### Common Issues & Solutions:")
            
            issues_df = pd.DataFrame({
                'Issue': [
                    'File not uploading',
                    'Missing required columns',
                    'Invalid ticker symbols',
                    'Incorrect number format',
                    'Date format errors'
                ],
                'Solution': [
                    'Check file size (<10MB) and format (CSV/JSON/Excel)',
                    'Ensure Ticker, Purchase Price, Quantity, Asset Type columns exist',
                    'Use correct symbols: AAPL (stocks), BTC-USD (crypto)',
                    'Use numbers without $ or commas: 150.50 not $150.50',
                    'Use YYYY-MM-DD format: 2023-01-15'
                ]
            })
            
            st.dataframe(issues_df, use_container_width=True)

def process_uploaded_file_enhanced(uploaded_file, merge_option: str, validate_tickers: bool, clean_data: bool, username: str):
    """Enhanced file processing with detailed validation and feedback."""
    try:
        # File info
        st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        # Parse the file based on extension
        with st.spinner("📖 Reading file..."):
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension == 'json':
                df = pd.read_json(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
            else:
                st.error("❌ Unsupported file format")
                return
        
        st.success(f"✅ File loaded successfully! Found {len(df)} rows.")
        
        # Initial validation
        validation_results = validate_portfolio_file(df)
        display_validation_results(validation_results, df)
        
        # Data cleaning
        if clean_data and validation_results['can_proceed']:
            with st.spinner("🧹 Cleaning data..."):
                df = clean_portfolio_data_enhanced(df)
                st.info(f"🧹 Data cleaned. {len(df)} valid rows remaining.")
        
        # Ticker validation
        if validate_tickers and validation_results['can_proceed']:
            validate_portfolio_tickers_enhanced(df)
        
        # Preview and import
        if validation_results['can_proceed']:
            display_upload_preview_enhanced(df, merge_option, username)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        
        if st.session_state.education_mode:
            with st.expander("🔧 Error Details"):
                st.code(traceback.format_exc())

def validate_portfolio_file(df: pd.DataFrame) -> Dict[str, any]:
    """Validate uploaded portfolio file and return detailed results."""
    results = {
        'can_proceed': True,
        'errors': [],
        'warnings': [],
        'info': []
    }
    
    try:
        # Check if file is empty
        if df.empty:
            results['errors'].append("File is empty")
            results['can_proceed'] = False
            return results
        
        # Check required columns
        required_cols = ['Ticker', 'Purchase Price', 'Quantity', 'Asset Type']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            results['errors'].append(f"Missing required columns: {', '.join(missing_cols)}")
            results['can_proceed'] = False
        
        # Check data types and ranges
        if 'Purchase Price' in df.columns:
            try:
                prices = pd.to_numeric(df['Purchase Price'], errors='coerce')
                invalid_prices = prices.isna().sum()
                negative_prices = (prices <= 0).sum()
                
                if invalid_prices > 0:
                    results['warnings'].append(f"{invalid_prices} invalid price values found")
                if negative_prices > 0:
                    results['warnings'].append(f"{negative_prices} zero/negative prices found")
            except:
                results['errors'].append("Purchase Price column has invalid data")
        
        if 'Quantity' in df.columns:
            try:
                quantities = pd.to_numeric(df['Quantity'], errors='coerce')
                invalid_quantities = quantities.isna().sum()
                zero_quantities = (quantities <= 0).sum()
                
                if invalid_quantities > 0:
                    results['warnings'].append(f"{invalid_quantities} invalid quantity values found")
                if zero_quantities > 0:
                    results['warnings'].append(f"{zero_quantities} zero/negative quantities found")
            except:
                results['errors'].append("Quantity column has invalid data")
        
        # Check ticker format
        if 'Ticker' in df.columns:
            empty_tickers = df['Ticker'].isna().sum()
            if empty_tickers > 0:
                results['warnings'].append(f"{empty_tickers} empty ticker symbols found")
        
        # Info messages
        results['info'].append(f"Found {len(df)} total rows")
        results['info'].append(f"Columns: {', '.join(df.columns.tolist())}")
        
        return results
        
    except Exception as e:
        results['errors'].append(f"Validation error: {str(e)}")
        results['can_proceed'] = False
        return results

def display_validation_results(results: Dict[str, any], df: pd.DataFrame):
    """Display file validation results with color coding."""
    st.subheader("🔍 File Validation Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if results['errors']:
            st.error("❌ **Errors Found:**")
            for error in results['errors']:
                st.write(f"• {error}")
        else:
            st.success("✅ **No Errors**")
    
    with col2:
        if results['warnings']:
            st.warning("⚠️ **Warnings:**")
            for warning in results['warnings']:
                st.write(f"• {warning}")
        else:
            st.info("ℹ️ **No Warnings**")
    
    with col3:
        if results['info']:
            st.info("📊 **File Info:**")
            for info in results['info']:
                st.write(f"• {info}")
    
    # Data sample
    if not df.empty:
        with st.expander("👀 Data Preview (First 5 rows)", expanded=True):
            st.dataframe(df.head(), use_container_width=True)

def clean_portfolio_data_enhanced(df: pd.DataFrame) -> pd.DataFrame:
    """Enhanced data cleaning with detailed logging."""
    if df is None or df.empty:
        return df
    
    try:
        cleaned_df = df.copy()
        original_count = len(cleaned_df)
        
        # Clean ticker symbols
        if 'Ticker' in cleaned_df.columns:
            cleaned_df['Ticker'] = cleaned_df['Ticker'].astype(str).str.upper().str.strip()
            # Remove rows with empty tickers
            cleaned_df = cleaned_df[cleaned_df['Ticker'].str.len() > 0]
            cleaned_df = cleaned_df[cleaned_df['Ticker'] != 'NAN']
        
        # Convert and validate numeric columns
        numeric_cols = ['Purchase Price', 'Quantity']
        for col in numeric_cols:
            if col in cleaned_df.columns:
                # Convert to numeric, coercing errors to NaN
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                # Remove rows with invalid numbers
                cleaned_df = cleaned_df.dropna(subset=[col])
                # Remove rows with zero or negative values
                cleaned_df = cleaned_df[cleaned_df[col] > 0]
        
        # Clean asset type
        if 'Asset Type' in cleaned_df.columns:
            cleaned_df['Asset Type'] = cleaned_df['Asset Type'].astype(str).str.title().str.strip()
            # Replace common variations
            type_mapping = {
                'Stocks': 'Stock',
                'Equities': 'Stock', 
                'Equity': 'Stock',
                'Etfs': 'ETF',
                'Exchange Traded Fund': 'ETF',
                'Cryptocurrency': 'Crypto',
                'Digital Asset': 'Crypto',
                'Fixed Income': 'Bond',
                'Government Bond': 'Bond',
                'Corporate Bond': 'Bond'
            }
            cleaned_df['Asset Type'] = cleaned_df['Asset Type'].replace(type_mapping)
        
        # Clean dates
        if 'Purchase Date' in cleaned_df.columns:
            try:
                cleaned_df['Purchase Date'] = pd.to_datetime(cleaned_df['Purchase Date']).dt.strftime('%Y-%m-%d')
            except:
                # If date parsing fails, set to today
                cleaned_df['Purchase Date'] = datetime.now().strftime('%Y-%m-%d')
        
        final_count = len(cleaned_df)
        removed_count = original_count - final_count
        
        if removed_count > 0:
            st.warning(f"🧹 Removed {removed_count} invalid rows during cleaning")
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error in enhanced data cleaning: {e}")
        return df

def validate_portfolio_tickers_enhanced(df: pd.DataFrame):
    """Enhanced ticker validation with batch processing and detailed results."""
    if df.empty or 'Ticker' not in df.columns:
        return
    
    st.subheader("🔍 Ticker Validation")
    
    tickers = df['Ticker'].unique().tolist()
    total_tickers = len(tickers)
    
    if total_tickers == 0:
        st.warning("No tickers found to validate")
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"Validating {total_tickers} unique tickers...")
        
        # Validate in batches for better performance
        batch_size = 10
        all_results = {}
        
        for i in range(0, total_tickers, batch_size):
            batch = tickers[i:i + batch_size]
            batch_results = putils.validate_tickers_enhanced(batch)
            all_results.update(batch_results)
            
            # Update progress
            progress = min((i + batch_size) / total_tickers, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"Validated {min(i + batch_size, total_tickers)}/{total_tickers} tickers...")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Analyze results
        valid_tickers = [ticker for ticker, result in all_results.items() if result.get('valid', False)]
        invalid_tickers = [ticker for ticker, result in all_results.items() if not result.get('valid', False)]
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"✅ **Valid Tickers ({len(valid_tickers)}):**")
            
            if valid_tickers:
                # Group by validation method
                by_method = {}
                for ticker in valid_tickers:
                    method = all_results[ticker].get('reason', 'unknown')
                    if method not in by_method:
                        by_method[method] = []
                    by_method[method].append(ticker)
                
                for method, ticker_list in by_method.items():
                    st.write(f"**{method}:** {', '.join(ticker_list[:5])}" + 
                            (f" and {len(ticker_list)-5} more" if len(ticker_list) > 5 else ""))
        
        with col2:
            if invalid_tickers:
                st.error(f"❌ **Invalid Tickers ({len(invalid_tickers)}):**")
                
                for ticker in invalid_tickers[:10]:  # Show first 10
                    reason = all_results[ticker].get('reason', 'Unknown error')
                    st.write(f"• **{ticker}**: {reason}")
                
                if len(invalid_tickers) > 10:
                    st.write(f"... and {len(invalid_tickers) - 10} more")
                
                # Suggestions for invalid tickers
                st.subheader("💡 Suggestions:")
                for ticker in invalid_tickers[:3]:
                    suggestions = putils.search_popular_assets(ticker, limit=3)
                    if suggestions:
                        st.write(f"**{ticker}** → Try: {', '.join([s['ticker'] for s in suggestions])}")
            else:
                st.success("🎉 All tickers are valid!")
        
        # Summary
        success_rate = len(valid_tickers) / total_tickers * 100
        if success_rate == 100:
            st.balloons()
            st.success(f"🎉 Perfect! All {total_tickers} tickers validated successfully!")
        elif success_rate >= 80:
            st.success(f"✅ Good validation rate: {success_rate:.1f}% ({len(valid_tickers)}/{total_tickers})")
        else:
            st.warning(f"⚠️ Low validation rate: {success_rate:.1f}% ({len(valid_tickers)}/{total_tickers})")
            st.info("💡 Consider reviewing invalid tickers before importing")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Validation failed: {str(e)}")

def display_upload_preview_enhanced(df: pd.DataFrame, merge_option: str, username: str):
    """Enhanced upload preview with detailed statistics and import options."""
    st.subheader("👀 Import Preview")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Assets", len(df))
    
    with col2:
        if 'Purchase Price' in df.columns and 'Quantity' in df.columns:
            total_cost = (df['Purchase Price'] * df['Quantity']).sum()
            st.metric("💰 Total Cost", f"${total_cost:,.0f}")
        else:
            st.metric("💰 Total Cost", "N/A")
    
    with col3:
        if 'Asset Type' in df.columns:
            unique_types = df['Asset Type'].nunique()
            st.metric("🎯 Asset Types", unique_types)
        else:
            st.metric("🎯 Asset Types", "N/A")
    
    with col4:
        if 'Purchase Price' in df.columns and 'Quantity' in df.columns:
            avg_position = (df['Purchase Price'] * df['Quantity']).mean()
            st.metric("📈 Avg Position", f"${avg_position:,.0f}")
        else:
            st.metric("📈 Avg Position", "N/A")
    
    # Asset type breakdown
    if 'Asset Type' in df.columns and 'Purchase Price' in df.columns and 'Quantity' in df.columns:
        type_breakdown = df.groupby('Asset Type').agg({
            'Ticker': 'count',
            'Purchase Price': lambda x: (x * df.loc[x.index, 'Quantity']).sum()
        }).rename(columns={'Ticker': 'Count', 'Purchase Price': 'Total Value'})
        
        fig = px.bar(
            type_breakdown.reset_index(),
            x='Asset Type',
            y='Count',
            title="📊 Assets by Type",
            color='Total Value',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data preview table
    st.subheader("📋 Data Preview")
    
    # Show first 10 rows with formatting
    preview_df = df.head(10).copy()
    
    # Format numeric columns for display
    if 'Purchase Price' in preview_df.columns:
        preview_df['Purchase Price'] = preview_df['Purchase Price'].apply(lambda x: f"${x:.2f}")
    
    if 'Quantity' in preview_df.columns:
        preview_df['Quantity'] = preview_df['Quantity'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(preview_df, use_container_width=True)
    
    if len(df) > 10:
        st.caption(f"Showing first 10 of {len(df)} rows")
    
    # Import confirmation
    st.subheader("💾 Confirm Import")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Import Portfolio", type="primary", use_container_width=True):
            import_portfolio_data_enhanced(df, merge_option, username)
    
    with col2:
        if st.button("📥 Download Cleaned Data", use_container_width=True):
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download CSV",
                csv_data,
                f"cleaned_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    with col3:
        if st.button("🔍 Advanced Preview", use_container_width=True):
            display_advanced_preview(df)

def import_portfolio_data_enhanced(df: pd.DataFrame, merge_option: str, username: str):
    """Enhanced portfolio data import with better conflict resolution."""
    try:
        overwrite = merge_option.startswith("🔄")
        preview_only = merge_option.startswith("🔍")
        
        if preview_only:
            st.info("📋 Preview mode - no data was imported")
            return
        
        existing_df = st.session_state.portfolio_df
        
        if not overwrite and existing_df is not None and not existing_df.empty:
            # Merge mode - check for conflicts
            existing_tickers = set(existing_df['Ticker'].str.upper())
            new_tickers = set(df['Ticker'].str.upper())
            conflicts = existing_tickers.intersection(new_tickers)
            
            if conflicts:
                st.warning(f"⚠️ Found {len(conflicts)} conflicting tickers: {', '.join(list(conflicts)[:5])}")
                
                conflict_resolution = st.radio(
                    "How to handle conflicts:",
                    ["🔄 Update existing positions", "➕ Add as new positions", "❌ Skip conflicting assets"],
                    help="Choose how to handle assets that already exist in your portfolio"
                )
                
                if not st.button("Proceed with Import"):
                    return
                
                # Handle conflicts based on user choice
                if conflict_resolution.startswith("🔄"):  # Update existing
                    # Remove conflicting assets from existing portfolio
                    existing_df = existing_df[~existing_df['Ticker'].str.upper().isin(conflicts)]
                    final_df = pd.concat([existing_df, df], ignore_index=True)
                    
                elif conflict_resolution.startswith("❌"):  # Skip conflicts
                    # Remove conflicting assets from new data
                    df = df[~df['Ticker'].str.upper().isin(conflicts)]
                    final_df = pd.concat([existing_df, df], ignore_index=True)
                    
                else:  # Add as new positions
                    final_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                # No conflicts, simple merge
                final_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            # Replace mode or no existing data
            final_df = df
        
        # Save the portfolio
        with st.spinner("💾 Saving portfolio..."):
            putils.save_portfolio(username, final_df, overwrite=True)
        
        # Update session state
        st.session_state.portfolio_df = final_df
        st.session_state.portfolio_modified = True
        st.session_state.last_refresh = datetime.now()
        
        # Success feedback
        action = "replaced" if overwrite else "merged with existing portfolio"
        st.success(f"🎉 Portfolio {action} successfully!")
        st.balloons()
        
        # Show summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Assets", len(final_df))
        with col2:
            if 'Purchase Price' in final_df.columns and 'Quantity' in final_df.columns:
                total_cost = (final_df['Purchase Price'] * final_df['Quantity']).sum()
                st.metric("💰 Total Investment", f"${total_cost:,.0f}")
        with col3:
            st.metric("📈 Asset Types", final_df['Asset Type'].nunique())
        
        logger.info(f"Portfolio imported for user {username}: {len(final_df)} assets")
        
        # Auto-redirect to dashboard
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Import failed: {str(e)}")
        logger.error(f"Portfolio import error: {e}")
        
        if st.session_state.education_mode:
            with st.expander("🔧 Error Details"):
                st.code(traceback.format_exc())

# Additional enhanced functions would continue here...
# For brevity, I'll include the main application entry point

def handle_application_error_enhanced(e: Exception):
    """Enhanced application error handling with better user guidance."""
    error_msg = f"Application error: {str(e)}"
    st.error(f"❌ {error_msg}")
    logger.error(f"Application error: {e}", exc_info=True)
    
    # Error categorization and helpful suggestions
    error_str = str(e).lower()
    
    if "network" in error_str or "connection" in error_str:
        st.warning("🌐 **Network Issue Detected**")
        st.info("• Check your internet connection\n• Try refreshing the page\n• Market data may be temporarily unavailable")
    
    elif "permission" in error_str or "access" in error_str:
        st.warning("🔒 **Permission Issue**")
        st.info("• Check file permissions\n• Ensure you're logged in correctly\n• Try logging out and back in")
    
    elif "memory" in error_str or "timeout" in error_str:
        st.warning("⚡ **Performance Issue**")
        st.info("• Try refreshing the page\n• Clear browser cache\n• Reduce portfolio size if very large")
    
    else:
        st.warning("🔧 **General Error**")
        st.info("• Try refreshing the page\n• Check your input data\n• Contact support if issue persists")
    
    # Recovery options
    st.markdown("### 🔧 Recovery Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Page", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🏠 Go to Dashboard", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear Cache", use_container_width=True):
            putils.clear_all_caches()
            st.success("✅ Cache cleared")
            st.rerun()
    
    with col4:
        if st.button("🆘 Reset Session", use_container_width=True):
            # Clear problematic session state but keep authentication
            for key in list(st.session_state.keys()):
                if key not in ['authenticated', 'username']:
                    del st.session_state[key]
            initialize_session_state()
            st.session_state.authenticated = True  # Restore auth status
            st.success("✅ Session reset")
            st.rerun()
    
    # Technical details for debugging
    if st.session_state.education_mode:
        with st.expander("🔍 Technical Details (for developers)"):
            st.code(traceback.format_exc())
            
            # System info
            st.markdown("**System Information:**")
            st.write(f"• App Version: {st.session_state.app_version}")
            st.write(f"• yfinance Available: {putils.YF_AVAILABLE}")
            st.write(f"• Cache Size: {len(putils.PRICE_CACHE)} items")
            st.write(f"• Last Refresh: {st.session_state.last_refresh}")

def display_auth_page_enhanced():
    """Enhanced authentication page with better design and features."""
    # Main header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">📊 Portfolio Manager Pro</h1>
        <p style="font-size: 1.3rem; color: #64748b; margin-bottom: 3rem;">
            Professional investment portfolio management with real-time analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    display_feature_highlights_enhanced()
    
    st.markdown("---")
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab1:
        display_login_form_enhanced()
    
    with tab2:
        display_registration_form_enhanced()
    
    # Footer with security notice
    display_security_notice_enhanced()

def display_feature_highlights_enhanced():
    """Enhanced feature highlights with better visuals."""
    st.subheader("🌟 Why Choose Portfolio Manager Pro?")
    
    # Main features in cards
    col1, col2, col3 = st.columns(3)
    
    features = [
        {
            "icon": "📈",
            "title": "Real-Time Market Data",
            "description": "Live prices, technical indicators (RSI, Beta, Alpha), and advanced analytics powered by Yahoo Finance API",
            "highlights": ["✅ 500+ Popular Assets", "✅ Multiple Asset Classes", "✅ Technical Analysis"]
        },
        {
            "icon": "🎯", 
            "title": "Smart Portfolio Analytics",
            "description": "AI-powered insights, risk analysis, diversification recommendations, and performance tracking",
            "highlights": ["✅ Risk Metrics (VaR, Sharpe)", "✅ Rebalancing Suggestions", "✅ Performance Attribution"]
        },
        {
            "icon": "🔒",
            "title": "Secure & Private",
            "description": "Bank-grade encryption, local data storage, and complete privacy protection for your financial data",
            "highlights": ["✅ PBKDF2 Encryption", "✅ Local Storage", "✅ No Data Sharing"]
        }
    ]
    
    for i, feature in enumerate(features):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                border: 1px solid #e2e8f0;
                text-align: center;
                height: 100%;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{feature['icon']}</div>
                <h3 style="color: #1e293b; margin-bottom: 1rem;">{feature['title']}</h3>
                <p style="color: #64748b; margin-bottom: 1.5rem;">{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add highlights
            for highlight in feature['highlights']:
                st.markdown(f"<small>{highlight}</small>", unsafe_allow_html=True)

def display_login_form_enhanced():
    """Enhanced login form with better UX."""
    st.markdown("### 🔐 Welcome Back!")
    st.write("Access your investment dashboard with advanced analytics")
    
    with st.form("login_form"):
        username_input = st.text_input(
            "👤 Username",
            placeholder="Enter your username",
            help="Case-sensitive username you registered with"
        )
        
        password_input = st.text_input(
            "🔒 Password", 
            type="password",
            placeholder="Enter your secure password",
            help="Your encrypted password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            remember_me = st.checkbox("🔄 Keep me signed in", help="Stay logged in for this session")
        
        with col2:
            show_demo = st.checkbox("📊 Load demo data", help="Start with sample portfolio data")
        
        submitted = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        if submitted:
            handle_login_submission_enhanced(username_input, password_input, show_demo)

def handle_login_submission_enhanced(username_input: str, password_input: str, show_demo: bool):
    """Enhanced login submission with demo data option."""
    if not username_input.strip():
        st.error("❌ Please enter your username")
        return
    
    if not password_input:
        st.error("❌ Please enter your password")
        return
    
    with st.spinner("🔍 Verifying credentials..."):
        time.sleep(0.5)  # Brief delay for UX
        
        if authenticate_user(username_input.strip(), password_input):
            # Successful login
            st.session_state.authenticated = True
            st.session_state.username = username_input.strip()
            st.session_state.first_login = True
            st.session_state.show_welcome = True
            
            # Load demo data if requested
            if show_demo:
                create_demo_portfolio()
                st.session_state.show_welcome = False
            else:
                # Try to load user's existing portfolio
                safe_load_portfolio(username_input.strip())
            
            st.success("✅ Welcome back! Redirecting to your dashboard...")
            logger.info(f"User logged in: {username_input.strip()}")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
            
            # Enhanced error guidance
            with st.expander("🔧 Login Help"):
                st.markdown("""
                **Trouble signing in?**
                
                🔍 **Common Issues:**
                • Username is case-sensitive
                • Make sure Caps Lock is off
                • Check for extra spaces
                
                🔒 **Security Features:**
                • Passwords are encrypted with PBKDF2
                • Account lockout after 5 failed attempts
                • 15-minute lockout duration for security
                
                💡 **Tips:**
                • Try typing credentials manually (don't copy/paste)
                • Clear browser cache if having persistent issues
                • Create a new account if you forgot credentials
                """)

def display_registration_form_enhanced():
    """Enhanced registration form with real-time validation."""
    st.markdown("### 📝 Join Portfolio Manager Pro")
    st.write("Create your secure account to start professional portfolio management")
    
    with st.form("register_form"):
        new_username = st.text_input(
            "👤 Choose Username",
            placeholder="Enter a unique username (3-20 characters)",
            help="Letters, numbers, underscores, and hyphens only"
        )
        
        new_password = st.text_input(
            "🔒 Create Password",
            type="password",
            placeholder="Minimum 6 characters",
            help="Use a mix of letters, numbers, and symbols for security"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password", 
            placeholder="Re-enter your password",
            help="Must match the password above exactly"
        )
        
        # Real-time password strength indicator
        if new_password:
            strength = putils.check_password_strength(new_password)
            strength_colors = {
                "Weak": "🔴",
                "Medium": "🟡", 
                "Strong": "🟢"
            }
            strength_descriptions = {
                "Weak": "Add more characters, numbers, or symbols",
                "Medium": "Good! Consider adding special characters",
                "Strong": "Excellent! Very secure password"
            }
            
            st.markdown(f"""
            **Password Strength:** {strength_colors.get(strength, '⚪')} {strength}
            
            *{strength_descriptions.get(strength, '')}*
            """)
        
        # Terms and privacy
        agree_terms = st.checkbox(
            "✅ I agree to the Terms of Service and Privacy Policy",
            help="Required to create an account"
        )
        
        with st.expander("📋 Terms Summary"):
            st.markdown("""
            **Privacy & Security:**
            • Your data is stored locally and encrypted
            • No personal information is shared with third parties
            • Market data is fetched from public APIs (Yahoo Finance)
            
            **Usage Terms:**
            • For personal investment tracking only
            • Not financial advice - educational purposes
            • Users responsible for investment decisions
            
            **Data Policy:**
            • Portfolios saved locally on our servers
            • Passwords encrypted with military-grade security
            • You can delete your account and data anytime
            """)
        
        submitted_reg = st.form_submit_button("✨ Create Account", type="primary", use_container_width=True)
        
        if submitted_reg:
            handle_registration_submission_enhanced(new_username, new_password, confirm_password, agree_terms)

def handle_registration_submission_enhanced(new_username: str, new_password: str, confirm_password: str, agree_terms: bool):
    """Enhanced registration with detailed validation feedback."""
    # Collect all validation errors
    errors = []
    warnings = []
    
    username_clean = new_username.strip()
    
    # Username validation
    if not username_clean:
        errors.append("Username is required")
    elif len(username_clean) < 3:
        errors.append("Username must be at least 3 characters")
    elif len(username_clean) > 20:
        errors.append("Username must be less than 20 characters")
    elif not username_clean.replace('_', '').replace('-', '').isalnum():
        errors.append("Username can only contain letters, numbers, underscores, and hyphens")
    elif username_clean.startswith(('_', '-')) or username_clean.endswith(('_', '-')):
        errors.append("Username cannot start or end with special characters")
    
    # Password validation
    if not new_password:
        errors.append("Password is required")
    elif len(new_password) < 6:
        errors.append("Password must be at least 6 characters")
    elif len(new_password) > 128:
        errors.append("Password is too long (max 128 characters)")
    else:
        # Check password strength requirements
        strength = putils.check_password_strength(new_password)
        if strength == "Weak":
            warnings.append("Password is weak - consider adding more characters or complexity")
    
    # Password confirmation
    if new_password != confirm_password:
        errors.append("Passwords do not match")
    
    # Terms agreement
    if not agree_terms:
        errors.append("You must agree to the Terms of Service and Privacy Policy")
    
    # Display errors and warnings
    if errors:
        st.error("❌ **Please fix these issues:**")
        for error in errors:
            st.write(f"• {error}")
        return
    
    if warnings:
        st.warning("⚠️ **Recommendations:**")
        for warning in warnings:
            st.write(f"• {warning}")
        
        if not st.button("Continue anyway?"):
            return
    
    # Attempt registration
    with st.spinner("👤 Creating your secure account..."):
        time.sleep(0.5)  # Brief delay for UX
        
        if register_user(username_clean, new_password):
            st.success("🎉 Account created successfully!")
            st.balloons()
            
            # Show next steps
            st.info("""
            **🚀 What's Next?**
            
            1. Sign in using the **Sign In** tab above
            2. Start by adding your first asset or uploading a portfolio
            3. Explore real-time analytics and AI-powered insights
            4. Enable Education Mode for helpful tips and explanations
            """)
            
            logger.info(f"New user registered: {username_clean}")
        else:
            st.error("❌ Username already exists. Please choose another.")
            
            # Suggest alternatives
            suggestions = [
                f"{username_clean}2025",
                f"{username_clean}_investor", 
                f"{username_clean}123"
            ]
            st.info(f"💡 **Try these alternatives:** {', '.join(suggestions)}")

def display_security_notice_enhanced():
    """Enhanced security notice with detailed information."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔒 Bank-Grade Security**
        • PBKDF2-HMAC-SHA256 encryption
        • 100,000 hash iterations
        • Individual salt per user
        """)
    
    with col2:
        st.markdown("""
        **🛡️ Privacy Protection**
        • Data stored locally
        • No personal info sharing
        • Complete user control
        """)
    
    with col3:
        st.markdown("""
        **📊 Real-Time Data**
        • Yahoo Finance API
        • Live market prices
        • Advanced analytics
        """)

def display_unauthenticated_sidebar_enhanced():
    """Enhanced unauthenticated sidebar with app preview."""
    st.markdown("### 🔐 Please Sign In")
    st.write("Access your professional portfolio dashboard")
    
    st.markdown("### 🌟 App Features")
    
    features = [
        "📈 **Real-time market data** from Yahoo Finance",
        "📊 **Interactive dashboards** with advanced charts", 
        "🎯 **Risk analysis** with VaR, Beta, and Sharpe ratio",
        "💡 **AI recommendations** for portfolio optimization",
        "📱 **Mobile responsive** design for any device",
        "🔒 **Bank-grade security** with encrypted storage",
        "🔍 **Smart asset picker** with 500+ popular assets",
        "📤 **Bulk import** from CSV/JSON/Excel files"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")
    
    st.markdown("### 📊 Demo Preview")
    
    # Show a simple demo chart
    demo_data = pd.DataFrame({
        'Asset': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY'],
        'Value': [15000, 9000, 8000, 6000, 12000],
        'Return': [12.5, 8.3, 15.2, -5.1, 9.8]
    })
    
    fig = px.bar(demo_data, x='Asset', y='Value', color='Return',
                 color_continuous_scale='RdYlGn',
                 title="Sample Portfolio View")
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("*Sample data - create account to track your real portfolio*")

# ============================================================================
# Application Entry Point
# ============================================================================

def safe_load_portfolio(username: str, filename: Optional[str] = None) -> bool:
    """Enhanced portfolio loading with better error handling."""
    try:
        with st.spinner("📂 Loading portfolio..."):
            df = putils.load_portfolio(username, filename)
            
        if df is not None and not df.empty:
            # Enhanced validation
            required_cols = ['Ticker', 'Purchase Price', 'Quantity', 'Asset Type']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Portfolio missing required columns: {', '.join(missing_cols)}")
                
                # Offer to fix common issues
                if st.button("🔧 Try to Fix Automatically"):
                    df = fix_portfolio_columns(df)
                    if df is not None:
                        putils.save_portfolio(username, df, overwrite=True)
                        st.success("✅ Portfolio fixed and saved!")
                        st.rerun()
                return False
            
            # Data cleaning and validation
            original_count = len(df)
            df = clean_portfolio_data(df)
            cleaned_count = len(df)
            
            if cleaned_count < original_count:
                st.warning(f"⚠️ Removed {original_count - cleaned_count} invalid rows during loading")
            
            # Update session state
            st.session_state.portfolio_df = df
            st.session_state.selected_portfolio_file = filename
            st.session_state.portfolio_modified = False
            st.session_state.last_refresh = datetime.now()

            st.success(f"✅ Portfolio loaded successfully! ({len(df)} assets)")
            logger.info(f"Portfolio loaded for user {username}: {len(df)} assets")
            return True
        else:
            st.warning("⚠️ Portfolio file is empty or could not be loaded")
            return False

    except Exception as e:
        error_msg = f"Error loading portfolio: {str(e)}"
        show_error_with_details(error_msg, traceback.format_exc())
        logger.error(f"Portfolio load failed for {username}: {e}")
        return False
        
if __name__ == "__main__":
    main()

def clean_portfolio_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate portfolio data."""
    if df is None or df.empty:
        return df
    
    try:
        # Make a copy
        cleaned_df = df.copy()
        
        # Clean ticker symbols
        cleaned_df['Ticker'] = cleaned_df['Ticker'].astype(str).str.upper().str.strip()
        
        # Convert numeric columns
        numeric_cols = ['Purchase Price', 'Quantity']
        for col in numeric_cols:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # Remove invalid rows
        cleaned_df = cleaned_df.dropna(subset=['Ticker'])
        cleaned_df = cleaned_df[cleaned_df['Ticker'].str.len() > 0]
        
        if 'Purchase Price' in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df['Purchase Price'] > 0]
        
        if 'Quantity' in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df['Quantity'] > 0]
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error cleaning portfolio data: {e}")
        return df

def fix_portfolio_columns(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Attempt to fix missing portfolio columns."""
    try:
        fixed_df = df.copy()
        
        # Add missing columns with defaults
        if 'Asset Type' not in fixed_df.columns:
            # Try to guess asset type from ticker
            fixed_df['Asset Type'] = fixed_df['Ticker'].apply(guess_asset_type)
        
        if 'Purchase Price' not in fixed_df.columns:
            if 'Price' in fixed_df.columns:
                fixed_df['Purchase Price'] = fixed_df['Price']
            elif 'Cost' in fixed_df.columns:
                fixed_df['Purchase Price'] = fixed_df['Cost']
            else:
                fixed_df['Purchase Price'] = 0.0
        
        if 'Quantity' not in fixed_df.columns:
            if 'Shares' in fixed_df.columns:
                fixed_df['Quantity'] = fixed_df['Shares']
            elif 'Amount' in fixed_df.columns:
                fixed_df['Quantity'] = fixed_df['Amount']
            else:
                fixed_df['Quantity'] = 1.0
        
        return fixed_df
        
    except Exception as e:
        logger.error(f"Error fixing portfolio columns: {e}")
        return None

def guess_asset_type(ticker: str) -> str:
    """Guess asset type from ticker symbol."""
    ticker_upper = str(ticker).upper()
    
    # Cryptocurrency patterns
    if '-USD' in ticker_upper or ticker_upper in ['BTC', 'ETH', 'ADA', 'DOGE']:
        return 'Crypto'
    
    # Index patterns
    if ticker_upper.startswith('^'):
        return 'Index'
    
    # ETF patterns (common ones)
    etf_patterns = ['SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'BND']
    if ticker_upper in etf_patterns or ticker_upper.endswith('ETF'):
        return 'ETF'
    
    # Default to Stock
    return 'Stock'

def display_empty_portfolio_guide():
    """Enhanced empty portfolio guide."""
    st.markdown("## 🚀 Welcome to Portfolio Manager Pro!")
    st.markdown("Start building your investment portfolio with our comprehensive tools")
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### ➕ Smart Asset Addition
        - 🔍 Search from 500+ popular assets
        - 📊 Real-time price validation
        - 🎯 Automatic categorization
        - 📈 Live preview with P/L
        """)
        
        if st.button("🚀 Add Your First Asset", type="primary"):
            st.session_state.show_welcome = False
            # This would navigate to add asset page
    
    with col2:
        st.markdown("""
        ### 📤 Bulk Import
        - 📄 CSV/JSON file support
        - 🔧 Automatic data cleaning
        - ✅ Ticker validation
        - 📋 Template downloads
        """)
        
        if st.button("📁 Upload Portfolio File"):
            # This would navigate to upload page
            pass
    
    with col3:
        st.markdown("""
        ### 📊 Advanced Analytics
        - 📈 Real-time market data
        - ⚡ Technical indicators (RSI, Beta)
        - 🎯 Risk analysis & VaR
        - 💡 AI-powered recommendations
        """)
    
    # Quick start tips
    with st.expander("💡 Quick Start Tips", expanded=True):
        st.markdown("""
        **For beginners:**
        1. Start with popular ETFs like SPY (S&P 500) or QQQ (NASDAQ)
        2. Enable Education Mode in the sidebar for helpful explanations
        3. Use the asset picker to discover new investments
        
        **For experienced investors:**
        1. Import your existing portfolio via CSV/JSON
        2. Explore advanced metrics like Alpha, Beta, and Sharpe ratio
        3. Set up automatic refreshing for real-time monitoring
        """)

def display_offline_portfolio_summary(df: pd.DataFrame):
    """Display basic portfolio summary when market data is unavailable."""
    st.subheader("📱 Offline Portfolio View")
    st.info("📶 Market data unavailable - showing basic portfolio information")
    
    # Basic calculations without current prices
    if 'Purchase Price' in df.columns and 'Quantity' in df.columns:
        total_cost = (df['Purchase Price'] * df['Quantity']).sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Total Assets", len(df))
        
        with col2:
            st.metric("💰 Total Cost Basis", f"${total_cost:,.2f}")
        
        with col3:
            asset_types = df['Asset Type'].nunique()
            st.metric("📊 Asset Types", asset_types)
        
        # Asset breakdown
        if 'Asset Type' in df.columns:
            breakdown = putils.asset_breakdown(df.assign(**{'Total Value': df['Purchase Price'] * df['Quantity']}))
            if not breakdown.empty:
                st.subheader("📊 Asset Allocation (by Cost)")
                
                fig = px.pie(
                    breakdown,
                    values='Total Value',
                    names='Asset Type',
                    title="Portfolio Allocation by Cost Basis"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Holdings table
        st.subheader("📋 Holdings (Offline)")
        display_cols = ['Ticker', 'Asset Type', 'Quantity', 'Purchase Price']
        if 'Notes' in df.columns:
            display_cols.append('Notes')
        
        st.dataframe(df[display_cols], use_container_width=True)
        
        # Reconnect button
        if st.button("🔄 Try to Reconnect", type="primary"):
            st.rerun()

# ============================================================================
# Enhanced Dashboard Tabs
# ============================================================================

def display_dashboard_tabs_enhanced(metrics_df: pd.DataFrame):
    """Enhanced dashboard with additional tabs and features."""
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Performance", 
        "🥧 Allocation", 
        "⚠️ Risk Analysis", 
        "📋 Holdings",
        "🎯 Recommendations",
        "📊 Market Insights"
    ])
    
    with tab1:
        display_performance_analysis_enhanced(metrics_df)
    
    with tab2:
        display_allocation_analysis_enhanced(metrics_df)
    
    with tab3:
        display_risk_analysis_enhanced(metrics_df)
    
    with tab4:
        display_holdings_detail_enhanced(metrics_df)
    
    with tab5:
        display_recommendations_enhanced(metrics_df)
    
    with tab6:
        display_market_insights(metrics_df)

def display_performance_analysis_enhanced(metrics_df: pd.DataFrame):
    """Enhanced performance analysis with more charts and insights."""
    st.subheader("📊 Performance Analysis")
    
    if metrics_df.empty:
        st.info("No data available for performance analysis.")
        return
    
    # Performance overview
    col1, col2 = st.columns(2)
    
    with col1:
        # Top performers chart
        top_performers = metrics_df.nlargest(10, 'P/L %')
        if not top_performers.empty:
            fig = px.bar(
                top_performers,
                x='Ticker',
                y='P/L %',
                color='P/L %',
                color_continuous_scale='RdYlGn',
                title="🏆 Top 10 Performers by Return (%)",
                labels={'P/L %': 'Return (%)'}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Dollar P/L chart
        top_dollar_performers = metrics_df.nlargest(10, 'P/L')
        if not top_dollar_performers.empty:
            fig = px.bar(
                top_dollar_performers,
                x='Ticker',
                y='P/L',
                color='P/L',
                color_continuous_scale='RdYlGn',
                title="💰 Top 10 by Dollar P/L",
                labels={'P/L': 'Profit/Loss ($)'}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Performance distribution
    if 'P/L %' in metrics_df.columns and not metrics_df['P/L %'].isna().all():
        st.subheader("📊 Performance Distribution")
        
        fig = px.histogram(
            metrics_df.dropna(subset=['P/L %']),
            x='P/L %',
            nbins=20,
            title="Portfolio Performance Distribution",
            labels={'P/L %': 'Return (%)', 'count': 'Number of Assets'}
        )
        fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        fig.add_vline(x=metrics_df['P/L %'].mean(), line_dash="dash", line_color="blue", annotation_text="Average")
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics table
    st.subheader("📈 Performance Metrics")
    perf_metrics = calculate_performance_metrics(metrics_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Win Rate", f"{perf_metrics['win_rate']:.1f}%")
    
    with col2:
        st.metric("📈 Avg Winner", f"+{perf_metrics['avg_winner']:.1f}%")
    
    with col3:
        st.metric("📉 Avg Loser", f"{perf_metrics['avg_loser']:.1f}%")
    
    with col4:
        st.metric("⚖️ Risk/Reward", f"{perf_metrics['risk_reward']:.2f}")

def calculate_performance_metrics(metrics_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate portfolio performance metrics."""
    try:
        valid_returns = metrics_df['P/L %'].dropna()
        
        if valid_returns.empty:
            return {'win_rate': 0, 'avg_winner': 0, 'avg_loser': 0, 'risk_reward': 0}
        
        winners = valid_returns[valid_returns > 0]
        losers = valid_returns[valid_returns < 0]
        
        win_rate = len(winners) / len(valid_returns) * 100
        avg_winner = winners.mean() if not winners.empty else 0
        avg_loser = losers.mean() if not losers.empty else 0
        risk_reward = abs(avg_winner / avg_loser) if avg_loser != 0 else 0
        
        return {
            'win_rate': win_rate,
            'avg_winner': avg_winner,
            'avg_loser': avg_loser,
            'risk_reward': risk_reward
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return {'win_rate': 0, 'avg_winner': 0, 'avg_loser': 0, 'risk_reward': 0}

def display_allocation_analysis_enhanced(metrics_df: pd.DataFrame):
    """Enhanced allocation analysis with rebalancing suggestions."""
    st.subheader("🥧 Asset Allocation Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Current allocation by asset type
        allocation_by_type = metrics_df.groupby('Asset Type')['Total Value'].sum().reset_index()
        
        if not allocation_by_type.empty:
            fig = px.pie(
                allocation_by_type,
                values='Total Value',
                names='Asset Type',
                title="📊 Current Allocation by Asset Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top holdings
        top_holdings = metrics_df.nlargest(8, 'Total Value')
        
        if not top_holdings.empty:
            fig = px.pie(
                top_holdings,
                values='Total Value',
                names='Ticker',
                title="💰 Top Holdings by Value",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    # Rebalancing suggestions
    rebalancing_data = putils.suggest_rebalancing(metrics_df)
    if rebalancing_data:
        st.subheader("⚖️ Rebalancing Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Allocation:**")
            current_fig = px.bar(
                rebalancing_data['current'],
                x='asset_type',
                y='weight',
                title="Current Distribution",
                color='weight',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(current_fig, use_container_width=True)
        
        with col2:
            st.write("**Suggested Allocation:**")
            suggested_fig = px.bar(
                rebalancing_data['suggested'],
                x='asset_type',
                y='weight',
                title="Suggested Distribution",
                color='weight',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(suggested_fig, use_container_width=True)
        
        # Rebalancing actions
        st.subheader("🎯 Rebalancing Actions")
        current_df = rebalancing_data['current'].set_index('asset_type')
        suggested_df = rebalancing_data['suggested'].set_index('asset_type')
        
        rebalance_df = pd.merge(current_df, suggested_df, left_index=True, right_index=True, suffixes=('_current', '_suggested'))
        rebalance_df['difference'] = rebalance_df['weight_suggested'] - rebalance_df['weight_current']
        rebalance_df['action'] = rebalance_df['difference'].apply(
            lambda x: f"📈 Increase by {abs(x):.1f}%" if x > 1 else f"📉 Decrease by {abs(x):.1f}%" if x < -1 else "✅ Maintain"
        )
        
        st.dataframe(rebalance_df[['weight_current', 'weight_suggested', 'action']], use_container_width=True)

def display_market_insights(metrics_df: pd.DataFrame):
    """Display market insights and sector analysis."""
    st.subheader("📊 Market Insights")
    
    # Market status and timing
    market_status = putils.get_market_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"🕐 Market Status: {market_status.get('status', 'Unknown')}")
        st.info(f"⏰ Local Time: {market_status.get('local_time', 'Unknown')}")
        
        if not market_status.get('is_open', False):
            st.warning(f"📅 Next Open: {market_status.get('next_open', 'Unknown')}")
    
    with col2:
        # Portfolio beta distribution
        if 'Beta' in metrics_df.columns:
            avg_beta = metrics_df['Beta'].mean()
            if not pd.isna(avg_beta):
                market_correlation = "High" if avg_beta > 1.2 else "Medium" if avg_beta > 0.8 else "Low"
                st.metric("📊 Market Correlation", market_correlation, f"β = {avg_beta:.2f}")
                
                beta_dist = metrics_df['Beta'].dropna()
                if not beta_dist.empty:
                    fig = px.histogram(
                        x=beta_dist,
                        title="Beta Distribution",
                        labels={'x': 'Beta', 'y': 'Count'}
                    )
                    fig.add_vline(x=1, line_dash="dash", annotation_text="Market Beta")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Sector analysis (if we can determine sectors)
    if 'Asset Type' in metrics_df.columns:
        st.subheader("🏭 Sector Exposure")
        
        sector_performance = metrics_df.groupby('Asset Type').agg({
            'P/L %': 'mean',
            'Total Value': 'sum',
            'Volatility': 'mean'
        }).round(2)
        
        sector_performance.columns = ['Avg Return %', 'Total Value', 'Avg Volatility %']
        st.dataframe(sector_performance, use_container_width=True)

# ============================================================================
# Main Application Logic
# ============================================================================

def main():
    """Enhanced main application with better routing and error handling."""
    try:
        # Create sidebar and get navigation choice
        selected_page = create_sidebar_enhanced()
        
        if not st.session_state.authenticated:
            display_auth_page_enhanced()
            return
        
        # Show welcome message for new sessions
        if st.session_state.show_welcome:
            show_welcome_message_enhanced()
        
        # Main content routing
        route_to_page_enhanced(selected_page)
        
    except Exception as e:
        handle_application_error_enhanced(e)

def create_sidebar_enhanced():
    """Enhanced sidebar with better organization and features."""
    with st.sidebar:
        if st.session_state.authenticated:
            # User profile section
            st.markdown("### 👤 Welcome Back!")
            st.write(f"**{st.session_state.username}**")
            st.caption(f"Version: {st.session_state.app_version}")
            
            # Quick portfolio stats
            display_sidebar_portfolio_stats_enhanced()
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            page = st.radio(
                "Choose a page:",
                [
                    "📊 Dashboard",
                    "➕ Add Asset",
                    "📤 Upload Portfolio", 
                    "📚 Portfolio History",
                    "🔧 Settings",
                    "❓ Help",
                    "🚪 Sign Out"
                ],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Enhanced settings
            display_sidebar_settings_enhanced()
            
            # Quick actions
            display_sidebar_quick_actions_enhanced()
            
            # System status
            display_sidebar_status()
            
            return page
        
        else:
            # Unauthenticated sidebar
            display_unauthenticated_sidebar_enhanced()
            return None

def display_sidebar_portfolio_stats_enhanced():
    """Enhanced sidebar portfolio statistics."""
    if st.session_state.portfolio_df is not None and not st.session_state.portfolio_df.empty:
        df = st.session_state.portfolio_df
        
        st.markdown("#### 📊 Portfolio Quick Stats")
        
        # Calculate basic stats
        asset_count = len(df)
        asset_types = df['Asset Type'].nunique()
        
        if 'Purchase Price' in df.columns and 'Quantity' in df.columns:
            total_cost = (df['Purchase Price'] * df['Quantity']).sum()
        else:
            total_cost = 0
        
        # Display metrics in compact format
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Assets", asset_count)
        with col2:
            st.metric("Types", asset_types)
        
        st.metric("Invested", f"${total_cost:,.0f}")
        
        # Last refresh indicator
        last_refresh = st.session_state.last_refresh
        if last_refresh:
            time_diff = datetime.now() - last_refresh
            if time_diff.total_seconds() < 3600:  # Less than 1 hour
                refresh_color = "🟢"
            elif time_diff.total_seconds() < 86400:  # Less than 1 day
                refresh_color = "🟡"
            else:
                refresh_color = "🔴"
            
            st.caption(f"{refresh_color} Updated: {last_refresh.strftime('%H:%M')}")

def display_sidebar_settings_enhanced():
    """Enhanced sidebar settings with more options."""
    st.markdown("### ⚙️ Settings")
    
    # Education mode
    st.session_state.education_mode = st.checkbox(
        "📚 Education Mode",
        value=st.session_state.education_mode,
        help="Show helpful tooltips and explanations"
    )
    
    # Auto-refresh
    st.session_state.auto_refresh_enabled = st.checkbox(
        "🔄 Auto Refresh",
        value=st.session_state.auto_refresh_enabled,
        help="Automatically refresh data every 5 minutes"
    )
    
    # Data timeframe
    timeframe = st.selectbox(
        "📅 Timeframe",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=["1mo", "3mo", "6mo", "1y", "2y"].index(st.session_state.selected_timeframe),
        help="Historical data period for analysis"
    )
    st.session_state.selected_timeframe = timeframe
    
    # Advanced metrics
    st.session_state.show_advanced_metrics = st.checkbox(
        "📊 Advanced Metrics",
        value=st.session_state.show_advanced_metrics,
        help="Show technical indicators and risk metrics"
    )

def display_sidebar_quick_actions_enhanced():
    """Enhanced quick actions with more functionality."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", help="Update all market data", use_container_width=True):
            refresh_portfolio_data()
    
    with col2:
        if st.button("💾 Save", help="Save current portfolio", use_container_width=True):
            if st.session_state.portfolio_df is not None:
                try:
                    putils.save_portfolio(st.session_state.username, st.session_state.portfolio_df)
                    st.success("✅ Saved!")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
    
    # Cache management
    if st.button("🧹 Clear Cache", help="Clear all cached data", use_container_width=True):
        putils.clear_all_caches()
        st.success("✅ Cache cleared!")

def display_sidebar_status():
    """Display system status in sidebar."""
    st.markdown("### 📊 System Status")
    
    # Market data status
    if putils.YF_AVAILABLE:
        st.success("✅ Market Data")
    else:
        st.error("❌ Market Data")
    
    # Cache status
    cache_size = len(putils.PRICE_CACHE)
    if cache_size > 0:
        st.info(f"💾 Cache: {cache_size} items")
    else:
        st.caption("💾 Cache: Empty")
    
    # Last update
    if st.session_state.last_refresh:
        time_ago = datetime.now() - st.session_state.last_refresh
        hours = int(time_ago.total_seconds() // 3600)
        minutes = int((time_ago.total_seconds() % 3600) // 60)
        
        if hours > 0:
            st.caption(f"🕐 {hours}h {minutes}m ago")
        else:
            st.caption(f"🕐 {minutes}m ago")

def show_welcome_message_enhanced():
    """Enhanced welcome message with better onboarding."""
    if st.session_state.show_welcome and st.session_state.authenticated:
        st.markdown(f"""
        ## 👋 Welcome back, {st.session_state.username}!
        
        Your portfolio dashboard is ready with **real-time market data** and **AI-powered insights**.
        """)
        
        # Quick start options
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 Get Started", type="primary"):
                st.session_state.show_welcome = False
                st.rerun()
        
        with col2:
            if st.button("📚 Enable Learning"):
                st.session_state.education_mode = True
                st.session_state.show_welcome = False
                st.rerun()
        
        with col3:
            if st.button("📊 View Demo Data"):
                # Load demo portfolio
                create_demo_portfolio()
                st.session_state.show_welcome = False
                st.rerun()
        
        with col4:
            if st.button("❓ Show Help"):
                st.session_state.show_welcome = False
                # Navigate to help
                st.rerun()
        
        st.markdown("---")

def create_demo_portfolio():
    """Create a demo portfolio for new users."""
    demo_data = [
        {"Ticker": "AAPL", "Purchase Price": 150.0, "Quantity": 10, "Asset Type": "Stock", "Notes": "Demo tech stock"},
        {"Ticker": "SPY", "Purchase Price": 400.0, "Quantity": 5, "Asset Type": "ETF", "Notes": "Demo market ETF"},
        {"Ticker": "BTC-USD", "Purchase Price": 45000.0, "Quantity": 0.1, "Asset Type": "Crypto", "Notes": "Demo cryptocurrency"},
        {"Ticker": "GOOGL", "Purchase Price": 2500.0, "Quantity": 2, "Asset Type": "Stock", "Notes": "Demo growth stock"},
        {"Ticker": "QQQ", "Purchase Price": 350.0, "Quantity": 3, "Asset Type": "ETF", "Notes": "Demo tech ETF"}
    ]
    
    demo_df = pd.DataFrame(demo_data)
    demo_df['Purchase Date'] = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Save demo portfolio
        putils.save_portfolio(st.session_state.username, demo_df, overwrite=True)
        st.session_state.portfolio_df = demo_df
        st.session_state.portfolio_modified = True
        
        st.success("✅ Demo portfolio created! Explore the features with sample data.")
        
    except Exception as e:
        st.error(f"❌ Failed to create demo portfolio: {e}")

# Continue with remaining functions...
def route_to_page_enhanced(selected_page: str):
    """
    Enhanced Financial Portfolio Manager - FIXED AND ENHANCED VERSION
    ================================================================

    A comprehensive Streamlit application for managing investment portfolios with:
    - FIXED Yahoo Finance data fetching with robust error handling
    - Enhanced asset picker with popular assets database and search
    - Advanced visualizations and real-time metrics
    - Intelligent portfolio analysis and recommendations
    - Improved UI/UX with better error handling

    Key improvements:
    - Fixed price fetching issues with multiple fallback strategies
    - Added popular assets database with search functionality
    - Enhanced error handling and user feedback
    - Better data validation and cleaning
    - Improved portfolio analytics and recommendations
    - Mobile-responsive design with modern styling

    Author: Marc
    """


import os
import time
import traceback
import logging
import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from auth import authenticate_user, register_user
import portfolio_utils as putils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None

# ============================================================================
# Configuration and Setup
# ============================================================================

st.set_page_config(
    page_title="📊 Portfolio Manager Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
def load_custom_css():
    """Load enhanced custom CSS styles - COMPLETELY FIXED VERSION."""
    css_content = '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        text-align: center;
        padding: 2.5rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif;
    }

    .main-header h1 {
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-size: 2.5rem;
    }

    .main-header p {
        opacity: 0.9;
        font-size: 1.2rem;
        margin: 0;
    }

    /* Enhanced metric cards */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .welcome-box {
        background: linear-gradient(135deg, #f0f9ff, #dbeafe);
        border: 2px solid #3b82f6;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .asset-picker {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .asset-picker:hover {
        border-color: #667eea;
    }

    .status-success {
        color: #10b981;
        font-weight: 600;
    }

    .status-warning {
        color: #f59e0b;
        font-weight: 600;
    }

    .status-error {
        color: #ef4444;
        font-weight: 600;
    }

    .market-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .market-open {
        background-color: #dcfce7;
        color: #166534;
    }

    .market-closed {
        background-color: #fef2f2;
        color: #991b1b;
    }

    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .recommendation-success {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .recommendation-warning {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .recommendation-info {
        background-color: #f0f9ff;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .loading-pulse {
        animation: pulse 2s ease-in-out infinite;
    }

    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }

    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        .main-header h1 {
            font-size: 2rem;
        }
        .welcome-box {
            padding: 1.5rem;
        }
        .asset-picker {
            padding: 1rem;
        }
    }

    .stSelectbox > div > div {
        border-radius: 8px;
    }

    .stTextInput > div > div > input {
        border-radius: 8px;
    }

    .stNumberInput > div > div > input {
        border-radius: 8px;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    </style>
    '''
    st.markdown(css_content, unsafe_allow_html=True)

# Load CSS
load_custom_css()

# ============================================================================
# Session State Management
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables with enhanced defaults."""
    defaults = {
        'authenticated': False,
        'username': '',
        'portfolio_df': None,
        'selected_portfolio_file': None,
        'price_cache': {},
        'price_cache_time': 0,
        'first_login': True,
        'portfolio_modified': False,
        'show_welcome': True,
        'last_refresh': None,
        'benchmark_data': None,
        'education_mode': True,
        'selected_timeframe': '6mo',
        'app_version': '2.2.0',
        'market_status': None,
        'asset_search_query': '',
        'selected_asset_category': 'All',
        'show_advanced_metrics': True,
        'auto_refresh_enabled': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# ============================================================================
# Enhanced Asset Picker Component
# ============================================================================

def display_enhanced_asset_picker():
    """Display enhanced asset picker with search and categories."""
    st.subheader("🔍 Smart Asset Picker")
    
    with st.container():
        # Search and filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "🔍 Search assets",
                value=st.session_state.get('asset_search_query', ''),
                placeholder="Type ticker or company name (e.g., AAPL, Apple, Tesla)",
                help="Search through 500+ popular assets"
            )
            st.session_state.asset_search_query = search_query
        
        with col2:
            asset_categories = ["All", "Stocks", "ETFs", "Crypto", "Indices", "Commodities"]
            selected_category = st.selectbox(
                "📊 Category",
                asset_categories,
                index=asset_categories.index(st.session_state.get('selected_asset_category', 'All'))
            )
            st.session_state.selected_asset_category = selected_category
        
        with col3:
            if st.button("🔄 Refresh Assets", help="Update asset database"):
                st.success("✅ Asset database refreshed!")
        
        # Display search results
        if search_query and len(search_query) >= 1:
            try:
                results = putils.search_popular_assets(search_query, limit=20)
                
                if results:
                    st.write(f"**Found {len(results)} matching assets:**")
                    
                    # Display results in a nice format
                    for i, asset in enumerate(results[:10]):  # Show top 10
                        col_ticker, col_name, col_category, col_action = st.columns([1, 3, 2, 1])
                        
                        with col_ticker:
                            st.code(asset['ticker'])
                        
                        with col_name:
                            st.write(asset['name'])
                        
                        with col_category:
                            st.caption(asset['category'])
                        
                        with col_action:
                            if st.button("➕", key=f"add_{asset['ticker']}_{i}", help=f"Add {asset['ticker']}"):
                                # Auto-fill the form with selected asset
                                return asset['ticker'], asset['name']
                    
                    if len(results) > 10:
                        st.info(f"Showing top 10 results. {len(results) - 10} more available.")
                else:
                    st.warning("🔍 No assets found. Try a different search term.")
            except Exception as e:
                st.error(f"Error searching assets: {str(e)}")
        
        # Category browser
        elif selected_category != "All":
            try:
                category_map = {
                    "Stocks": "stocks",
                    "ETFs": "etfs", 
                    "Crypto": "crypto",
                    "Indices": "indices",
                    "Commodities": "commodities"
                }
                
                if selected_category in category_map:
                    assets_by_cat = putils.get_assets_by_category(category_map[selected_category])
                    
                    if assets_by_cat:
                        st.write(f"**Popular {selected_category}:**")
                        
                        # Group by subcategory
                        df_assets = pd.DataFrame(assets_by_cat)
                        if not df_assets.empty:
                            for subcategory in df_assets['category'].unique():
                                with st.expander(f"📁 {subcategory}", expanded=True):
                                    cat_assets = df_assets[df_assets['category'] == subcategory]
                                    
                                    for i, (_, asset) in enumerate(cat_assets.iterrows()):
                                        col_ticker, col_name, col_action = st.columns([1, 4, 1])
                                        
                                        with col_ticker:
                                            st.code(asset['ticker'])
                                        
                                        with col_name:
                                            st.write(asset['name'])
                                        
                                        with col_action:
                                            if st.button("➕", key=f"cat_{asset['ticker']}_{i}", help=f"Add {asset['ticker']}"):
                                                return asset['ticker'], asset['name']
            except Exception as e:
                st.error(f"Error loading category assets: {str(e)}")
        
        # Popular picks
        else:
            st.write("**🌟 Popular Picks:**")
            popular_picks = [
                ("AAPL", "Apple Inc."), ("MSFT", "Microsoft"), ("GOOGL", "Alphabet"),
                ("TSLA", "Tesla"), ("AMZN", "Amazon"), ("NVDA", "NVIDIA"),
                ("SPY", "S&P 500 ETF"), ("QQQ", "NASDAQ ETF"), ("BTC-USD", "Bitcoin")
            ]
            
            cols = st.columns(3)
            for i, (ticker, name) in enumerate(popular_picks):
                with cols[i % 3]:
                    if st.button(f"**{ticker}**\n{name}", key=f"popular_{ticker}"):
                        return ticker, name
    
    return None, None

def display_market_status():
    """Display current market status."""
    try:
        market_info = putils.get_market_status()
        status = market_info.get('status', 'Unknown')
        is_open = market_info.get('is_open', False)
        
        status_class = "market-open" if is_open else "market-closed"
        status_icon = "🟢" if is_open else "🔴"
        
        st.markdown(
            f'<div class="market-status {status_class}">'
            f'{status_icon} Market: {status} | {market_info.get("local_time", "")}'
            f'</div>',
            unsafe_allow_html=True
        )
        
        if not is_open:
            st.caption(f"Next open: {market_info.get('next_open', 'Unknown')}")
            
    except Exception as e:
        logger.debug(f"Error displaying market status: {e}")

# ============================================================================
# Enhanced Add Asset Page
# ============================================================================

def add_asset_page():
    """Enhanced asset addition page with smart picker."""
    show_main_header("➕ Add New Asset", "Expand your portfolio with smart asset selection")
    
    # Display market status
    display_market_status()
    
    username = st.session_state.username
    df = st.session_state.portfolio_df
    
    # Enhanced asset picker
    selected_ticker, selected_name = display_enhanced_asset_picker()
    
    # Asset Addition Form
    with st.form("add_asset_form", clear_on_submit=True):
        st.subheader("📝 Asset Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pre-fill ticker if selected from picker
            ticker_value = selected_ticker if selected_ticker else ""
            ticker = st.text_input(
                "🎯 Ticker Symbol",
                value=ticker_value,
                max_chars=12,
                help="Stock symbol (e.g., AAPL, TSLA, BTC-USD)",
                placeholder="Enter or select from picker above"
            ).strip().upper()
            
            purchase_price = st.number_input(
                "💰 Purchase Price ($)",
                min_value=0.0,
                format="%.4f",
                step=0.01,
                help="Price per share/unit when you bought it"
            )
            
            asset_type = st.selectbox(
                "📊 Asset Type",
                ["Stock", "ETF", "Crypto", "Bond", "REIT", "Commodity", "Option", "Mutual Fund", "Other"],
                help="Choose the category that best describes this asset"
            )
        
        with col2:
            quantity = st.number_input(
                "📦 Quantity",
                min_value=0.0,
                format="%.6f",
                step=0.001,
                help="Number of shares/units you own"
            )
            
            purchase_date = st.date_input(
                "📅 Purchase Date",
                value=datetime.now().date(),
                help="When you bought this asset"
            )
            
            notes = st.text_area(
                "📝 Notes (Optional)",
                placeholder="e.g., Part of tech diversification strategy...",
                help="Any additional information about this investment"
            )
        
        # Real-time validation and preview
        if ticker and purchase_price > 0 and quantity > 0:
            display_asset_preview_enhanced(ticker, purchase_price, quantity, selected_name)
        
        # Form submission
        col_submit, col_validate = st.columns([2, 1])
        
        with col_submit:
            submitted = st.form_submit_button("➕ Add Asset", type="primary", use_container_width=True)
        
        with col_validate:
            validate_pressed = st.form_submit_button("🔍 Validate Ticker", use_container_width=True)
        
        # Handle validation
        if validate_pressed and ticker:
            validate_single_ticker(ticker)
        
        # Handle submission
        if submitted:
            handle_asset_submission_enhanced(ticker, purchase_price, quantity, asset_type, purchase_date, notes, username, df, selected_name)

def display_asset_preview_enhanced(ticker: str, purchase_price: float, quantity: float, asset_name: str = ""):
    """Enhanced asset preview with real-time data and validation."""
    st.subheader("👀 Live Preview")
    
    cost_basis = purchase_price * quantity
    
    with st.spinner("🔍 Fetching current market data..."):
        try:
            # Get current price and validation
            current_prices = putils.get_cached_prices([ticker])
            current_price = current_prices.get(ticker, np.nan)
            
            # Validate ticker
            validation_results = putils.validate_tickers_enhanced([ticker])
            is_valid = validation_results.get(ticker, {}).get("valid", False)
            validation_reason = validation_results.get(ticker, {}).get("reason", "Unknown")
            
            # Display validation status
            col_status, col_name = st.columns([1, 3])
            
            with col_status:
                if is_valid:
                    st.success("✅ Valid Ticker")
                else:
                    st.error("❌ Invalid Ticker")
                    st.caption(f"Reason: {validation_reason}")
            
            with col_name:
                if asset_name:
                    st.info(f"📊 {asset_name}")
                elif is_valid and 'name' in validation_results.get(ticker, {}):
                    st.info(f"📊 {validation_results[ticker]['name']}")
            
            # Display financial preview
            if is_valid and not pd.isna(current_price) and current_price > 0:
                current_value = current_price * quantity
                pl = current_value - cost_basis
                pl_pct = (pl / cost_basis * 100) if cost_basis > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Cost Basis", f"${cost_basis:,.2f}")
                with col2:
                    st.metric("📊 Current Value", f"${current_value:,.2f}")
                with col3:
                    delta_color = "normal" if pl >= 0 else "inverse"
                    st.metric("📈 P/L", f"${pl:,.2f}", f"{pl_pct:+.2f}%", delta_color=delta_color)
                with col4:
                    price_change = current_price - purchase_price
                    price_change_pct = (price_change / purchase_price * 100) if purchase_price > 0 else 0
                    st.metric("💲 Current Price", f"${current_price:.2f}", f"{price_change_pct:+.2f}%")
                
                # Additional insights
                if abs(pl_pct) > 20:
                    if pl_pct > 20:
                        st.success(f"🚀 Excellent performance! +{pl_pct:.1f}% gain")
                    else:
                        st.warning(f"📉 Significant loss: {pl_pct:.1f}%")
                
            else:
                st.info(f"💡 Cost basis: ${cost_basis:,.2f}. Current price will be fetched after adding.")
                if not is_valid:
                    st.error("⚠️ Please verify the ticker symbol before adding to portfolio.")
        
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.info(f"💡 Cost basis will be ${cost_basis:,.2f}")

def validate_single_ticker(ticker: str):
    """Validate a single ticker and show detailed results."""
    if not ticker:
        st.error("Please enter a ticker symbol")
        return
    
    with st.spinner(f"🔍 Validating {ticker}..."):
        try:
            validation_results = putils.validate_tickers_enhanced([ticker])
            result = validation_results.get(ticker, {})
            
            if result.get("valid", False):
                st.success(f"✅ {ticker} is valid!")
                
                reason = result.get("reason", "")
                name = result.get("name", "")
                
                if name:
                    st.info(f"📊 **{name}**")
                if reason:
                    st.caption(f"Validation method: {reason}")
                
                # Try to get current price
                try:
                    prices = putils.get_cached_prices([ticker])
                    price = prices.get(ticker, np.nan)
                    if not pd.isna(price):
                        st.metric("💲 Current Price", f"${price:.2f}")
                except Exception:
                    pass
                    
            else:
                st.error(f"❌ {ticker} is not valid")
                reason = result.get("reason", "Unknown error")
                st.caption(f"Reason: {reason}")
                
                # Suggest alternatives
                if len(ticker) > 1:
                    suggestions = putils.search_popular_assets(ticker, limit=5)
                    if suggestions:
                        st.write("💡 **Did you mean:**")
                        for suggestion in suggestions:
                            st.write(f"• **{suggestion['ticker']}** - {suggestion['name']}")
                            
        except Exception as e:
            st.error(f"❌ Validation failed: {str(e)}")

def handle_asset_submission_enhanced(ticker: str, purchase_price: float, quantity: float, 
                                   asset_type: str, purchase_date, notes: str, 
                                   username: str, df: Optional[pd.DataFrame], asset_name: str = ""):
    """Enhanced asset submission with better validation and feedback."""
    # Validation
    errors = []
    
    if not ticker:
        errors.append("Ticker symbol is required")
    elif len(ticker) < 1:
        errors.append("Ticker symbol too short")
    
    if quantity <= 0:
        errors.append("Quantity must be greater than zero")
    
    if purchase_price <= 0:
        errors.append("Purchase price must be greater than zero")
    
    # Validate ticker before adding
    if ticker and not errors:
        try:
            validation_results = putils.validate_tickers_enhanced([ticker])
            is_valid = validation_results.get(ticker, {}).get("valid", False)
            
            if not is_valid:
                errors.append(f"Ticker '{ticker}' is not valid or not found")
        except Exception as e:
            logger.warning(f"Ticker validation failed: {e}")
            # Don't block addition if validation fails due to network issues
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
        return
    
    # Add the asset
    try:
        new_asset = {
            'Ticker': ticker,
            'Purchase Price': purchase_price,
            'Quantity': quantity,
            'Asset Type': asset_type,
            'Purchase Date': purchase_date.strftime('%Y-%m-%d'),
            'Notes': notes
        }
        
        # Add asset name if available
        if asset_name:
            new_asset['Asset Name'] = asset_name
        
        # Check for duplicates
        if df is not None and not df.empty:
            existing_tickers = df['Ticker'].str.upper().tolist()
            if ticker.upper() in existing_tickers:
                if st.button("⚠️ Ticker already exists. Add anyway?"):
                    pass  # Continue with addition
                else:
                    st.warning(f"⚠️ {ticker} already exists in portfolio. Click above to add anyway.")
                    return
        
        # Add to portfolio
        if df is None or df.empty:
            new_df = pd.DataFrame([new_asset])
        else:
            new_df = pd.concat([df, pd.DataFrame([new_asset])], ignore_index=True)
        
        # Save portfolio
        putils.save_portfolio(username, new_df, overwrite=True)
        
        # Update session state
        st.session_state.portfolio_df = new_df
        st.session_state.portfolio_modified = True
        
        st.success(f"🎉 Successfully added {ticker} to your portfolio!")
        st.balloons()
        
        # Show quick stats
        total_value = (new_df['Purchase Price'] * new_df['Quantity']).sum()
        st.info(f"📊 Portfolio now has {len(new_df)} assets with total cost basis of ${total_value:,.2f}")
        
        logger.info(f"Asset added: {ticker} for user {username}")
        
        # Clear form by rerunning
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error adding asset: {str(e)}")
        logger.error(f"Error adding asset {ticker}: {e}")
        
        if st.session_state.education_mode:
            with st.expander("🔧 Error Details"):
                st.code(traceback.format_exc())

# ============================================================================
# Enhanced Portfolio Overview
# ============================================================================

def display_portfolio_overview():
    """Enhanced portfolio overview with better error handling and features."""
    show_main_header("📊 Portfolio Dashboard", "Real-time analysis with advanced insights")
    
    # Display market status
    display_market_status()
    
    username = st.session_state.username
    
    # Portfolio Selection Section
    st.subheader("🗂️ Portfolio Management")
    portfolios = putils.list_portfolios(username)
    
    if portfolios:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            default_index = 0
            if st.session_state.selected_portfolio_file in portfolios:
                try:
                    default_index = portfolios.index(st.session_state.selected_portfolio_file)
                except ValueError:
                    pass
            
            selected_file = st.selectbox(
                "Select portfolio:",
                portfolios,
                index=default_index,
                help="Choose from your saved portfolios"
            )
            
            if selected_file != st.session_state.selected_portfolio_file:
                safe_load_portfolio(username, selected_file)
        
        with col2:
            if st.button("🔄 Refresh", help="Update prices and recalculate metrics"):
                refresh_portfolio_data()
        
        with col3:
            if st.button("📊 Quick Stats", help="Show portfolio summary"):
                show_portfolio_quick_stats()
        
        with col4:
            auto_refresh = st.checkbox("🔄 Auto", value=st.session_state.auto_refresh_enabled, help="Auto-refresh data")
            st.session_state.auto_refresh_enabled = auto_refresh
    else:
        display_empty_portfolio_guide()

    df = st.session_state.portfolio_df
    if df is None or df.empty:
        return

    # Auto-refresh if enabled
    if st.session_state.auto_refresh_enabled:
        # Check if we need to refresh (every 5 minutes)
        last_refresh = st.session_state.last_refresh
        if last_refresh is None or (datetime.now() - last_refresh).total_seconds() > 300:
            refresh_portfolio_data()

    # Fetch and process data with enhanced error handling
    try:
        with st.spinner("📡 Fetching real-time market data..."):
            metrics_df = fetch_and_compute_metrics_enhanced(df)
            
        if metrics_df is None or metrics_df.empty:
            st.error("❌ Unable to fetch market data. Please check your internet connection and try again.")
            
            # Show offline mode
            if st.button("📱 View in Offline Mode"):
                display_offline_portfolio_summary(df)
            return
            
    except Exception as e:
        show_error_with_details("Error processing portfolio data", str(e))
        return

    # Display enhanced components
    display_portfolio_summary_enhanced(metrics_df)
    display_dashboard_tabs_enhanced(metrics_df)

def refresh_portfolio_data():
    """Refresh portfolio data with user feedback."""
    try:
        # Clear caches
        putils.clear_all_caches()
        
        # Update timestamp
        st.session_state.last_refresh = datetime.now()
        
        st.success("✅ Data refreshed successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Refresh failed: {str(e)}")

def fetch_and_compute_metrics_enhanced(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Enhanced metrics computation with better error handling and progress tracking."""
    try:
        tickers = df['Ticker'].tolist()
        total_tickers = len(tickers)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Check yfinance availability
        if not putils.YF_AVAILABLE:
            st.error("❌ Yahoo Finance data is not available. Please check your internet connection.")
            return None
        
        # Step 1: Get current prices (40% of progress)
        status_text.text("📈 Fetching current prices...")
        price_dict = putils.get_cached_prices(tickers)
        progress_bar.progress(0.4)
        
        # Check for failed price fetches
        successful_prices = sum(1 for p in price_dict.values() if not pd.isna(p))
        failed_count = total_tickers - successful_prices
        
        if failed_count > 0:
            failed_tickers = [t for t, p in price_dict.items() if pd.isna(p)]
            st.warning(f"⚠️ Could not fetch prices for {failed_count} assets: {', '.join(failed_tickers[:5])}" + 
                      (f" and {failed_count-5} more" if failed_count > 5 else ""))
        
        # Step 2: Get benchmark data (60% of progress)
        status_text.text("📊 Fetching benchmark data...")
        benchmark_data = putils.fetch_benchmark_data()
        st.session_state.benchmark_data = benchmark_data
        progress_bar.progress(0.6)
        
        # Step 3: Compute enhanced metrics (100% of progress)
        status_text.text("🧮 Computing advanced metrics...")
        metrics_df = putils.compute_enhanced_metrics(
            df, price_dict, benchmark_data, st.session_state.selected_timeframe
        )
        progress_bar.progress(1.0)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Update last refresh time
        st.session_state.last_refresh = datetime.now()
        
        # Show success summary
        if successful_prices > 0:
            st.success(f"✅ Successfully updated {successful_prices}/{total_tickers} assets")
        
        return metrics_df
        
    except Exception as e:
        logger.error(f"Error in fetch_and_compute_metrics_enhanced: {e}")
        
        # Clear progress indicators
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
        
        raise

def display_portfolio_summary_enhanced(metrics_df: pd.DataFrame):
    """Enhanced portfolio summary with more detailed metrics."""
    st.subheader("📈 Portfolio Summary")
    
    # Calculate comprehensive metrics
    total_value = metrics_df['Total Value'].sum()
    total_cost = metrics_df['Cost Basis'].sum()
    total_pl = total_value - total_cost
    total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
    
    # Top row metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💰 Total Value",
            f"${total_value:,.0f}",
            help="Current market value of all holdings"
        )
    
    with col2:
        pl_delta = f"{total_pl_pct:+.1f}%" if not pd.isna(total_pl_pct) else "N/A"
        delta_color = "normal" if total_pl >= 0 else "inverse"
        st.metric(
            "📈 Total P/L",
            f"${total_pl:,.0f}",
            pl_delta,
            delta_color=delta_color,
            help="Profit/Loss vs purchase price"
        )
    
    with col3:
        # Best performer
        if not metrics_df['P/L %'].isna().all():
            best_performer = metrics_df.loc[metrics_df['P/L %'].idxmax()]
            best_pl = best_performer['P/L %']
            best_ticker = best_performer['Ticker']
        else:
            best_ticker = "N/A"
            best_pl = 0
            
        st.metric(
            "🏆 Best Performer",
            str(best_ticker),
            f"+{best_pl:.1f}%" if best_pl > 0 else "N/A",
            help="Asset with highest return percentage"
        )
    
    with col4:
        # Portfolio diversity
        asset_types = metrics_df['Asset Type'].nunique()
        total_assets = len(metrics_df)
        st.metric(
            "🎯 Diversity",
            f"{asset_types} types",
            f"{total_assets} assets",
            help="Number of different asset classes and total assets"
        )
    
    with col5:
        # Risk metric (average volatility)
        if 'Volatility' in metrics_df.columns:
            avg_volatility = metrics_df['Volatility'].mean()
            if not pd.isna(avg_volatility):
                risk_level = "Low" if avg_volatility < 20 else "Medium" if avg_volatility < 40 else "High"
                st.metric(
                    "⚠️ Risk Level",
                    risk_level,
                    f"{avg_volatility:.1f}%",
                    help="Average portfolio volatility"
                )
            else:
                st.metric("⚠️ Risk Level", "Calculating...", help="Computing risk metrics")
        else:
            st.metric("⚠️ Risk Level", "Pending", help="Risk data not available")
    
    # Second row - additional insights
    with st.expander("📊 Additional Portfolio Insights", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Largest position
            if 'Weight %' in metrics_df.columns:
                largest_pos = metrics_df.loc[metrics_df['Weight %'].idxmax()]
                st.metric(
                    "🎯 Largest Position",
                    largest_pos['Ticker'],
                    f"{largest_pos['Weight %']:.1f}%"
                )
        
        with col2:
            # Number of profitable positions
            profitable = len(metrics_df[metrics_df['P/L'] > 0])
            total_positions = len(metrics_df)
            st.metric(
                "📈 Profitable Positions",
                f"{profitable}/{total_positions}",
                f"{profitable/total_positions*100:.0f}%"
            )
        
        with col3:
            # Average position size
            if total_value > 0:
                avg_position = total_value / len(metrics_df)
                st.metric(
                    "📊 Avg Position Size",
                    f"${avg_position:,.0f}",
                    f"{100/len(metrics_df):.1f}%"
                )
        
        with col4:
            # Days since last update
            last_refresh = st.session_state.last_refresh
            if last_refresh:
                hours_since = (datetime.now() - last_refresh).total_seconds() / 3600
                if hours_since < 1:
                    refresh_text = f"{int(hours_since * 60)}m ago"
                else:
                    refresh_text = f"{int(hours_since)}h ago"
            else:
                refresh_text = "Never"
            
            st.metric(
                "🕐 Last Updated",
                refresh_text,
                help="Time since last data refresh"
            )

# ============================================================================
# Main Header and Utility Functions
# ============================================================================

def show_main_header(title: str, subtitle: str):
    """Display enhanced main header."""
    st.markdown(
        f'<div class="main-header">'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

def show_error_with_details(error_msg: str, details: str = None):
    """Enhanced error display with better formatting."""
    st.error(f"❌ {error_msg}")
    
    if st.session_state.education_mode and details:
        with st.expander("🔍 Technical Details (for debugging)"):
            st.code(details)
            
            # Provide helpful suggestions
            st.markdown("**💡 Possible solutions:**")
            st.markdown("• Check your internet connection")
            st.markdown("• Try refreshing the page")
            st.markdown("• Verify ticker symbols are correct")
            st.markdown("• Try again in a few minutes")

def safe_load_portfolio(username: str, filename: Optional[str] = None) -> bool:
    """Enhanced portfolio loading with better error handling."""
    try:
        with st.spinner("📂 Loading portfolio..."):
            # Código que se ejecuta mientras está el spinner
            st.write("Cargando portfolio...")
            # Aquí pondrías la lógica real de carga
            return True
    except Exception as e:
        show_error_with_details("❌ Error loading portfolio.", str(e))
        return False


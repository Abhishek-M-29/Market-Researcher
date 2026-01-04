"""
Market Research Engine - Streamlit UI

An interactive dashboard for running market research and exploring results.

Run with:
    streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (override=True to pick up changes)
load_dotenv(override=True)

# Page config
st.set_page_config(
    page_title="Market Research Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #00D26A;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'research_state' not in st.session_state:
        st.session_state.research_state = None
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = None
    if 'agent_logs' not in st.session_state:
        st.session_state.agent_logs = []
    if 'idea_input' not in st.session_state:
        st.session_state.idea_input = ""
    if 'region_input' not in st.session_state:
        st.session_state.region_input = "India"


def render_sidebar():
    """Render the sidebar with inputs and controls."""
    with st.sidebar:
        st.title("🔍 Market Research Engine")
        st.markdown("---")
        
        # Input fields
        idea = st.text_area(
            "💡 Your Startup Idea",
            placeholder="e.g., AI-powered expense tracker for Indian freelancers",
            height=100,
            key="idea_text_area"
        )
        
        region = st.selectbox(
            "🌍 Target Region",
            ["India", "Southeast Asia", "Global"],
            index=0,
            key="region_select"
        )
        
        # API Key check - need all 3 keys
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        google_key = os.getenv("GOOGLE_API_KEY", "")
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        api_keys_valid = (
            perplexity_key and perplexity_key != "your_perplexity_api_key_here" and
            google_key and google_key != "your_google_api_key_here" and
            tavily_key and tavily_key != "your_tavily_api_key_here"
        )
        run_disabled = not (idea and api_keys_valid)
        
        # ======== PROMINENT ENTER BUTTON ========
        st.markdown("---")
        run_clicked = st.button(
            "🚀 ENTER - Run Research", 
            disabled=run_disabled, 
            use_container_width=True,
            type="primary"
        )
        
        if run_disabled:
            if not idea:
                st.caption("⚠️ Enter an idea above to start")
            elif not api_keys_valid:
                st.caption("⚠️ Configure API keys first")
        
        st.markdown("---")
        
        # API Key status (collapsed by default)
        with st.expander("🔑 API Keys", expanded=False):
            st.caption("**Research LLM (Perplexity)**")
            if perplexity_key and perplexity_key != "your_perplexity_api_key_here":
                st.success("✅ Perplexity API Key")
            else:
                st.error("❌ Perplexity API Key missing")
            
            st.caption("**Analysis LLM (Gemini)**")
            if google_key and google_key != "your_google_api_key_here":
                st.success("✅ Google API Key")
            else:
                st.error("❌ Google API Key missing")
            
            st.caption("**Web Search (Tavily)**")
            if tavily_key and tavily_key != "your_tavily_api_key_here":
                st.success("✅ Tavily API Key")
            else:
                st.error("❌ Tavily API Key missing")
        
        if run_clicked:
            return idea, region, True
        
        return idea, region, False


def render_agent_progress():
    """Render the agent progress tracker."""
    agents = [
        ("🔍", "Strategist", "Searching for pain points"),
        ("✓", "Critic", "Verifying with statistics"),
        ("🕵️", "Infiltrator", "Analyzing competitors"),
        ("👥", "Anthropologist", "Creating personas"),
        ("📊", "Analyzer", "Building competitor matrix"),
        ("💡", "Innovator", "Proposing features"),
        ("💰", "Auditor", "Validating financials"),
        ("📄", "PDF Compiler", "Generating report"),
    ]
    
    current = st.session_state.current_agent
    
    cols = st.columns(len(agents))
    for i, (icon, name, desc) in enumerate(agents):
        with cols[i]:
            if current and name.lower() == current.lower().replace("_", ""):
                st.markdown(f"**{icon} {name}**")
                st.caption(f"⏳ {desc}...")
            elif name.lower() in [log.lower() for log in st.session_state.agent_logs]:
                st.markdown(f"✅ {name}")
                st.caption("Complete")
            else:
                st.markdown(f"⬜ {name}")
                st.caption(desc)


def render_results(state: dict):
    """Render the research results."""
    if not state:
        return
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "😤 Pain Points",
        "🏢 Competitors",
        "👥 Personas",
        "💡 Features",
        "💰 Financials"
    ])
    
    with tab1:
        render_overview(state)
    
    with tab2:
        render_pain_points(state)
    
    with tab3:
        render_competitors(state)
    
    with tab4:
        render_personas(state)
    
    with tab5:
        render_features(state)
    
    with tab6:
        render_financials(state)


def render_overview(state: dict):
    """Render the overview tab."""
    st.header("Research Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Verified Pains",
            len(state.get('verified_pains', []))
        )
    
    with col2:
        st.metric(
            "Competitors",
            len(state.get('competitor_table', []))
        )
    
    with col3:
        st.metric(
            "Personas",
            len(state.get('personas', []))
        )
    
    with col4:
        st.metric(
            "Features",
            len(state.get('feature_list', []))
        )
    
    st.markdown("---")
    
    # Financial viability
    revenue_model = state.get('revenue_model', {})
    ltv_cac = revenue_model.get('ltv_cac_ratio', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Financial Viability")
        if state.get('is_financially_viable'):
            st.success(f"✅ Viable (LTV/CAC: {ltv_cac:.2f})")
        else:
            st.error(f"❌ Not Viable (LTV/CAC: {ltv_cac:.2f})")
            st.caption("LTV/CAC ratio should be > 3.0")
    
    with col2:
        st.subheader("Positioning")
        st.info(state.get('recommended_positioning', 'No positioning recommendation yet.'))
    
    # Report download
    if state.get('report_markdown'):
        st.markdown("---")
        st.subheader("📥 Download Report")
        st.download_button(
            label="Download Markdown Report",
            data=state.get('report_markdown', ''),
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )


def render_pain_points(state: dict):
    """Render the pain points tab."""
    st.header("Verified Pain Points")
    
    pains = state.get('verified_pains', [])
    
    if not pains:
        st.info("No verified pain points yet.")
        return
    
    for i, pain in enumerate(pains, 1):
        with st.expander(f"Pain #{i}: {pain.get('pain', 'Unknown')[:60]}..."):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Pain:** {pain.get('pain', 'N/A')}")
                st.markdown(f"**Statistic:** {pain.get('stat', 'N/A')}")
                st.markdown(f"**Source:** {pain.get('source', 'N/A')}")
            
            with col2:
                st.metric("Year", pain.get('year', 'N/A'))
                sentiment = pain.get('sentiment_score', 0)
                st.metric("Sentiment", f"{sentiment:.2f}", 
                         delta="Negative" if sentiment < 0 else "Positive",
                         delta_color="normal" if sentiment < 0 else "inverse")


def render_competitors(state: dict):
    """Render the competitors tab."""
    st.header("Competitive Landscape")
    
    competitors = state.get('competitor_table', [])
    
    if not competitors:
        st.info("No competitor data yet.")
        return
    
    for comp in competitors:
        with st.expander(f"🏢 {comp.get('name', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**URL:** {comp.get('url', 'N/A')}")
                st.markdown(f"**Best At:** {comp.get('best_at', 'N/A')}")
                st.markdown(f"**Lag:** {comp.get('lag', 'N/A')}")
            
            with col2:
                st.markdown(f"**Lack:** {comp.get('lack', 'N/A')}")
                st.markdown(f"**Gap (Our Opportunity):** {comp.get('gap', 'N/A')}")
            
            # Dark patterns
            dark_patterns = comp.get('dark_patterns_detected', []) or comp.get('scraped_dark_patterns', {}).get('dark_patterns_found', [])
            if dark_patterns:
                st.warning(f"⚠️ Dark Patterns Detected: {', '.join(dark_patterns)}")


def render_personas(state: dict):
    """Render the personas tab."""
    st.header("Target Personas")
    
    personas = state.get('personas', [])
    
    if not personas:
        st.info("No personas created yet.")
        return
    
    # Group by segment
    segments = {"India 1": [], "India 2": [], "India 3": []}
    for persona in personas:
        segment = persona.get('segment', 'India 1')
        if segment in segments:
            segments[segment].append(persona)
    
    for segment, segment_personas in segments.items():
        if segment_personas:
            st.subheader(f"🇮🇳 {segment}")
            
            cols = st.columns(len(segment_personas))
            for i, persona in enumerate(segment_personas):
                with cols[i]:
                    st.markdown(f"**{persona.get('name', 'Unknown')}**")
                    st.caption(f"{persona.get('age_range', 'N/A')} | {persona.get('income_bracket', 'N/A')}")
                    
                    trust_score = persona.get('trust_deficit_score', 5)
                    st.progress(trust_score / 10, text=f"Trust Deficit: {trust_score}/10")
                    
                    st.markdown(f"🗣️ {persona.get('language_preference', 'N/A')}")
                    st.markdown(f"💻 Tech: {persona.get('tech_comfort', 'N/A')}")
                    
                    with st.expander("Full Profile"):
                        st.write(persona.get('description', 'No description'))


def render_features(state: dict):
    """Render the features tab."""
    st.header("Proposed Features (by RICE Score)")
    
    features = state.get('feature_list', [])
    
    if not features:
        st.info("No features proposed yet.")
        return
    
    # Summary metrics
    categories = state.get('feature_categories', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚀 Quick Wins", categories.get('quick_wins', 0))
    with col2:
        st.metric("🎯 Big Bets", categories.get('big_bets', 0))
    with col3:
        st.metric("🤔 Maybes", categories.get('maybes', 0))
    with col4:
        st.metric("❄️ Ice Box", categories.get('ice_box', 0))
    
    st.markdown("---")
    
    # Feature table
    for i, feature in enumerate(features[:15], 1):
        with st.expander(f"#{i} {feature.get('name', 'Unknown')} (RICE: {feature.get('rice_score', 0):,.0f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {feature.get('description', 'N/A')}")
                st.markdown(f"**Delta-4 Claim:** {feature.get('delta_4_claim', 'N/A')}")
                st.markdown(f"**Linked Pain:** {feature.get('linked_pain', 'N/A')}")
                st.markdown(f"**Target Persona:** {feature.get('persona_target', 'N/A')}")
            
            with col2:
                st.metric("Reach", f"{feature.get('reach', 0):,}")
                st.metric("Impact", feature.get('impact', 0))
                st.metric("Confidence", f"{feature.get('confidence', 0)*100:.0f}%")
                st.metric("Effort", f"{feature.get('effort', 0)} weeks")


def render_financials(state: dict):
    """Render the financials tab."""
    st.header("Financial Projections")
    
    revenue_model = state.get('revenue_model', {})
    business_model = state.get('business_model', {})
    
    if not revenue_model:
        st.info("No financial data yet.")
        return
    
    # Unit Economics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Unit Economics")
        st.metric("CAC", f"₹{revenue_model.get('cac', 0):,.0f}")
        st.metric("ARPU", f"₹{revenue_model.get('arpu', 0):,.0f}/mo")
        st.metric("Gross Margin", f"{revenue_model.get('gross_margin', 0)*100:.0f}%")
    
    with col2:
        st.subheader("Lifetime Metrics")
        st.metric("LTV", f"₹{revenue_model.get('ltv', 0):,.0f}")
        st.metric("LTV/CAC", f"{revenue_model.get('ltv_cac_ratio', 0):.2f}")
        st.metric("Payback", f"{revenue_model.get('payback_months', 0):.1f} months")
    
    with col3:
        st.subheader("Pricing Tiers")
        pricing = revenue_model.get('pricing_tiers', {})
        for tier, price in pricing.items():
            st.markdown(f"**{tier}:** ₹{price:,.0f}/mo")
    
    st.markdown("---")
    
    # Business Model
    st.subheader("Business Model Canvas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Key Partners**")
        for partner in business_model.get('key_partners', []):
            st.markdown(f"• {partner}")
    
    with col2:
        st.markdown("**Revenue Streams**")
        for stream in business_model.get('revenue_streams', []):
            st.markdown(f"• {stream}")
    
    with col3:
        st.markdown("**Cost Structure**")
        for cost in business_model.get('cost_structure', []):
            st.markdown(f"• {cost}")


def run_research_pipeline(idea: str, region: str):
    """Run the research pipeline with progress updates and live logging."""
    from src.graph import get_runnable_graph, create_initial_state
    import time
    
    st.session_state.is_running = True
    st.session_state.agent_logs = []
    
    # Agent information for display
    agent_info = {
        "strategist": ("🔍", "Strategist", "Searching for pain points..."),
        "critic": ("✓", "Critic", "Verifying with statistics..."),
        "infiltrator": ("🕵️", "Infiltrator", "Analyzing competitors..."),
        "anthropologist": ("👥", "Anthropologist", "Creating personas..."),
        "analyzer": ("📊", "Analyzer", "Building competitor matrix..."),
        "innovator": ("💡", "Innovator", "Proposing features..."),
        "auditor": ("💰", "Auditor", "Validating financials..."),
        "pdf_compiler": ("📄", "PDF Compiler", "Generating report..."),
    }
    
    # Create initial state
    initial_state = create_initial_state(idea, region)
    
    # Get the compiled graph
    graph = get_runnable_graph()
    
    # Create UI containers
    st.markdown("## 🔄 Research in Progress")
    st.markdown(f"**Idea:** {idea}")
    st.markdown(f"**Region:** {region}")
    st.markdown("---")
    
    # Progress bar
    progress_bar = st.progress(0, text="Starting research pipeline...")
    
    # Log container
    log_container = st.container()
    
    # Status container for current agent
    status_container = st.empty()
    
    # Expandable log section
    with st.expander("📋 Live Execution Log", expanded=True):
        log_placeholder = st.empty()
    
    logs = []
    completed_agents = []
    total_agents = 8
    
    def add_log(message: str, level: str = "info"):
        """Add a log entry with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        if level == "success":
            logs.append(f"✅ [{timestamp}] {message}")
        elif level == "error":
            logs.append(f"❌ [{timestamp}] {message}")
        elif level == "warning":
            logs.append(f"⚠️ [{timestamp}] {message}")
        else:
            logs.append(f"ℹ️ [{timestamp}] {message}")
        
        # Update log display
        log_placeholder.code("\n".join(logs), language=None)
    
    add_log(f"Starting market research for: {idea}")
    add_log(f"Target region: {region}")
    add_log("Initializing LangGraph pipeline...")
    
    try:
        # Stream through the graph
        current_step = 0
        
        for event in graph.stream(initial_state):
            for node_name, state_update in event.items():
                current_step += 1
                
                # Get agent info
                icon, name, desc = agent_info.get(node_name, ("🔄", node_name, "Processing..."))
                
                # Update status
                status_container.info(f"{icon} **Currently running:** {name} - {desc}")
                
                # Update progress
                progress = min(current_step / total_agents, 1.0)
                progress_bar.progress(progress, text=f"Step {current_step}/{total_agents}: {name}")
                
                # Log completion
                add_log(f"Completed: {name}", "success")
                
                # Log specific details based on agent
                if node_name == "strategist":
                    pains_found = len(state_update.get('raw_pains', []))
                    add_log(f"  → Found {pains_found} potential pain points")
                
                elif node_name == "critic":
                    verified = len(state_update.get('verified_pains', []))
                    is_verified = state_update.get('is_verified', False)
                    add_log(f"  → Verified {verified} pain points")
                    if not is_verified:
                        add_log(f"  → Verification loop triggered", "warning")
                
                elif node_name == "infiltrator":
                    competitors = len(state_update.get('competitor_table', []))
                    add_log(f"  → Analyzed {competitors} competitors")
                
                elif node_name == "anthropologist":
                    personas = len(state_update.get('personas', []))
                    add_log(f"  → Created {personas} personas")
                
                elif node_name == "analyzer":
                    gaps = len(state_update.get('market_gaps', []))
                    add_log(f"  → Identified {gaps} market gaps")
                
                elif node_name == "innovator":
                    features = len(state_update.get('feature_list', []))
                    add_log(f"  → Proposed {features} features")
                
                elif node_name == "auditor":
                    is_viable = state_update.get('is_financially_viable', False)
                    revenue = state_update.get('revenue_model', {})
                    ratio = revenue.get('ltv_cac_ratio', 0)
                    add_log(f"  → LTV/CAC Ratio: {ratio:.2f}")
                    if is_viable:
                        add_log(f"  → Financially viable ✓", "success")
                    else:
                        add_log(f"  → Not viable - may loop to Innovator", "warning")
                
                elif node_name == "pdf_compiler":
                    report_path = state_update.get('final_report_path', '')
                    add_log(f"  → Report generated")
                
                completed_agents.append(node_name)
        
        # Get final state by running invoke
        add_log("Finalizing research results...")
        final_state = graph.invoke(initial_state)
        
        # Complete
        progress_bar.progress(1.0, text="✅ Research Complete!")
        status_container.success("🎉 **Research pipeline completed successfully!**")
        add_log("=" * 50)
        add_log("RESEARCH COMPLETE", "success")
        add_log(f"Total pain points verified: {len(final_state.get('verified_pains', []))}")
        add_log(f"Total competitors analyzed: {len(final_state.get('competitor_table', []))}")
        add_log(f"Total personas created: {len(final_state.get('personas', []))}")
        add_log(f"Total features proposed: {len(final_state.get('feature_list', []))}")
        
        st.session_state.research_state = final_state
        st.session_state.is_running = False
        st.session_state.agent_logs = logs
        
        return final_state
        
    except Exception as e:
        add_log(f"Error: {str(e)}", "error")
        status_container.error(f"❌ Error during research: {str(e)}")
        st.session_state.is_running = False
        import traceback
        add_log(traceback.format_exc(), "error")
        return None


def main():
    """Main application entry point."""
    init_session_state()
    
    # Sidebar
    idea, region, should_run = render_sidebar()
    
    # Main content
    st.title("🔍 Multi-Agent Market Research Engine")
    st.markdown("*Powered by LangGraph + Gemini + Deterministic Python Logic*")
    
    st.markdown("---")
    
    # Run research if button clicked
    if should_run and idea:
        # Clear previous results
        st.session_state.research_state = None
        result = run_research_pipeline(idea, region)
        if result:
            st.success("✅ Research complete! Scroll down to see results.")
            st.balloons()
            # Rerun to show results properly
            st.rerun()
    
    # Show previous logs if available
    if st.session_state.agent_logs and not st.session_state.is_running:
        with st.expander("📋 Previous Execution Log", expanded=False):
            st.code("\n".join(st.session_state.agent_logs), language=None)
    
    # Show results if available
    if st.session_state.research_state:
        render_results(st.session_state.research_state)
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome! 👋
        
        This is a **hybrid AI + deterministic code** market research engine.
        
        ### What makes it special?
        
        | Component | AI | Real Code |
        |-----------|-----|-----------|
        | Pain Point Discovery | ✅ LLM | ✅ VADER Sentiment |
        | Source Verification | ✅ LLM | ✅ Domain Trust Scoring |
        | Competitor Analysis | ✅ LLM | ✅ BeautifulSoup Scraping |
        | Feature Prioritization | ✅ LLM | ✅ RICE Algorithm |
        | Financial Modeling | ✅ LLM | ✅ Pandas Calculations |
        
        ### Get Started
        
        1. Add your **Google API Key** and **Tavily API Key** to the `.env` file
        2. Enter your startup idea in the sidebar
        3. Click **▶️ ENTER - Run Research**
        4. Watch the live execution log
        5. Explore the results across the tabs
        
        ---
        
        *Built with ❤️ using LangGraph, Streamlit, and deterministic Python logic.*
        """)


if __name__ == "__main__":
    main()

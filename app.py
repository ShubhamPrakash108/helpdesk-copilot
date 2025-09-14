import streamlit as st
import time
from helper_functions.topic_tags import topic_tags_of_the_concern
from helper_functions.emoji import emotion_to_emoji
import os
import random
import pandas as pd
import plotly.express as px
from helper_functions.priority import priority_of_the_concern
import json

with open("./frontend/heading.txt", "r", encoding="utf-8") as f:
    heading = f.read()

st.set_page_config(
    page_title="Customer Assistance Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(heading, unsafe_allow_html=True)


with open("./frontend/button.txt", "r", encoding="utf-8") as f:
    button_css = f.read()

st.markdown(button_css, unsafe_allow_html=True)

if 'button_pressed' not in st.session_state:
    st.session_state.button_pressed = None

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📊 Classification Dashboard (click to view) ", use_container_width=True):
        st.session_state.button_pressed = "dashboard"

with col2:
    if st.button("🤖 Interactive AI Bot (click to view)", use_container_width=True):
        st.session_state.button_pressed = "bot"

emotion_colors = {
    "excitement": "#FF4500","pride": "#800080", "joy": "#BFFF00","approval": "#4CAF50","admiration": "#F4C542",
    "desire": "#FF69B4","love": "#E91E63","optimism": "#A8E6CF","amusement": "#FFA500","caring": "#5DADE2",
    "realization": "#3498DB","gratitude": "#5CFF3B","curiosity": "#9B59B6","relief": "#82E0AA","surprise": "#FF7F50","neutral": "#BDC3C7",
    "nervousness": "#F39C12","confusion": "#7F8C8D","remorse": "#8E44AD","anger": "#E74C3C","annoyance": "#E67E22",
    "grief": "#2C3E50","fear": "#4B0082","embarrassment": "#FAD7A0","disapproval": "#C0392B","disgust": "#556B2F",
    "disappointment": "#5D6D7E","sadness": "#3498DB"
}

emotion_colors_record = {
    "excitement": 0,"pride": 0,"joy": 0,"approval": 0,"admiration": 0,
    "desire": 0,"love": 0,"optimism": 0,"amusement": 0,"caring": 0,
    "realization": 0,"gratitude": 0,"curiosity": 0,"relief": 0,"surprise": 0,"neutral": 0,
    "nervousness": 0,"confusion": 0,"remorse": 0,"anger": 0,"annoyance": 0,
    "grief": 0,"fear": 0,"embarrassment": 0,"disapproval": 0,"disgust": 0,
    "disappointment": 0,"sadness": 0
}

df = pd.DataFrame(list(emotion_colors_record.items()), columns=['Emotion', 'Count'])

def draw_bar_chart(df):
    df["Color"] = df['Emotion'].map(emotion_colors)
    fig = px.bar(df,
                 x='Emotion', 
                 y='Count',
                 color='Emotion',
                 color_discrete_map=emotion_colors)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def draw_pie_chart(df):
    df["Color"] = df['Emotion'].map(emotion_colors)
    fig = px.pie(df, 
                 names='Emotion', 
                 values='Count',
                 color='Emotion',
                 color_discrete_map=emotion_colors,
                 hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

rag_topics = ['How-to', 'Product', 'Connector', 'Lineage', 'Connector', 'API/SDK', 'SSO', 'Glossary', 'Best practices', 'Sensitive data']

if st.session_state.button_pressed == "dashboard":

    st.markdown("### 📁 Upload Sample Tickets File")
    uploaded_file = st.file_uploader(
        "Choose a JSON file containing sample tickets", 
        type=['json'],
        help="Upload the sample_tickets file to begin classification"
    )

    customer_data = []

    if uploaded_file is not None:
        try: 
            customer_data = json.load(uploaded_file)
            st.success(f"✅ Successfully loaded {len(customer_data)} tickets from {uploaded_file.name}")
        except json.JSONDecodeError:
            st.error("❌ Error: Invalid JSON file. Please check your file format.")
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    else:
        
        st.info("👆 Please upload a sample tickets JSON file to start the classification dashboard.")
        
        try:
            with open("./json_files_data/data.json", "r", encoding="utf-8") as f:
                customer_data = json.load(f)
            st.warning("⚠️ Using default sample data. Upload your own file for custom analysis.")
        except FileNotFoundError:
            st.warning("⚠️ No default data available. Please upload a sample tickets file.")
            customer_data = []


    with open("./frontend/classification_dashboard.txt", "r", encoding="utf-8") as f:
        classification_dashboard = f.read()
    st.markdown(classification_dashboard, unsafe_allow_html=True)
    
    st.markdown('<div class="dashboard-header">📊 Classification Dashboard</div>', unsafe_allow_html=True)
        
    with st.container():
        
        from helper_functions.sentiment_analysis import sentiment_analysis
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            bar_chart_placeholder = st.empty()
        with chart_col2:
            pie_chart_placeholder = st.empty()
        
        emotion_colors_record = {key: 0 for key in emotion_colors_record}
        
        progress_bar = st.progress(0)
        for i, data in enumerate(customer_data):
            sentiment_analysis_result = sentiment_analysis(data['body'])
            emotion_colors_record[sentiment_analysis_result.lower()] += 1
            sentiment_analysis_result = sentiment_analysis_result.capitalize()
            progress_bar.progress((i + 1) / len(customer_data))
            updated_df = pd.DataFrame(list(emotion_colors_record.items()), columns=['Emotion', 'Count'])
            
            with bar_chart_placeholder.container():
                updated_df["Color"] = updated_df['Emotion'].map(emotion_colors)
                fig_bar = px.bar(updated_df,
                                x='Emotion', 
                                y='Count',
                                color='Emotion',
                                color_discrete_map=emotion_colors)
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with pie_chart_placeholder.container():
                updated_df["Color"] = updated_df['Emotion'].map(emotion_colors)
                fig_pie = px.pie(updated_df, 
                                names='Emotion', 
                                values='Count',
                                color='Emotion',
                                color_discrete_map=emotion_colors,
                                hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)

            emotion_color = emotion_colors.get(sentiment_analysis_result.lower(), "#BDC3C7")
            
            emotion_css = f"""
            <style>
            .emotion-{sentiment_analysis_result.lower()}-header {{
                background: linear-gradient(135deg, {emotion_color} 0%, {emotion_color}CC 100%);
                border-radius: 12px;
                padding: 18px;
                color: white;
                font-weight: bold;
                margin: 15px 0;
                box-shadow: 0 4px 15px {emotion_color}33;
                transition: all 0.3s ease;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-header:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px {emotion_color}44;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-box {{
                background: linear-gradient(145deg, {emotion_color}11, {emotion_color}22);
                border-left: 5px solid {emotion_color};
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 4px 12px {emotion_color}22;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-box:before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, {emotion_color}66, transparent);
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-box:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 20px {emotion_color}33;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-label {{
                font-weight: bold;
                color: {emotion_color};
                margin-bottom: 12px;
                font-size: 1.1rem;
                display: flex;
                align-items: center;
                gap: 8px;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-scrollbar::-webkit-scrollbar {{
                width: 6px;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-scrollbar::-webkit-scrollbar-track {{
                background: #f1f1f1;
                border-radius: 10px;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-scrollbar::-webkit-scrollbar-thumb {{
                background: {emotion_color};
                border-radius: 10px;
            }}
            
            .emotion-{sentiment_analysis_result.lower()}-scrollbar::-webkit-scrollbar-thumb:hover {{
                background: {emotion_color}DD;
            }}
            </style>
            """
            
            st.markdown(emotion_css, unsafe_allow_html=True)
            groq_api_key = os.environ.get("GROQ_API_KEY")
            with st.expander(f"### Customer ID: {data['id']} | Sentiment: {sentiment_analysis_result} | Emotion: {emotion_to_emoji(sentiment_analysis_result)} | Priority: {priority_of_the_concern(data['body'], 'groq', groq_api_key)}", expanded=False):
                groq_api_key = [os.environ.get("GROQ_API_KEY"), os.environ.get("GROQ_API_KEY_2")]
                groq_api_key = random.choice(groq_api_key)
                
                st.markdown(
                    f'''
                    <div class="emotion-{sentiment_analysis_result.lower()}-box">
                        <div class="emotion-{sentiment_analysis_result.lower()}-label">📋 Customer Concern Subject:</div>
                        <div>{data["subject"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f'''
                    <div class="emotion-{sentiment_analysis_result.lower()}-box emotion-{sentiment_analysis_result.lower()}-scrollbar" style="max-height: 200px; overflow-y: auto;">
                        <div class="emotion-{sentiment_analysis_result.lower()}-label">💬 Customer Body:</div>
                        <div>{data["body"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'''
                    <div class="emotion-{sentiment_analysis_result.lower()}-box">
                        <div class="emotion-{sentiment_analysis_result.lower()}-label">🏷️ Top Tags:</div>
                        <div>{topic_tags_of_the_concern(data["body"], "groq", groq_api_key)}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )


            # time.sleep(5)



elif st.session_state.button_pressed == "bot":
    with st.container():
        
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        
        .input-section {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }
        
        .send-button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .analysis-card {
            background: #ffffff;
            border: 1px solid #e0e6ed;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .ticket-info {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            color: #2c3e50;
        }
        
        .context-section {
            background: #f1f5f9;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .ai-response {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #f59e0b;
            margin: 15px 0;
        }
        
        .warning-box {
            background: #fef3cd;
            border: 1px solid #fbbf24;
            padding: 12px;
            border-radius: 8px;
            color: #92400e;
        }
        
        .error-box {
            background: #fef2f2;
            border: 1px solid #ef4444;
            padding: 12px;
            border-radius: 8px;
            color: #dc2626;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">🤖 Interactive AI Bot</div>', unsafe_allow_html=True)
        
        user_input = st.text_input("Enter your concern or Ticket number here...", key="user_input")
        st.markdown('</div>', unsafe_allow_html=True)
                
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            send_clicked = st.button("📤 Send", key="send_button", use_container_width=True)

        if send_clicked:
            if user_input.strip() == "":
                st.markdown('<div class="warning-box">⚠️ Please enter a valid concern or Ticket number.</div>', unsafe_allow_html=True)
            else:
                
                if "TICKET-" in user_input.upper():
                    st.markdown('<div class="ticket-info">🎫 Fetching details for ticket number from sql DB...</div>', unsafe_allow_html=True)
                    
                    from sql_db.query_from_db import fetch_data_from_db
                    
                    problem_id = user_input.upper().strip()
                    fetched_data = fetch_data_from_db(problem_id)
                    
                    if fetched_data:
                        with st.spinner("Processing..."):
                            
                            subject, body = fetched_data[0]
                            st.markdown(f'<div class="analysis-card"><h3>📋 Subject: {subject}</h3></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="analysis-card"><h3>📝 Body: {body}</h3></div>', unsafe_allow_html=True)
                            
                            from helper_functions.internal_analysis import internal_analysis
                            analysis_results = internal_analysis(body)
                            st.markdown(f'<div class="analysis-card"><strong>Sentiment:</strong> {analysis_results["sentiment"]} {analysis_results["emoji"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="analysis-card"><strong>Priority:</strong> {analysis_results["priority"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="analysis-card"><strong>Topics:</strong> {analysis_results["topics"]}</div>', unsafe_allow_html=True)

                            if any(topic in analysis_results["topics"] for topic in ['How-to', 'Product', 'Best practices', 'API/SDK', 'SSO']):
                            # if any(topic in rag_topics for topic in analysis_results["topics"]):
                                from helper_functions.query_from_db_llm import llm_generation, show_metadata

                                results, context, source_urls = show_metadata(body)
                                st.markdown("### 🗄️ Context from Pinecone Database:")
                                with st.expander("🔗 Source URLs", expanded=False):
                                    for i, url in enumerate(source_urls, start=1):
                                        st.markdown(f"- 🌐 [{url}]({url})")
                                st.markdown('<div class="context-section"><h3>🗄️ Context from Pinecone Database:</h3>', unsafe_allow_html=True)
                                with st.expander("🗄️ Context from Pinecone Database", expanded=False):
                                    st.markdown(f'{context}</div>', unsafe_allow_html=True)
                                
                                llm_generation_response = llm_generation(body, context, llm="gemini")
                                st.markdown('<div class="ai-response"><h3>🤖 AI Response:</h3>', unsafe_allow_html=True)
                                st.markdown(f'{llm_generation_response}</div>', unsafe_allow_html=True)
                            
                            else:
                                st.markdown('<div class="warning-box">⚠️ This ticket is unrelated to product usage or how-to questions. The concern has been referred to the support team for further assistance.</div>', unsafe_allow_html=True)

                    else:
                        st.markdown(f'<div class="error-box">❌ No data found for Ticket ID: {problem_id} in the database.</div>', unsafe_allow_html=True)
                
                else:
                    with st.spinner("Processing..."):
                        
                        from helper_functions.internal_analysis import internal_analysis
                        analysis_results = internal_analysis(user_input)
                        st.markdown(f'<div class="analysis-card"><strong>Sentiment:</strong> {analysis_results["sentiment"]} {analysis_results["emoji"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="analysis-card"><strong>Priority:</strong> {analysis_results["priority"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="analysis-card"><strong>Topics:</strong> {analysis_results["topics"]}</div>', unsafe_allow_html=True)
                        
                        if any(topic in analysis_results["topics"] for topic in ['How-to', 'Product', 'Best practices', 'API/SDK', 'SSO']):
                        # if any(topic in rag_topics for topic in analysis_results["topics"]):
                       
                            from helper_functions.query_from_db_llm import llm_generation, show_metadata

                            results, context, source_urls = show_metadata(user_input)
                            st.markdown("### 🗄️ Context from Pinecone Database:")
                            with st.expander("🔗 Source URLs", expanded=False):
                                for i, url in enumerate(source_urls, start=1):
                                    st.markdown(f"- 🌐 [{url}]({url})")
                            st.markdown('<div class="context-section"><h3>🗄️ Context from Pinecone Database:</h3>', unsafe_allow_html=True)
                            with st.expander("🗄️ Context from Pinecone Database", expanded=False):
                                st.markdown(f'{context}</div>', unsafe_allow_html=True)
                                
                            llm_generation_response = llm_generation(user_input, context, llm="gemini")
                            st.markdown('<div class="ai-response"><h3>🤖 AI Response:</h3>', unsafe_allow_html=True)
                            st.markdown(f'{llm_generation_response}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="warning-box">⚠️ This ticket is unrelated to product usage or how-to questions. The concern has been referred to the support team for further assistance.</div>', unsafe_allow_html=True)



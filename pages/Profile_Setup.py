import streamlit as st
from utils.database import get_db_connection
from datetime import datetime

st.title("🎓 Complete Your Profile")
st.subheader("Help us personalize your learning experience")

# Check if profile exists
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', 
               (st.session_state['user_id'],))
existing_profile = cursor.fetchone()
conn.close()

# Form
with st.form("profile_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        study_field = st.selectbox(
            "📚 Study Field",
            ["Computer Science", "Engineering", "Mathematics", 
             "Physics", "Chemistry", "Biology", "Commerce", 
             "Arts", "Other"],
            index=0 if not existing_profile else None
        )
        
        knowledge_level = st.selectbox(
            "📊 Knowledge Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=0 if not existing_profile else None
        )
        
        institution = st.text_input(
            "🏫 Institution/School",
            value=existing_profile['institution'] if existing_profile else ""
        )
    
    with col2:
        interest_areas = st.multiselect(
            "🎯 Interest Areas (Select multiple)",
            ["Programming", "Web Development", "Data Science", 
             "Machine Learning", "Mobile Development", "Mathematics",
             "Physics", "Chemistry", "Biology", "History", "Literature"],
            default=existing_profile['interest_areas'].split(',') if existing_profile else []
        )
        
        grade_year = st.selectbox(
            "🎓 Grade/Year",
            ["8th Grade", "9th Grade", "10th Grade", "11th Grade", "12th Grade",
             "1st Year College", "2nd Year College", "3rd Year College", 
             "4th Year College", "Graduate", "Professional"],
            index=0 if not existing_profile else None
        )
        
        learning_goals = st.text_area(
            "🎯 Learning Goals",
            placeholder="E.g., Prepare for JEE, Learn web development, Improve coding skills...",
            value=existing_profile['learning_goals'] if existing_profile else ""
        )
    
    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
    
    if submitted:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        interest_str = ','.join(interest_areas)
        
        if existing_profile:
            # Update existing profile
            cursor.execute('''
                UPDATE user_profiles 
                SET study_field=?, interest_areas=?, knowledge_level=?, 
                    institution=?, grade_year=?, learning_goals=?, updated_at=?
                WHERE user_id=?
            ''', (study_field, interest_str, knowledge_level, institution, 
                  grade_year, learning_goals, datetime.now(), st.session_state['user_id']))
        else:
            # Create new profile
            cursor.execute('''
                INSERT INTO user_profiles 
                (user_id, study_field, interest_areas, knowledge_level, 
                 institution, grade_year, learning_goals, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (st.session_state['user_id'], study_field, interest_str, 
                  knowledge_level, institution, grade_year, learning_goals, datetime.now()))
        
        conn.commit()
        conn.close()
        
        st.success("✅ Profile saved successfully!")
        st.balloons()
        
        # Redirect to home after 2 seconds
        import time
        time.sleep(2)
        st.switch_page("pages/Home.py")

# Show preview
if existing_profile:
    st.markdown("---")
    st.subheader("📋 Your Current Profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Study Field", existing_profile['study_field'])
    with col2:
        st.metric("Knowledge Level", existing_profile['knowledge_level'])
    with col3:
        st.metric("Grade/Year", existing_profile['grade_year'])

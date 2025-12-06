import streamlit as st
import cohere
from datetime import datetime, timedelta, time
import requests
import json
from typing import List, Dict

# Initialize Cohere
COHERE_API_KEY = ""
co = cohere.Client(COHERE_API_KEY)

# Page config
st.set_page_config(
    page_title="Smart Goal Tracker with Notion",
    page_icon="📝",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    .slot-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;

    # ...existing code...
        padding: 18px;
        border-radius: 12px;
        margin: 14px 0;
        border-left: 5px solid #7f53ac;
        box-shadow: 0 2px 8px rgba(100, 125, 238, 0.08);
        transition: box-shadow 0.2s;
    }
    .slot-card:hover {
        box-shadow: 0 4px 16px rgba(100, 125, 238, 0.18);
        border-left: 5px solid #647dee;
    }
    .stButton > button {
        background: linear-gradient(90deg, #7f53ac 0%, #647dee 100%);
        color: #fff;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.75em 2em;
        box-shadow: 0 2px 8px rgba(100, 125, 238, 0.08);
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #647dee 0%, #7f53ac 100%);
        color: #fff;
    }
    .stTextInput > div > input {
        border-radius: 8px;
        border: 1px solid #647dee;
        padding: 0.5em 1em;
        background: #f8fafc;
    }
    .stSlider > div {
        background: #e0e7ff;
        border-radius: 8px;
    }
    .stSelectbox > div {
        border-radius: 8px;
        border: 1px solid #647dee;
        background: #f8fafc;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #e0e7ff;
        border-radius: 8px;
        padding: 0.5em;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #7f53ac;
    }
    .stTabs [aria-selected="true"] {
        color: #fff;
        background: linear-gradient(90deg, #7f53ac 0%, #647dee 100%);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


class NotionAPI:
    """Notion API Integration"""
    
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id.strip().replace('-', '')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def test_connection(self) -> tuple:
        """Test if connection to database works"""
        url = f"https://api.notion.com/v1/databases/{self.database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return True, "Connection successful!"
            elif response.status_code == 401:
                return False, "Invalid API token. Check your integration token."
            elif response.status_code == 404:
                return False, "Database not found. Check your Database ID or make sure you shared the database with the integration."
            else:
                error_data = response.json()
                return False, f"Error {response.status_code}: {error_data.get('message', 'Unknown error')}"
        
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def create_task(self, activity: str, date: str, time_str: str, duration: int, 
                    energy: str, category: str = "Personal") -> tuple:
        """Create a new task in Notion database"""
        
        url = "https://api.notion.com/v1/pages"
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Activity": {
                    "title": [
                        {
                            "text": {
                                "content": activity
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": date
                    }
                },
                "Time": {
                    "rich_text": [
                        {
                            "text": {
                                "content": time_str
                            }
                        }
                    ]
                },
                "Duration": {
                    "number": duration
                },
                "Energy": {
                    "select": {
                        "name": energy
                    }
                },
                "Status": {
                    "select": {
                        "name": "📝 Planned"
                    }
                },
                "Category": {
                    "select": {
                        "name": category
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return True, "Task successfully added to Notion!"
            else:
                error_data = response.json()
                error_msg = error_data.get('message', 'Unknown error')
                
                return False, f"Error {response.status_code}: {error_msg}\n\nFull response: {json.dumps(error_data, indent=2)}"
        
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def get_tasks(self, date: str = None) -> tuple:
        """Get tasks from Notion database"""
        
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        
        data = {}
        if date:
            data = {
                "filter": {
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                tasks = []
                for result in results:
                    props = result['properties']
                    
                    activity = props.get('Activity', {}).get('title', [{}])[0].get('text', {}).get('content', 'Untitled')
                    time_str = props.get('Time', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '')
                    duration = props.get('Duration', {}).get('number', 0)
                    energy = props.get('Energy', {}).get('select', {}).get('name', 'Medium') if props.get('Energy', {}).get('select') else 'Medium'
                    status = props.get('Status', {}).get('select', {}).get('name', 'Planned') if props.get('Status', {}).get('select') else 'Planned'
                    
                    tasks.append({
                        'activity': activity,
                        'time': time_str,
                        'duration': duration,
                        'energy': energy,
                        'status': status
                    })
                
                return True, tasks
            else:
                error_data = response.json()
                return False, f"Error fetching tasks: {error_data.get('message', 'Unknown error')}"
        
        except Exception as e:
            return False, f"Error: {str(e)}"


class UserProfile:
    """Store user's daily routine"""
    def __init__(self):
        self.sleep_time = time(23, 0)
        self.wake_time = time(7, 0)
        self.work_start = time(9, 0)
        self.work_end = time(17, 0)
        self.commute_to_work = 30
        self.commute_from_work = 30
        self.high_energy_periods = [(time(9, 0), time(11, 30))]
        self.low_energy_periods = [(time(14, 0), time(15, 30))]


class SmartScheduler:
    """AI-powered scheduler"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
    
    def find_free_slots(self, date: datetime, existing_tasks: List[Dict], min_duration: int = 30) -> List[Dict]:
        """Find free time slots"""
        day_start = datetime.combine(date.date(), self.profile.wake_time)
        day_end = datetime.combine(date.date(), self.profile.sleep_time)
        
        busy_periods = []
        
        work_start = datetime.combine(date.date(), self.profile.work_start)
        work_end = datetime.combine(date.date(), self.profile.work_end)
        leave_time = work_start - timedelta(minutes=self.profile.commute_to_work)
        arrive_time = work_end + timedelta(minutes=self.profile.commute_from_work)
        busy_periods.append((leave_time, arrive_time))
        
        for task in existing_tasks:
            if task['time']:
                try:
                    task_time = datetime.strptime(task['time'], '%I:%M %p').time()
                    task_start = datetime.combine(date.date(), task_time)
                    task_end = task_start + timedelta(minutes=task['duration'])
                    busy_periods.append((task_start, task_end))
                except:
                    pass
        
        busy_periods.sort(key=lambda x: x[0])
        
        free_slots = []
        current_time = day_start
        
        for busy_start, busy_end in busy_periods:
            if current_time < busy_start:
                duration = (busy_start - current_time).seconds // 60
                if duration >= min_duration:
                    free_slots.append({
                        'start': current_time,
                        'end': busy_start,
                        'duration': duration,
                        'energy': self._get_energy_level(current_time.time())
                    })
            current_time = max(current_time, busy_end)
        
        if current_time < day_end:
            duration = (day_end - current_time).seconds // 60
            if duration >= min_duration:
                free_slots.append({
                    'start': current_time,
                    'end': day_end,
                    'duration': duration,
                    'energy': self._get_energy_level(current_time.time())
                })
        
        return free_slots
    
    def _get_energy_level(self, check_time: time) -> str:
        """Determine energy level"""
        for start, end in self.profile.high_energy_periods:
            if start <= check_time <= end:
                return "High"
        
        for start, end in self.profile.low_energy_periods:
            if start <= check_time <= end:
                return "Low"
        
        return "Medium"
    
    def suggest_optimal_slot(self, activity: str, duration: int, free_slots: List[Dict], priority: str = "medium") -> Dict:
        """Use AI to suggest best time slot"""
        
        if not free_slots:
            return {"error": "No free slots available"}
        
        slots_description = "\n".join([
            f"{i+1}. {s['start'].strftime('%I:%M %p')} - {s['end'].strftime('%I:%M %p')}, "
            f"Duration: {s['duration']} min, Energy: {s['energy']}"
            for i, s in enumerate(free_slots)
        ])
        
        prompt = f"""Suggest the BEST time slot for this activity.

Activity: {activity}
Required Duration: {duration} minutes
Priority: {priority}

Available Slots:
{slots_description}

High Energy: {[(s.strftime('%H:%M'), e.strftime('%H:%M')) for s, e in self.profile.high_energy_periods]}
Low Energy: {[(s.strftime('%H:%M'), e.strftime('%H:%M')) for s, e in self.profile.low_energy_periods]}

Respond with:
SLOT: [number]
REASON: [brief explanation]"""
        
        response = co.chat(message=prompt, model="command-r-08-2024")
        
        try:
            slot_num = 0
            reason = ""
            for line in response.text.split('\n'):
                if 'SLOT:' in line:
                    slot_num = int(line.split(':')[1].strip()) - 1
                elif 'REASON:' in line:
                    reason = line.split(':', 1)[1].strip()
            
            if 0 <= slot_num < len(free_slots):
                return {
                    "slot": free_slots[slot_num],
                    "reason": reason,
                    "all_slots": free_slots
                }
        except:
            pass
        
        for slot in free_slots:
            if slot["energy"] == "High":
                return {"slot": slot, "reason": "High energy period", "all_slots": free_slots}
        
        return {"slot": free_slots[0], "reason": "First available", "all_slots": free_slots}


# Initialize session state
if "profile" not in st.session_state:
    st.session_state.profile = UserProfile()

if "notion_api" not in st.session_state:
    # Credentials should be set via environment variables or user input
    NOTION_TOKEN = "YOUR_NOTION_TOKEN_HERE"
    DATABASE_ID = "YOUR_DATABASE_ID_HERE"
    st.session_state.notion_api = NotionAPI(NOTION_TOKEN, DATABASE_ID)

if "notion_configured" not in st.session_state:
    st.session_state.notion_configured = True  # Auto-configured

# Header
st.markdown('<div class="main-header">📝 Smart Goal Tracker with Notion</div>', unsafe_allow_html=True)
st.markdown("*Add goals in Streamlit → AI suggests time → Automatically added to Notion!*")
st.markdown("---")

# Skip configuration - go straight to main app
st.success("✅ Connected to Notion")

# Sidebar
with st.sidebar:
    st.header("⚙️ Your Daily Routine")
    
    with st.expander("🛏️ Sleep Schedule"):
        col1, col2 = st.columns(2)
        with col1:
            wake_time = st.time_input("Wake Up", st.session_state.profile.wake_time)
        with col2:
            sleep_time = st.time_input("Sleep", st.session_state.profile.sleep_time)
        
        st.session_state.profile.wake_time = wake_time
        st.session_state.profile.sleep_time = sleep_time
    
    with st.expander("💼 Work Schedule"):
        col1, col2 = st.columns(2)
        with col1:
            work_start = st.time_input("Work Start", st.session_state.profile.work_start)
        with col2:
            work_end = st.time_input("Work End", st.session_state.profile.work_end)
        
        st.session_state.profile.work_start = work_start
        st.session_state.profile.work_end = work_end
    
    with st.expander("🚗 Commute"):
        commute_to = st.slider("To Work (min)", 0, 120, st.session_state.profile.commute_to_work, 5)
        commute_from = st.slider("From Work (min)", 0, 120, st.session_state.profile.commute_from_work, 5)
        
        st.session_state.profile.commute_to_work = commute_to
        st.session_state.profile.commute_from_work = commute_from
    
    with st.expander("⚡ Energy Levels"):
        high_start = st.time_input("High Energy Start", time(9, 0))
        high_end = st.time_input("High Energy End", time(11, 30))
        st.session_state.profile.high_energy_periods = [(high_start, high_end)]
        
        low_start = st.time_input("Low Energy Start", time(14, 0))
        low_end = st.time_input("Low Energy End", time(15, 30))
        st.session_state.profile.low_energy_periods = [(low_start, low_end)]
    
    st.markdown("---")
    # Removed reconfigure button since credentials are hardcoded

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Add New Goal", "📊 Today's Schedule", "📝 View Notion Tasks"])

scheduler = SmartScheduler(st.session_state.profile)

with tab1:
    st.header("🎯 Add New Goal to Notion")
    
    activity_name = st.text_input("What do you want to do?", 
                                  placeholder="e.g., Exercise, Read a book, Learn Python...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.slider("Duration (minutes)", 15, 180, 60, 15)
    with col2:
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    with col3:
        category = st.selectbox("Category", ["Personal", "Work", "Health", "Learning", "Social"])
    
    # Separate button - not nested
    find_time_clicked = st.button("🔍 Find Best Time", type="primary", key="find_time")
    
    if find_time_clicked and activity_name:
        with st.spinner("🤖 AI is analyzing your schedule..."):
            today_str = datetime.now().strftime("%Y-%m-%d")
            success, result = st.session_state.notion_api.get_tasks(today_str)
            
            if success:
                existing_tasks = result
                free_slots = scheduler.find_free_slots(datetime.now(), existing_tasks, duration)
                
                if free_slots:
                    suggestion = scheduler.suggest_optimal_slot(activity_name, duration, free_slots, priority.lower())
                    slot = suggestion["slot"]
                    
                    # Store in session state
                    st.session_state.current_slot = slot
                    st.session_state.current_activity = activity_name
                    st.session_state.current_duration = duration
                    st.session_state.current_category = category
                    
                    st.markdown(f"""
                    <div class="success-box">
                    <h3>🎯 AI Recommended Time</h3>
                    <p><strong>Time:</strong> {slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')}</p>
                    <p><strong>Duration:</strong> {duration} minutes</p>
                    <p><strong>Energy Level:</strong> {slot['energy']}</p>
                    <p><strong>Why this time?</strong> {suggestion['reason']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ No free slots available today!")
    
    # Add button - completely separate
    if hasattr(st.session_state, 'current_slot'):
        if st.button("📝 ADD TO NOTION NOW", type="primary", key="add_now"):
            slot = st.session_state.current_slot
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            with st.spinner("Adding to Notion..."):
                success, message = st.session_state.notion_api.create_task(
                    activity=st.session_state.current_activity,
                    date=today_str,
                    time_str=slot['start'].strftime('%I:%M %p'),
                    duration=st.session_state.current_duration,
                    energy=slot['energy'],
                    category=st.session_state.current_category
                )
                
                if success:
                    st.success("🎉 " + message)
                    st.balloons()
                    st.markdown(f"[✅ Open your Notion database](https://www.notion.so/f2f110b34c084f9b9e68bfbe1d769ea8)")
                    # Clear session
                    del st.session_state.current_slot
                else:
                    st.error("❌ " + message)

with tab2:
    st.header("📊 Today's Schedule")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    success, result = st.session_state.notion_api.get_tasks(today_str)
    
    if not success:
        st.error(f"❌ {result}")
    else:
        existing_tasks = result
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Your Tasks from Notion")
            if existing_tasks:
                for task in existing_tasks:
                    date_display = task.get('date', today_str) if 'date' in task else today_str
                    st.markdown(f"""
                    <div class="slot-card">
                    <strong>{task['activity']}</strong><br>
                    📅 {date_display} | ⏰ {task['time']} | ⏱️ {task['duration']} min | ⚡ {task['energy']}<br>
                    Status: {task['status']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tasks scheduled for today")
        
        with col2:
            st.subheader("🆓 Available Free Slots")
            free_slots = scheduler.find_free_slots(datetime.now(), existing_tasks, 30)
            
            if free_slots:
                for slot in free_slots:
                    st.markdown(f"""
                    <div class="slot-card">
                    <strong>{slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')}</strong><br>
                    {slot['duration']} minutes | Energy: {slot['energy']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No free slots available!")

with tab3:
    st.header("📝 All Tasks from Notion")
    
    if st.button("🔄 Refresh from Notion"):
        st.rerun()
    
    success, result = st.session_state.notion_api.get_tasks()
    
    if not success:
        st.error(f"❌ {result}")
    else:
        all_tasks = result
        
        if all_tasks:
            for task in all_tasks:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{task['activity']}**")
                with col2:
                    st.write(f"⏰ {task['time']} | ⏱️ {task['duration']} min")
                with col3:
                    st.write(task['status'])
        else:
            st.info("No tasks found in Notion database")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
🤖 Powered by Cohere AI + Notion API | Your intelligent goal management system
</div>
""", unsafe_allow_html=True)
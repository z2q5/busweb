import streamlit as st
import pandas as pd
import datetime
import json
import pickle
from pathlib import Path
import requests
import time
import base64
from io import BytesIO

# ===== إعداد الصفحة =====
st.set_page_config(
    page_title="Smart Bus System - Al Muneera Private School", 
    layout="wide",
    page_icon="🚍",
    initial_sidebar_state="collapsed",
    initial_sidebar_state="collapsed"
)

# ===== CSS مخصص محسن =====
def load_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,107,107,0.4);
    }
    
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    .student-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-right: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .student-card:hover {
        transform: translateX(-5px);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(102,126,234,0.3);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .status-coming {
        background: #d4edda;
        color: #155724;
    }
    
    .status-not-coming {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    
    .nav-button {
        background: white;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .nav-button:hover, .nav-button.active {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-top: 3rem;
    }
    
    .success-msg {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-right: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-msg {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-right: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #e7f3ff;
        border-right: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* تأثيرات الحركة */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* تحسين الجداول */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* تحسين الأزرار الراديو */
    .stRadio>div {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .stRadio>div>label {
        background: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stRadio>div>label:hover {
        border-color: #667eea;
    }
    
    /* وضع التباين العالي */
    .high-contrast {
        filter: contrast(150%);
    }
    
    .high-contrast .main {
        background: #000;
        color: #fff;
        border: 3px solid #fff;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ===== مسار حفظ البيانات =====
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

# ===== حالة التطبيق المحسنة =====
default_states = {
    "lang": "ar",
    "page": "student",
    "notifications": [],
    "driver_logged_in": False,
    "current_bus": "1",
    "theme": "light",
    "bus_passwords": {"1": "1111", "2": "2222", "3": "3333"},
    "admin_password": "admin123",
    "admin_logged_in": False,
    "ratings_df": pd.DataFrame(columns=["rating", "comment", "timestamp"]),
    "selected_rating": 0,
    "data_loaded": False,
    "offline_mode": False,
    "first_time": True,
    "last_save": datetime.datetime.now(),
    "font_size": "افتراضي",
    "high_contrast": False,
    "chat_messages": [],
    "sync_pending": False,
    "show_rating_dialog": False,
    "animation_enabled": True
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ===== وظائف حفظ البيانات المحسنة =====
def save_data():
    """حفظ جميع البيانات في الملفات مع معالجة الأخطاء"""
    try:
        save_tasks = [
            ('students_df', 'students.pkl'),
            ('attendance_df', 'attendance.pkl'),
            ('ratings_df', 'ratings.pkl')
        ]
        
        for df_key, filename in save_tasks:
            if df_key in st.session_state:
                filepath = DATA_DIR / filename
                with open(filepath, "wb") as f:
                    pickle.dump(st.session_state[df_key].to_dict(), f)
        
        # حفظ الإعدادات
        settings = {
            "bus_passwords": st.session_state.bus_passwords,
            "admin_password": st.session_state.admin_password,
            "theme": st.session_state.theme,
            "lang": st.session_state.lang,
            "font_size": st.session_state.font_size,
            "high_contrast": st.session_state.high_contrast,
        }
        
        with open(DATA_DIR / "settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)
            
        st.session_state.last_save = datetime.datetime.now()
        return True
        
    except Exception as e:
        st.error(f"❌ خطأ في حفظ البيانات: {str(e)}")
        return False

def load_data():
    """تحميل البيانات المحفوظة مع التحقق من الصحة"""
    try:
        files_to_load = [
            ('students.pkl', 'students_df'),
            ('attendance.pkl', 'attendance_df'),
            ('ratings.pkl', 'ratings_df')
        ]
        
        for filename, df_key in files_to_load:
            filepath = DATA_DIR / filename
            if filepath.exists():
                with open(filepath, "rb") as f:
                    data = pickle.load(f)
                    st.session_state[df_key] = pd.DataFrame(data)
        
        # تحميل الإعدادات
        settings_path = DATA_DIR / "settings.json"
        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                st.session_state.bus_passwords = settings.get("bus_passwords", {"1": "1111", "2": "2222", "3": "3333"})
                st.session_state.admin_password = settings.get("admin_password", "admin123")
                st.session_state.theme = settings.get("theme", "light")
                st.session_state.lang = settings.get("lang", "ar")
                st.session_state.font_size = settings.get("font_size", "افتراضي")
                st.session_state.high_contrast = settings.get("high_contrast", False)
                
    except Exception as e:
        st.warning(f"⚠️ تم إنشاء بيانات جديدة: {str(e)}")

# ===== البيانات الافتراضية المحسنة =====
def initialize_data():
    """تهيئة البيانات الافتراضية"""
    if 'students_df' not in st.session_state:
        students_data = [
            {"id": "1001", "name": "أحمد محمد", "grade": "10-A", "bus": "1", "parent_phone": "0501234567", "photo": None},
            {"id": "1002", "name": "فاطمة علي", "grade": "9-B", "bus": "2", "parent_phone": "0507654321", "photo": None},
            {"id": "1003", "name": "خالد إبراهيم", "grade": "8-C", "bus": "3", "parent_phone": "0505555555", "photo": None},
            {"id": "1004", "name": "سارة عبدالله", "grade": "10-B", "bus": "1", "parent_phone": "0504444444", "photo": None},
            {"id": "1005", "name": "محمد حسن", "grade": "7-A", "bus": "2", "parent_phone": "0503333333", "photo": None},
            {"id": "1006", "name": "ريم أحمد", "grade": "11-A", "bus": "3", "parent_phone": "0506666666", "photo": None},
            {"id": "1007", "name": "يوسف خالد", "grade": "6-B", "bus": "1", "parent_phone": "0507777777", "photo": None},
            {"id": "1008", "name": "نورة سعيد", "grade": "9-A", "bus": "2", "parent_phone": "0508888888", "photo": None},
        ]
        st.session_state.students_df = pd.DataFrame(students_data)

    if 'attendance_df' not in st.session_state:
        st.session_state.attendance_df = pd.DataFrame(columns=[
            "id", "name", "grade", "bus", "status", "time", "date", "location"
        ])

    if 'ratings_df' not in st.session_state:
        st.session_state.ratings_df = pd.DataFrame(columns=["rating", "comment", "timestamp", "user_type"])

# تحميل البيانات
load_data()
initialize_data()

# ===== الترجمة الكاملة والمحدثة =====
translations = {
    "ar": {
        # ... (الترجمات العربية الكاملة من الكود الأصلي)
        "title": "🚍 نظام الباص الذكي",
        "subtitle": "مدرسة المنيرة الخاصة - أبوظبي",
        "description": "نظام متكامل لإدارة النقل المدرسي الذكي",
        "student": "🎓 الطالب",
        "driver": "🚌 السائق", 
        "parents": "👨‍👩‍👧 أولياء الأمور",
        "admin": "🏫 الإدارة",
        "about": "ℹ️ حول النظام",
        "settings": "⚙️ الإعدادات",
        
        # صفحة الطالب
        "student_title": "🎓 تسجيل حضور الطالب",
        "student_desc": "أدخل رقم الوزارة لتسجيل حالتك اليوم",
        "student_id": "🔍 رقم الوزارة",
        "student_id_placeholder": "أدخل رقم الوزارة هنا...",
        "student_info": "🎓 معلومات الطالب",
        "grade": "📚 الصف",
        "bus": "🚍 الباص",
        "parent_phone": "📞 هاتف ولي الأمر",
        "already_registered": "✅ تم التسجيل مسبقاً",
        "current_status": "حالتك الحالية",
        "change_status": "🔄 تغيير الحالة",
        "choose_status": "اختر حالتك اليوم:",
        "coming": "✅ سأحضر اليوم",
        "not_coming": "❌ لن أحضر اليوم",
        "registered_success": "🎉 تم التسجيل بنجاح!",
        "student_name": "الطالب",
        "status": "الحالة",
        "time": "وقت التسجيل",
        "bus_number": "رقم الباص",
        "stats_title": "📊 إحصائيات اليوم",
        "total_registered": "إجمالي المسجلين",
        "expected_attendance": "الحضور المتوقع",
        "attendance_rate": "نسبة الحضور",
        
        # ... (بقية الترجمات العربية)
        "footer": "🚍 muneerago - الإصدار 2.0",
        "rights": "© 2025 جميع الحقوق محفوظة",
        "team": "تم التطوير بواسطة: إياد مصطفى | التصميم: إياد مصطفى | الإشراف: قسم النادي البيئي",
    },
    "en": {
        # English translations (مكتملة)
        "title": "🚍 Smart Bus System",
        "subtitle": "Al Muneera Private School - Abu Dhabi",
        "description": "Integrated system for smart school transportation management",
        "student": "🎓 Student",
        "driver": "🚌 Driver", 
        "parents": "👨‍👩‍👧 Parents",
        "admin": "🏫 Admin",
        "about": "ℹ️ About",
        "settings": "⚙️ Settings",
        
        # Student Page
        "student_title": "🎓 Student Attendance Registration",
        "student_desc": "Enter your ministry number to register your status today",
        "student_id": "🔍 Ministry Number",
        "student_id_placeholder": "Enter ministry number here...",
        "student_info": "🎓 Student Information",
        "grade": "📚 Grade",
        "bus": "🚍 Bus",
        "parent_phone": "📞 Parent Phone",
        "already_registered": "✅ Already Registered",
        "current_status": "Your Current Status",
        "change_status": "🔄 Change Status",
        "choose_status": "Choose your status today:",
        "coming": "✅ I will attend today",
        "not_coming": "❌ I will not attend today",
        "registered_success": "🎉 Registration Successful!",
        "student_name": "Student",
        "status": "Status",
        "time": "Registration Time",
        "bus_number": "Bus Number",
        "stats_title": "📊 Today's Statistics",
        "total_registered": "Total Registered",
        "expected_attendance": "Expected Attendance",
        "attendance_rate": "Attendance Rate",
        
        # Driver Page
        "driver_title": "🚌 Driver Control Panel",
        "driver_login": "🔐 Driver Login",
        "select_bus": "Select Bus",
        "password": "Password",
        "password_placeholder": "Enter password...",
        "login": "🚀 Login",
        "logout": "🚪 Logout",
        "student_list": "📋 Student List",
        "coming_students": "🎒 Students Coming Today",
        "all_students": "👥 All Bus Students",
        "total_students": "👥 Total Students",
        "confirmed_attendance": "✅ Confirmed Attendance",
        "attendance_percentage": "📈 Attendance Percentage",
        "no_students": "🚫 No students coming today",
        "status_coming": "Coming",
        "status_not_coming": "Not Coming",
        "status_not_registered": "Not Registered",
        
        # Parents Page
        "parents_title": "👨‍👩‍👧 Parents Portal",
        "parents_id_placeholder": "Example: 1001",
        "attendance_tracking": "📊 Attendance Tracking",
        "bus_info": "🚌 Bus Information",
        "morning_time": "Approximate Morning Time",
        "afternoon_time": "Approximate Afternoon Time",
        "track_student": "🔍 Track Student",
        "enter_student_id": "Enter student ministry number",
        "today_status": "Today's Status",
        "registration_time": "Registration Time",
        "bus_schedule": "⏰ Bus Schedule",
        "morning_pickup": "Morning Pickup",
        "evening_return": "Evening Return",
        "driver_contact": "📞 Driver Contact",
        "contact_info": "Contact Information",
        "bus_location": "📍 Bus Location",
        "current_location": "Current Location",
        
        # Admin Page
        "admin_title": "🏫 Admin Control Panel",
        "admin_login": "🔐 Admin Login",
        "admin_password": "Admin Password",
        "system_stats": "📊 System Statistics",
        "students_count": "Students Count",
        "attendance_records": "Attendance Records",
        "system_actions": "⚙️ System Actions",
        "reset_data": "🔄 Reset Data",
        "backup": "📥 Backup",
        "change_admin_password": "Change Admin Password",
        "current_passwords": "Current Passwords",
        "change_bus_password": "Change Bus Passwords",
        "select_bus_password": "Select Bus",
        "new_password": "New Password",
        "save_changes": "💾 Save Changes",
        
        # Student Management
        "add_student": "➕ Add New Student",
        "new_student_info": "New Student Information",
        "student_name": "Student Name",
        "student_name_placeholder": "Enter full student name...",
        "student_id": "Ministry Number",
        "student_id_placeholder": "Enter ministry number...",
        "select_grade": "Select Grade",
        "select_bus": "Select Bus",
        "parent_phone_placeholder": "Enter parent phone number...",
        "add_student_button": "➕ Add Student",
        "student_added_success": "✅ Student added successfully!",
        "student_exists_error": "❌ Ministry number already exists!",
        "delete_student": "🗑️ Delete Student",
        "delete_student_confirm": "Are you sure you want to delete this student?",
        "student_deleted_success": "✅ Student deleted successfully!",
        "edit_student": "✏️ Edit Student Data",
        "student_updated_success": "✅ Student data updated successfully!",
        "manage_students": "👥 Manage Students",
        "export_data": "📤 Export Data",
        "filter_data": "🔍 Filter Data",
        "filter_by_bus": "Filter by Bus",
        "filter_by_grade": "Filter by Grade",
        "filter_by_status": "Filter by Status",
        "all": "All",
        
        # About Page
        "about_title": "ℹ️ About System",
        "about_description": "Integrated smart school transportation management system at Al Muneera Private School in Abu Dhabi.",
        "features": "🎯 Key Features",
        "development_team": "👥 Development Team",
        "developer": "System Developer",
        "designer": "UI Designer",
        "version_info": "📋 Version Info",
        "version": "Version",
        "release_date": "Release Date",
        "status_stable": "⭐ Stable Release",
        "contact_developer": "📧 Contact Developer",
        "developer_email": "Email: eyadmustafaali99@gmail.com",
        "contact_form": "📝 Contact Form",
        
        # System Messages
        "not_found": "Student not found",
        "error": "System error occurred",
        "reset_success": "Your status has been reset",
        "login_success": "Login successful",
        "login_error": "Incorrect password",
        "data_reset_success": "Data reset successfully",
        "backup_success": "Backup created successfully",
        "password_updated": "Password updated successfully",
        
        # Settings
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        "language": "🌐 Language",
        
        # Rating System
        "rating_system": "⭐ Advanced Rating System",
        "rate_app": "Rate your experience with the app",
        "your_rating": "Your Rating",
        "your_comment": "Share your feedback (optional)",
        "submit_rating": "Submit Rating",
        "thank_you_rating": "Thank you for your rating!",
        "average_rating": "Average Rating",
        "total_ratings": "Total Ratings",
        "rating_success": "Your rating has been submitted successfully!",
        "select_rating": "Select star rating",
        "excellent": "Excellent",
        "very_good": "Very Good",
        "good": "Good",
        "fair": "Fair",
        "poor": "Poor",
        
        # Footer
        "footer": "🚍 muneerago - Version 2.0",
        "rights": "© 2025 All Rights Reserved",
        "team": "Developed by: Eyad Mustafa | Design: Eyad Mustafa | Supervision: Environmental Club",
        
        # Features
        "feature1": "Smart Attendance",
        "feature1_desc": "Automatic and easy attendance system for students",
        "feature2": "Live Tracking", 
        "feature2_desc": "Real-time tracking of bus movements and attendance",
        "feature3": "Service Rating",
        "feature3_desc": "Advanced rating system for service quality",
        "feature4": "Instant Notifications",
        "feature4_desc": "Instant notifications 
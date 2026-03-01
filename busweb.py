import streamlit as st
import pandas as pd
import datetime
import json
import pickle
from pathlib import Path
import requests
import time
import numpy as np

# ===== إعداد الصفحة =====
st.set_page_config(
    page_title="Smart Bus System - Al Muneera Private School", 
    layout="wide",
    page_icon="🚍",
    initial_sidebar_state="collapsed"
)

# ===== مسار حفظ البيانات =====
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

# ===== حالة التطبيق المحسنة =====
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "page" not in st.session_state:
    st.session_state.page = "student"
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "driver_logged_in" not in st.session_state:
    st.session_state.driver_logged_in = False
if "current_bus" not in st.session_state:
    st.session_state.current_bus = "1"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "bus_passwords" not in st.session_state:
    st.session_state.bus_passwords = {"1": "1111", "2": "2222", "3": "3333"}
if "admin_password" not in st.session_state:
    st.session_state.admin_password = "admin123"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "ratings_df" not in st.session_state:
    st.session_state.ratings_df = pd.DataFrame(columns=["rating", "comment", "timestamp"])
if "selected_rating" not in st.session_state:
    st.session_state.selected_rating = 0
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "offline_mode" not in st.session_state:
    st.session_state.offline_mode = False
if "first_time" not in st.session_state:
    st.session_state.first_time = True
if "last_save" not in st.session_state:
    st.session_state.last_save = datetime.datetime.now()
if "font_size" not in st.session_state:
    st.session_state.font_size = "افتراضي"
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "sync_pending" not in st.session_state:
    st.session_state.sync_pending = False
if "student_search" not in st.session_state:
    st.session_state.student_search = ""
if "contact_submitted" not in st.session_state:
    st.session_state.contact_submitted = False
if "student_health_conditions" not in st.session_state:
    st.session_state.student_health_conditions = {}
if "temp_rating" not in st.session_state:
    st.session_state.temp_rating = 0

# ===== وظائف حفظ البيانات =====
def save_data():
    """حفظ جميع البيانات في الملفات"""
    try:
        # حفظ بيانات الطلاب
        if 'students_df' in st.session_state and not st.session_state.students_df.empty:
            students_dict = st.session_state.students_df.to_dict(orient='list')
            with open(DATA_DIR / "students.pkl", "wb") as f:
                pickle.dump(students_dict, f)
        
        # حفظ بيانات الحضور
        if 'attendance_df' in st.session_state and not st.session_state.attendance_df.empty:
            attendance_dict = st.session_state.attendance_df.to_dict(orient='list')
            with open(DATA_DIR / "attendance.pkl", "wb") as f:
                pickle.dump(attendance_dict, f)
        
        # حفظ بيانات التقييمات
        if 'ratings_df' in st.session_state and not st.session_state.ratings_df.empty:
            ratings_dict = st.session_state.ratings_df.to_dict(orient='list')
            with open(DATA_DIR / "ratings.pkl", "wb") as f:
                pickle.dump(ratings_dict, f)
        
        # حفظ الحالات الصحية
        if 'student_health_conditions' in st.session_state:
            with open(DATA_DIR / "health_conditions.pkl", "wb") as f:
                pickle.dump(st.session_state.student_health_conditions, f)
        
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
            json.dump(settings, f, ensure_ascii=False, indent=2)
            
        st.session_state.last_save = datetime.datetime.now()
        return True
        
    except Exception as e:
        st.error(f"خطأ في حفظ البيانات: {e}")
        return False

def load_data():
    """تحميل البيانات المحفوظة"""
    try:
        # تحميل بيانات الطلاب
        if (DATA_DIR / "students.pkl").exists():
            with open(DATA_DIR / "students.pkl", "rb") as f:
                students_dict = pickle.load(f)
                st.session_state.students_df = pd.DataFrame(students_dict)
        
        # تحميل بيانات الحضور
        if (DATA_DIR / "attendance.pkl").exists():
            with open(DATA_DIR / "attendance.pkl", "rb") as f:
                attendance_dict = pickle.load(f)
                st.session_state.attendance_df = pd.DataFrame(attendance_dict)
        
        # تحميل بيانات التقييمات
        if (DATA_DIR / "ratings.pkl").exists():
            with open(DATA_DIR / "ratings.pkl", "rb") as f:
                ratings_dict = pickle.load(f)
                st.session_state.ratings_df = pd.DataFrame(ratings_dict)
        
        # تحميل الحالات الصحية
        if (DATA_DIR / "health_conditions.pkl").exists():
            with open(DATA_DIR / "health_conditions.pkl", "rb") as f:
                st.session_state.student_health_conditions = pickle.load(f)
        else:
            st.session_state.student_health_conditions = {}
                
        # تحميل الإعدادات
        if (DATA_DIR / "settings.json").exists():
            with open(DATA_DIR / "settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                st.session_state.bus_passwords = settings.get("bus_passwords", {"1": "1111", "2": "2222", "3": "3333"})
                st.session_state.admin_password = settings.get("admin_password", "admin123")
                st.session_state.theme = settings.get("theme", "light")
                st.session_state.lang = settings.get("lang", "ar")
                st.session_state.font_size = settings.get("font_size", "افتراضي")
                st.session_state.high_contrast = settings.get("high_contrast", False)
                
        st.session_state.data_loaded = True
        return True
        
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {e}")
        return False

# ===== البيانات الافتراضية =====
def initialize_data():
    """تهيئة البيانات الافتراضية"""
    if 'students_df' not in st.session_state or st.session_state.students_df.empty:
        students_data = [
            {"id": "1001", "name": "أحمد محمد", "grade": "10-A", "bus": "1", "parent_phone": "0501234567"},
            {"id": "1002", "name": "فاطمة علي", "grade": "9-B", "bus": "2", "parent_phone": "0507654321"},
            {"id": "1003", "name": "خالد إبراهيم", "grade": "8-C", "bus": "3", "parent_phone": "0505555555"},
            {"id": "1004", "name": "سارة عبدالله", "grade": "10-B", "bus": "1", "parent_phone": "0504444444"},
            {"id": "1005", "name": "محمد حسن", "grade": "7-A", "bus": "2", "parent_phone": "0503333333"},
            {"id": "1006", "name": "ريم أحمد", "grade": "11-A", "bus": "3", "parent_phone": "0506666666"},
            {"id": "1007", "name": "يوسف خالد", "grade": "6-B", "bus": "1", "parent_phone": "0507777777"},
            {"id": "1008", "name": "نورة سعيد", "grade": "9-A", "bus": "2", "parent_phone": "0508888888"},
        ]
        st.session_state.students_df = pd.DataFrame(students_data)
    
    if 'attendance_df' not in st.session_state or st.session_state.attendance_df.empty:
        st.session_state.attendance_df = pd.DataFrame(columns=[
            "id", "name", "grade", "bus", "status", "time", "date"
        ])
    
    if 'ratings_df' not in st.session_state or st.session_state.ratings_df.empty:
        st.session_state.ratings_df = pd.DataFrame(columns=["rating", "comment", "timestamp"])
    
    if 'student_health_conditions' not in st.session_state:
        st.session_state.student_health_conditions = {}
    
    save_data()

# تحميل البيانات المحفوظة
if not st.session_state.data_loaded:
    load_data()

# تهيئة البيانات إذا كانت فارغة
initialize_data()

# ===== الترجمة الكاملة =====
translations = {
    "ar": {
        # التنقل الرئيسي
        "title": "🚍 نظام الباص الذكي",
        "subtitle": "مدرسة المنيرة الخاصة - أبوظبي",
        "description": "نظام متكامل لإدارة النقل المدرسي الذكي",
        "student": "🎓 الطالب",
        "driver": "🚌 السائق", 
        "parents": "👨‍👩‍👧 أولياء الأمور",
        "admin": "🏫 الإدارة",
        "about": "ℹ️ حول النظام",
        
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
        
        # صفحة السائق
        "driver_title": "🚌 لوحة تحكم السائق",
        "driver_login": "🔐 تسجيل دخول السائق",
        "select_bus": "اختر الباص",
        "password": "كلمة المرور",
        "password_placeholder": "أدخل كلمة المرور...",
        "login": "🚀 تسجيل الدخول",
        "logout": "🚪 تسجيل الخروج",
        "student_list": "📋 قائمة الطلاب",
        "coming_students": "🎒 الطلاب القادمون اليوم",
        "all_students": "👥 جميع طلاب الباص",
        "total_students": "👥 إجمالي الطلاب",
        "confirmed_attendance": "✅ الحضور المؤكد",
        "attendance_percentage": "📈 نسبة الحضور",
        "no_students": "🚫 لا يوجد طلاب قادمين اليوم",
        "status_coming": "قادم",
        "status_not_coming": "لن يحضر",
        "status_not_registered": "لم يسجل",
        "register_attendance": "📝 تسجيل حضور",
        "mark_present": "✅ تسجيل حضور",
        "mark_absent": "❌ تسجيل غياب",
        "health_conditions": "🏥 الحالات الصحية",
        "student_health": "الحالة الصحية للطالب",
        "add_health_condition": "➕ إضافة حالة صحية",
        "chronic_disease": "مرض مزمن",
        "allergy": "حساسية",
        "injury": "إصابة",
        "other": "أخرى",
        "condition_description": "وصف الحالة",
        "no_health_conditions": "لا توجد حالات صحية مسجلة",
        "delete_condition": "🗑️ حذف الحالة",
        
        # صفحة أولياء الأمور
        "parents_title": "👨‍👩‍👧 بوابة أولياء الأمور",
        "parents_id_placeholder": "مثال: 1001",
        "attendance_tracking": "📊 متابعة الحضور",
        "bus_info": "🚌 معلومات الباص",
        "morning_time": "وقت الصباح التقريبي",
        "afternoon_time": "وقت الظهيرة التقريبي",
        "track_student": "🔍 متابعة الطالب",
        "enter_student_id": "أدخل رقم وزارة الطالب",
        "today_status": "حالة اليوم",
        "registration_time": "وقت التسجيل",
        "bus_schedule": "⏰ جدول الباص",
        "morning_pickup": "وقت الذهاب",
        "evening_return": "وقت العودة",
        "driver_contact": "📞 اتصال السائق",
        "contact_info": "معلومات الاتصال",
        "bus_location": "📍 موقع الباص",
        "current_location": "الموقع الحالي",
        "health_management": "🏥 إدارة الحالات الصحية",
        "student_health_info": "معلومات الحالة الصحية للطالب",
        "chronic_diseases": "الأمراض المزمنة",
        "allergies": "الحساسية",
        "injuries": "الإصابات",
        "medications": "الأدوية",
        "emergency_contact": "اتصال الطوارئ",
        "update_health_info": "تحديث المعلومات الصحية",
        "health_info_updated": "✅ تم تحديث المعلومات الصحية بنجاح",
        
        # صفحة الإدارة
        "admin_title": "🏫 لوحة تحكم الإدارة",
        "admin_login": "🔐 تسجيل دخول الإدارة",
        "admin_password": "كلمة مرور الإدارة",
        "system_stats": "📊 إحصائيات النظام",
        "students_count": "عدد الطلاب",
        "attendance_records": "سجلات الحضور",
        "system_actions": "⚙️ إجراءات النظام",
        "reset_data": "🔄 إعادة تعيين البيانات",
        "backup": "📥 نسخة احتياطية",
        "change_admin_password": "تغيير كلمة مرور الإدارة",
        "current_passwords": "كلمات المرور الحالية",
        "change_bus_password": "تغيير كلمات مرور الباصات",
        "select_bus_password": "اختر الباص",
        "new_password": "كلمة المرور الجديدة",
        "save_changes": "💾 حفظ التغييرات",
        
        # إدارة الطلاب
        "add_student": "➕ إضافة طالب جديد",
        "new_student_info": "معلومات الطالب الجديد",
        "student_name": "اسم الطالب",
        "student_name_placeholder": "أدخل اسم الطالب الكامل...",
        "student_id": "رقم الوزارة",
        "student_id_placeholder": "أدخل رقم الوزارة...",
        "select_grade": "اختر الصف",
        "select_bus": "اختر الباص",
        "parent_phone_placeholder": "أدخل رقم هاتف ولي الأمر...",
        "add_student_button": "➕ إضافة الطالب",
        "student_added_success": "✅ تم إضافة الطالب بنجاح!",
        "student_exists_error": "❌ رقم الوزارة موجود مسبقاً!",
        "delete_student": "🗑️ حذف الطالب",
        "delete_student_confirm": "هل أنت متأكد من حذف هذا الطالب؟",
        "student_deleted_success": "✅ تم حذف الطالب بنجاح!",
        "edit_student": "✏️ تعديل بيانات الطالب",
        "student_updated_success": "✅ تم تحديث بيانات الطالب بنجاح!",
        "manage_students": "👥 إدارة الطلاب",
        "export_data": "📤 تصدير البيانات",
        "filter_data": "🔍 تصفية البيانات",
        "filter_by_bus": "تصفية حسب الباص",
        "filter_by_grade": "تصفية حسب الصف",
        "filter_by_status": "تصفية حسب الحالة",
        "all": "الكل",
        
        # صفحة حول النظام
        "about_title": "ℹ️ حول النظام",
        "about_description": "نظام متكامل لإدارة النقل المدرسي الذكي في مدرسة المنيرة الخاصة بأبوظبي.",
        "features": "🎯 المميزات الرئيسية",
        "development_team": "👥 فريق التطوير",
        "developer": "مطور النظام",
        "designer": "مصمم الواجهة",
        "version_info": "📋 معلومات الإصدار",
        "version": "الإصدار",
        "release_date": "تاريخ الإصدار",
        "status_stable": "⭐ الإصدار المستقر",
        "contact_developer": "📧 التواصل مع المطور",
        "developer_email": "البريد الإلكتروني: eyadmustafaali99@gmail.com",
        "contact_form": "📝 نموذج التواصل",
        
        # رسائل النظام
        "not_found": "لم يتم العثور على الطالب",
        "error": "حدث خطأ في النظام",
        "reset_success": "تم إعادة تعيين حالتك",
        "login_success": "تم الدخول بنجاح",
        "login_error": "كلمة مرور غير صحيحة",
        "data_reset_success": "تم إعادة تعيين البيانات",
        "backup_success": "تم إنشاء نسخة احتياطية",
        "password_updated": "تم تحديث كلمة المرور",
        
        # الإعدادات
        "theme_light": "☀️",
        "theme_dark": "🌙",
        "language": "🌐",
        
        # نظام التقييم - تم تحسينه
        "rating_system": "⭐ نظام التقييم التفاعلي",
        "rate_app": "قيم تجربتك مع التطبيق",
        "your_rating": "تقييمك",
        "your_comment": "شاركنا رأيك (اختياري)",
        "submit_rating": "إرسال التقييم",
        "thank_you_rating": "شكراً جزيلاً لتقييمك!",
        "average_rating": "متوسط التقييم",
        "total_ratings": "إجمالي التقييمات",
        "rating_success": "تم إرسال تقييمك بنجاح!",
        "select_rating": "اختر عدد النجوم",
        "excellent": "ممتاز",
        "very_good": "جيد جداً",
        "good": "جيد",
        "fair": "مقبول",
        "poor": "ضعيف",
        "rate_now": "قيم الآن",
        "latest_ratings": "آخر التقييمات",
        "no_ratings_yet": "لا توجد تقييمات بعد، كن أول من يقيم!",
        "click_stars": "اضغط على النجوم للتقييم",
        
        # الفوتر
        "footer": "🚍 نظام الباص الذكي - الإصدار 2.0",
        "rights": "© 2025 جميع الحقوق محفوظة",
        "team": "تم التطوير بواسطة: إياد مصطفى",
        
        # مميزات النظام
        "feature1": "تسجيل حضور ذكي",
        "feature1_desc": "نظام تسجيل حضور آلي وسهل للطلاب",
        "feature2": "متابعة مباشرة", 
        "feature2_desc": "متابعة حية لتحركات الباصات والحضور",
        "feature3": "تقييم الخدمة",
        "feature3_desc": "نظام تقييم متطور لجودة الخدمة",
        "feature4": "إشعارات فورية",
        "feature4_desc": "إشعارات فورية لأولياء الأمور",
        "feature5": "واجهة متطورة",
        "feature5_desc": "تصميم حديث وسهل الاستخدام",
        "feature6": "أمان وحماية",
        "feature6_desc": "نظام حماية متكامل للبيانات",
        
        # التواصل مع المطور
        "contact_title": "📧 التواصل مع المطور",
        "contact_name": "👤 الاسم الكامل",
        "contact_email": "📧 البريد الإلكتروني",
        "contact_subject": "📋 نوع الرسالة",
        "contact_message": "💬 الرسالة",
        "contact_success": "✅ تم إرسال رسالتك بنجاح!",
        
        # المساعد الذكي
        "ai_assistant": "🤖 المساعد الذكي",
        "ai_welcome": "مرحباً! أنا المساعد الذكي لنظام الباص. كيف يمكنني مساعدتك؟",
        "ai_questions": "💬 أسئلة سريعة",
        "ai_placeholder": "💭 اكتب سؤالك هنا...",
        "ai_send": "🚀 إرسال"
    },
    "en": {
        # Main Navigation
        "title": "🚍 Smart Bus System",
        "subtitle": "Al Muneera Private School - Abu Dhabi",
        "description": "Integrated system for smart school transportation management",
        "student": "🎓 Student",
        "driver": "🚌 Driver", 
        "parents": "👨‍👩‍👧 Parents",
        "admin": "🏫 Admin",
        "about": "ℹ️ About",
        
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
        "register_attendance": "📝 Register Attendance",
        "mark_present": "✅ Mark Present",
        "mark_absent": "❌ Mark Absent",
        "health_conditions": "🏥 Health Conditions",
        "student_health": "Student Health Information",
        "add_health_condition": "➕ Add Health Condition",
        "chronic_disease": "Chronic Disease",
        "allergy": "Allergy",
        "injury": "Injury",
        "other": "Other",
        "condition_description": "Condition Description",
        "no_health_conditions": "No health conditions registered",
        "delete_condition": "🗑️ Delete Condition",
        
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
        "health_management": "🏥 Health Management",
        "student_health_info": "Student Health Information",
        "chronic_diseases": "Chronic Diseases",
        "allergies": "Allergies",
        "injuries": "Injuries",
        "medications": "Medications",
        "emergency_contact": "Emergency Contact",
        "update_health_info": "Update Health Information",
        "health_info_updated": "✅ Health information updated successfully",
        
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
        "about_description": "Integrated system for smart school transportation management at Al Muneera Private School in Abu Dhabi.",
        "features": "🎯 Main Features",
        "development_team": "👥 Development Team",
        "developer": "System Developer",
        "designer": "UI Designer",
        "version_info": "📋 Version Information",
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
        "theme_light": "☀️",
        "theme_dark": "🌙",
        "language": "🌐",
        
        # Rating System - Enhanced
        "rating_system": "⭐ Interactive Rating System",
        "rate_app": "Rate Your Experience",
        "your_rating": "Your Rating",
        "your_comment": "Share your feedback (optional)",
        "submit_rating": "Submit Rating",
        "thank_you_rating": "Thank you for your rating!",
        "average_rating": "Average Rating",
        "total_ratings": "Total Ratings",
        "rating_success": "Your rating has been submitted successfully!",
        "select_rating": "Select number of stars",
        "excellent": "Excellent",
        "very_good": "Very Good",
        "good": "Good",
        "fair": "Fair",
        "poor": "Poor",
        "rate_now": "Rate Now",
        "latest_ratings": "Latest Ratings",
        "no_ratings_yet": "No ratings yet, be the first to rate!",
        "click_stars": "Click on stars to rate",
        
        # Footer
        "footer": "🚍 Smart Bus System - Version 2.0",
        "rights": "© 2025 All Rights Reserved",
        "team": "Developed by: Eyad Mustafa",
        
        # Features
        "feature1": "Smart Attendance",
        "feature1_desc": "Automatic and easy student attendance system",
        "feature2": "Live Tracking", 
        "feature2_desc": "Real-time tracking of buses and attendance",
        "feature3": "Service Rating",
        "feature3_desc": "Advanced service quality rating system",
        "feature4": "Instant Notifications",
        "feature4_desc": "Instant notifications for parents",
        "feature5": "Modern Interface",
        "feature5_desc": "Modern and user-friendly design",
        "feature6": "Security & Protection",
        "feature6_desc": "Integrated data protection system",
        
        # Contact Developer
        "contact_title": "📧 Contact Developer",
        "contact_name": "👤 Full Name",
        "contact_email": "📧 Email Address",
        "contact_subject": "📋 Message Type",
        "contact_message": "💬 Message",
        "contact_success": "✅ Your message has been sent successfully!",
        
        # AI Assistant
        "ai_assistant": "🤖 AI Assistant",
        "ai_welcome": "Hello! I'm the Smart Bus System AI assistant. How can I help you?",
        "ai_questions": "💬 Common Questions",
        "ai_placeholder": "💭 Type your question here...",
        "ai_send": "🚀 Send"
    }
}

def t(key):
    """دالة الترجمة الآمنة"""
    try:
        return translations[st.session_state.lang][key]
    except KeyError:
        return key

# ===== وظائف مساعدة محسنة =====
def add_notification(message):
    """إضافة إشعار جديد"""
    st.session_state.notifications.append({
        "time": datetime.datetime.now().strftime("%H:%M"),
        "message": message
    })
    save_data()

def calculate_attendance_stats():
    """حساب إحصائيات الحضور"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.attendance_df.empty:
        return {"total": 0, "coming": 0, "percentage": 0}
    
    today_data = st.session_state.attendance_df[
        st.session_state.attendance_df["date"] == today
    ]
    
    total = len(today_data)
    coming = len(today_data[today_data["status"] == "قادم"]) if not today_data.empty else 0
    percentage = (coming / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "coming": coming,
        "percentage": percentage
    }

def has_student_registered_today(student_id):
    """التحقق من تسجيل الطالب اليوم"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.attendance_df.empty:
        return False, None
    
    student_data = st.session_state.attendance_df[
        (st.session_state.attendance_df["id"].astype(str) == str(student_id).strip()) & 
        (st.session_state.attendance_df["date"] == today)
    ]
    
    if not student_data.empty:
        latest_record = student_data.iloc[-1]
        return True, latest_record["status"]
    
    return False, None

def register_attendance(student, status):
    """تسجيل حضور الطالب"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # إزالة أي تسجيل سابق للطالب لنفس اليوم
    st.session_state.attendance_df = st.session_state.attendance_df[
        ~((st.session_state.attendance_df["id"].astype(str) == str(student["id"]).strip()) & 
          (st.session_state.attendance_df["date"] == today))
    ]
    
    now = datetime.datetime.now()
    new_entry = pd.DataFrame([{
        "id": student["id"],
        "name": student["name"], 
        "grade": student["grade"],
        "bus": student["bus"],
        "status": status,
        "time": now.strftime("%H:%M"),
        "date": today
    }])
    
    st.session_state.attendance_df = pd.concat([
        st.session_state.attendance_df, new_entry
    ], ignore_index=True)
    
    save_data()
    return now

def add_rating(rating, comment):
    """إضافة تقييم جديد"""
    try:
        new_rating = pd.DataFrame([{
            "rating": rating,
            "comment": comment if comment else "",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        if st.session_state.ratings_df.empty:
            st.session_state.ratings_df = new_rating
        else:
            st.session_state.ratings_df = pd.concat([
                st.session_state.ratings_df, new_rating
            ], ignore_index=True)
        
        save_data()
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة التقييم: {e}")
        return False

def get_average_rating():
    """حساب متوسط التقييم"""
    if st.session_state.ratings_df.empty:
        return 0, 0
    avg = st.session_state.ratings_df["rating"].mean()
    count = len(st.session_state.ratings_df)
    return avg, count

def toggle_theme():
    """تغيير الثيم"""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    save_data()
    st.rerun()

def toggle_language():
    """تغيير اللغة"""
    st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
    save_data()
    st.rerun()

# ===== وظائف إدارة الطلاب =====
def add_new_student(student_id, name, grade, bus, parent_phone):
    """إضافة طالب جديد إلى النظام"""
    try:
        # التحقق من عدم وجود رقم وزارة مكرر
        if str(student_id).strip() in st.session_state.students_df["id"].astype(str).values:
            return False, "student_exists"
        
        # إنشاء بيانات الطالب الجديد
        new_student = {
            "id": str(student_id).strip(),
            "name": name.strip(),
            "grade": grade,
            "bus": bus,
            "parent_phone": parent_phone.strip()
        }
        
        # إضافة الطالب إلى DataFrame
        new_student_df = pd.DataFrame([new_student])
        st.session_state.students_df = pd.concat([
            st.session_state.students_df, new_student_df
        ], ignore_index=True)
        
        # حفظ البيانات
        save_data()
        return True, "success"
        
    except Exception as e:
        return False, str(e)

def delete_student(student_id):
    """حذف طالب من النظام"""
    try:
        # حذف الطالب من بيانات الطلاب
        st.session_state.students_df = st.session_state.students_df[
            st.session_state.students_df["id"].astype(str) != str(student_id).strip()
        ]
        
        # حذف سجلات الحضور الخاصة بالطالب
        st.session_state.attendance_df = st.session_state.attendance_df[
            st.session_state.attendance_df["id"].astype(str) != str(student_id).strip()
        ]
        
        # حذف الحالات الصحية الخاصة بالطالب
        if str(student_id).strip() in st.session_state.student_health_conditions:
            del st.session_state.student_health_conditions[str(student_id).strip()]
        
        # حفظ البيانات
        save_data()
        return True, "success"
        
    except Exception as e:
        return False, str(e)

def update_student(student_id, name=None, grade=None, bus=None, parent_phone=None):
    """تحديث بيانات الطالب"""
    try:
        # العثور على الطالب
        mask = st.session_state.students_df["id"].astype(str) == str(student_id).strip()
        if not mask.any():
            return False, "not_found"
        
        # تحديث البيانات
        if name:
            st.session_state.students_df.loc[mask, "name"] = name
        if grade:
            st.session_state.students_df.loc[mask, "grade"] = grade
        if bus:
            st.session_state.students_df.loc[mask, "bus"] = bus
        if parent_phone:
            st.session_state.students_df.loc[mask, "parent_phone"] = parent_phone
        
        # حفظ البيانات
        save_data()
        return True, "success"
        
    except Exception as e:
        return False, str(e)

# ===== وظائف إدارة الحالات الصحية =====
def add_health_condition(student_id, condition_type, description):
    """إضافة حالة صحية للطالب"""
    try:
        student_id_str = str(student_id).strip()
        
        if student_id_str not in st.session_state.student_health_conditions:
            st.session_state.student_health_conditions[student_id_str] = []
        
        condition = {
            "type": condition_type,
            "description": description,
            "added_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.session_state.student_health_conditions[student_id_str].append(condition)
        save_data()
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة الحالة الصحية: {e}")
        return False

def delete_health_condition(student_id, condition_index):
    """حذف حالة صحية للطالب"""
    try:
        student_id_str = str(student_id).strip()
        
        if student_id_str in st.session_state.student_health_conditions:
            if 0 <= condition_index < len(st.session_state.student_health_conditions[student_id_str]):
                st.session_state.student_health_conditions[student_id_str].pop(condition_index)
                save_data()
                return True
        return False
    except Exception as e:
        st.error(f"خطأ في حذف الحالة الصحية: {e}")
        return False

def get_student_health_conditions(student_id):
    """الحصول على الحالات الصحية للطالب"""
    student_id_str = str(student_id).strip()
    return st.session_state.student_health_conditions.get(student_id_str, [])

# ===== وظائف مساعدة للصفحات =====
def get_bus_students(bus_number):
    """الحصول على قائمة طلاب الباص"""
    return st.session_state.students_df[
        st.session_state.students_df["bus"] == bus_number
    ]

def get_today_attendance_for_bus(bus_number):
    """الحصول على حضور اليوم لطلاب الباص"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.attendance_df.empty:
        return pd.DataFrame()
    
    bus_students = get_bus_students(bus_number)
    bus_student_ids = bus_students["id"].astype(str).tolist()
    
    today_attendance = st.session_state.attendance_df[
        (st.session_state.attendance_df["date"] == today) & 
        (st.session_state.attendance_df["id"].astype(str).isin(bus_student_ids))
    ]
    
    return today_attendance

def get_bus_schedule(bus_number):
    """جدول الباص"""
    schedules = {
        "1": {"morning": "07:00 AM", "evening": "02:30 PM"},
        "2": {"morning": "07:15 AM", "evening": "02:45 PM"}, 
        "3": {"morning": "07:30 AM", "evening": "03:00 PM"}
    }
    return schedules.get(bus_number, {"morning": "07:00 AM", "evening": "02:30 PM"})

def get_driver_contact(bus_number):
    """معلومات السائق"""
    drivers = {
        "1": {"name": "محمد أحمد", "phone": "0501111111"},
        "2": {"name": "علي حسن", "phone": "0502222222"},
        "3": {"name": "خالد سعيد", "phone": "0503333333"}
    }
    return drivers.get(bus_number, {"name": "غير محدد", "phone": "غير محدد"})

# ===== المساعد الذكي البسيط =====
def smart_ai_assistant():
    """المساعد الذكي البسيط"""
    st.header(t("ai_assistant"))
    
    # تهيئة المحادثة إذا كانت فارغة
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [{
            "role": "assistant", 
            "content": t("ai_welcome")
        }]
    
    # عرض المحادثة
    for msg in st.session_state.chat_messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #00b4d8, #0077b6);
                    color: white;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0;
                    border: none;
                    box-shadow: 0 4px 6px rgba(0, 180, 216, 0.3);
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("user"):
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #2a9d8f, #264653);
                    color: white;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0;
                    border: none;
                    box-shadow: 0 4px 6px rgba(42, 157, 143, 0.3);
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # الأسئلة السريعة
    st.subheader(t("ai_questions"))
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 " + t("student") + "?", use_container_width=True, key="ai_btn1"):
            handle_ai_question("كيف أسجل حضور؟" if st.session_state.lang == "ar" else "How do I register attendance?")
    with col2:
        if st.button("🔧 " + t("error"), use_container_width=True, key="ai_btn2"):
            handle_ai_question("مشكلة في التسجيل" if st.session_state.lang == "ar" else "Registration problem")
    with col3:
        if st.button("📧 " + t("contact_developer"), use_container_width=True, key="ai_btn3"):
            handle_ai_question("أريد التواصل مع المطور" if st.session_state.lang == "ar" else "I want to contact the developer")
    
    # إدخال السؤال
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.text_input(t("ai_placeholder"), key="ai_input")
    with col2:
        if st.button(t("ai_send"), use_container_width=True, key="ai_send"):
            if user_question:
                handle_ai_question(user_question)
            else:
                st.warning("يرجى كتابة سؤال أولاً" if st.session_state.lang == "ar" else "Please write a question first")

def handle_ai_question(question):
    """معالجة أسئلة المساعد الذكي"""
    # إضافة سؤال المستخدم
    st.session_state.chat_messages.append({
        "role": "user",
        "content": question
    })
    
    # توليد رد ذكي حسب اللغة
    if st.session_state.lang == "ar":
        responses = {
            "كيف أسجل حضور؟": """
**🎯 لتسجيل الحضور:**

1. **انتقل إلى صفحة الطالب** 📄
2. **أدخل رقم الوزارة** 🔢  
3. **اختر 'سأحضر اليوم' أو 'لن أحضر'** ✅ ❌
4. **انقر على زر التسجيل** 🚀

⏰ **نصيحة ذهبية:** سجل حضورك قبل الساعة 8 صباحاً لضمان أفضل خدمة!
            """,
            "مشكلة في التسجيل": """
**🔧 حلول سريعة للمشاكل:**

1. **تأكد من رقم الوزارة** 📋
2. **تحقق من اتصال الإنترنت** 🌐
3. **جرب تحديث الصفحة** 🔄
4. **إذا استمرت المشكلة، اتصل بالإدارة** 📞

🆘 **رقم الإدارة للطوارئ:** 025555555
            """,
            "أريد التواصل مع المطور": """
**📧 للتواصل مع المطور:**

**البريد الإلكتروني:** 📨 eyadmustafaali99@gmail.com

💡 **نصيحة:** يمكنك أيضاً استخدام نموذج التواصل في تبويب 'حول النظام' للحصول على رد أسرع!
            """,
            "default": """
**🤗 شكراً لسؤالك!**

أنا هنا لمساعدتك في:

🎓 **تسجيل الحضور** - شرح مفصل لكيفية التسجيل
🚍 **متابعة الباص** - معلومات عن المواعيد والمسارات  
🔧 **حل المشكلات التقنية** - استكشاف الأخطاء وإصلاحها
📞 **التواصل مع المطور** - رابط مباشر للدعم

💬 **اختر أحد الأسئلة السريعة أعلاه أو اشرح لي مشكلتك بالتفصيل لمزيد من المساعدة المتخصصة.**
            """
        }
    else:
        responses = {
            "How do I register attendance?": """
**🎯 To register attendance:**

1. **Go to Student Page** 📄
2. **Enter your ministry number** 🔢  
3. **Choose 'I will attend today' or 'I will not attend'** ✅ ❌
4. **Click the register button** 🚀

⏰ **Golden tip:** Register before 8 AM for best service!
            """,
            "Registration problem": """
**🔧 Quick solutions:**

1. **Check your ministry number** 📋
2. **Check internet connection** 🌐
3. **Try refreshing the page** 🔄
4. **If problem persists, contact admin** 📞

🆘 **Emergency admin number:** 025555555
            """,
            "I want to contact the developer": """
**📧 To contact the developer:**

**Email:** 📨 eyadmustafaali99@gmail.com

💡 **Tip:** You can also use the contact form in the 'About' tab for faster response!
            """,
            "default": """
**🤗 Thank you for your question!**

I'm here to help you with:

🎓 **Attendance registration** - Detailed guide
🚍 **Bus tracking** - Schedule and routes  
🔧 **Technical issues** - Troubleshooting
📞 **Contact developer** - Direct support link

💬 **Choose one of the quick questions above or describe your problem in detail for more specialized help.**
            """
        }
    
    response = responses.get(question, responses["default"])
    
    # إضافة رد المساعد
    st.session_state.chat_messages.append({
        "role": "assistant", 
        "content": response
    })
    
    save_data()
    st.rerun()

# ===== التواصل مع المطور =====
def contact_developer():
    """نموذج التواصل مع المطور"""
    st.header(t("contact_title"))
    
    with st.form("contact_form"):
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #00b4d8, #0077b6);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.3);
        '>
            <h3>{t("contact_form")}</h3>
            <p>{t("contact_title")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(f"**{t('contact_name')}**", key="contact_name", 
                               placeholder=t("contact_name"))
            email = st.text_input(f"**{t('contact_email')}**", key="contact_email",
                                placeholder="example@email.com")
        
        with col2:
            subject = st.selectbox(f"**{t('contact_subject')}**", [
                t("contact_subject") + " - " + x for x in ["Technical Issue", "Improvement Suggestion", "Support", "General Inquiry"]
            ], key="contact_subject")
        
        message = st.text_area(f"**{t('contact_message')}**", height=150, key="contact_message",
                             placeholder=t("contact_message"))
        
        submitted = st.form_submit_button(f"**{t('contact_success')}**", use_container_width=True, key="contact_submit")
        if submitted:
            if name and email and message:
                # حفظ الرسالة
                contact_data = {
                    "name": name,
                    "email": email, 
                    "subject": subject,
                    "message": message,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                try:
                    contact_file = DATA_DIR / "contact_messages.json"
                    messages = []
                    if contact_file.exists():
                        with open(contact_file, "r", encoding="utf-8") as f:
                            messages = json.load(f)
                    
                    messages.append(contact_data)
                    
                    with open(contact_file, "w", encoding="utf-8") as f:
                        json.dump(messages, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"""
                    **{t('contact_success')}**
                    
                    **📧 {t('contact_info') if st.session_state.lang == 'ar' else 'Contact Info'}:**
                    - **{t('contact_email')}:** eyadmustafaali99@gmail.com
                    - **{t('contact_subject')}:** {subject}
                    """)
                    
                    st.session_state.contact_submitted = True
                    
                except Exception as e:
                    st.error(f"حدث خطأ في حفظ الرسالة: {e}")
                    
            else:
                st.error(f"**❌ {t('error') if st.session_state.lang == 'ar' else 'Please fill all required fields'}**")

# ===== التصميم المحسن والمحدث =====
def apply_enhanced_styles():
    """تطبيق التصميم المحسن بالألوان الجديدة"""
    
    # ألوان جديدة ومحسنة
    primary_color = "#00b4d8"  # أزرق فاتح
    secondary_color = "#0077b6"  # أزرق غامق
    accent_color = "#2a9d8f"  # أخضر مزرق
    warning_color = "#e9c46a"  # أصفر
    danger_color = "#e76f51"  # برتقالي محمر
    success_color = "#2a9d8f"  # أخضر
    
    if st.session_state.theme == "dark":
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* تحسينات عامة */
        .stMarkdown, .stText, .stTitle {{
            color: #ffffff !important;
        }}
        
        /* الهيدر الرئيسي */
        .main-header {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            border: none;
            box-shadow: 0 10px 30px rgba(0, 180, 216, 0.3);
            position: relative;
            overflow: hidden;
            animation: gradientShift 10s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        .main-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }}
        
        /* البطاقات الإحصائية */
        .metric-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 30px rgba(0, 180, 216, 0.3);
            background: rgba(255, 255, 255, 0.15);
            border-color: {primary_color};
        }}
        
        /* أزرار التنقل */
        .nav-button {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin: 0.2rem;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        }}
        
        .nav-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 180, 216, 0.4);
        }}
        
        /* بطاقات المميزات */
        .feature-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px) scale(1.02);
            background: rgba(255, 255, 255, 0.15);
            border-color: {primary_color};
            box-shadow: 0 15px 30px rgba(0, 180, 216, 0.2);
        }}
        
        /* الأزرار العامة */
        .stButton > button {{
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 180, 216, 0.4);
        }}
        
        /* علامات التبويب */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            padding: 5px;
            border-radius: 15px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: rgba(255,255,255,0.1);
            border-radius: 10px;
            gap: 1px;
            padding: 10px 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            border-color: transparent;
        }}
        
        /* جداول البيانات */
        .dataframe {{
            width: 100%;
            border-collapse: collapse;
            border-radius: 15px;
            overflow: hidden;
        }}
        
        .dataframe th {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        .dataframe td {{
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .dataframe tr:hover td {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        /* صناديق الإدخال */
        .stTextInput>div>div>input {{
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.2);
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }}
        
        .stTextInput>div>div>input:focus {{
            border-color: {primary_color};
            box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.2);
            background: rgba(255, 255, 255, 0.15);
        }}
        
        /* القوائم المنسدلة */
        .stSelectbox>div>div {{
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.2);
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }}
        
        /* تأثيرات الحركة */
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        /* تحسينات للشاشات الصغيرة */
        @media (max-width: 768px) {{
            .title {{
                font-size: 2rem;
            }}
            .metric-card {{
                padding: 1rem;
            }}
        }}
        
        /* تصميم نجوم التقييم */
        .rating-stars {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
            direction: ltr;
        }}
        
        .star {{
            font-size: 40px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: #ffd700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }}
        
        .star:hover {{
            transform: scale(1.2) rotate(5deg);
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
        }}
        
        .star.active {{
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
            animation: starPulse 1s infinite;
        }}
        
        @keyframes starPulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        /* تصميم الإشعارات */
        .notification {{
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            background: rgba(255, 255, 255, 0.1);
            border-left: 4px solid {primary_color};
            animation: slideIn 0.5s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        /* تصميم الفوتر */
        .footer {{
            background: linear-gradient(135deg, rgba(0, 180, 216, 0.1), rgba(0, 119, 182, 0.1));
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-top: 3rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e6f3ff 50%, #d9eeff 100%);
            color: #1e293b;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* تحسينات عامة */
        .stMarkdown, .stText, .stTitle {{
            color: #1e293b !important;
        }}
        
        /* الهيدر الرئيسي */
        .main-header {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            border: none;
            box-shadow: 0 10px 30px rgba(0, 180, 216, 0.2);
            position: relative;
            overflow: hidden;
            animation: gradientShift 10s ease infinite;
        }}
        
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        .main-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }}
        
        /* البطاقات الإحصائية */
        .metric-card {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0;
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 5px 15px rgba(0, 180, 216, 0.1);
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 30px rgba(0, 180, 216, 0.2);
            background: rgba(255, 255, 255, 1);
            border-color: {primary_color};
        }}
        
        /* أزرار التنقل */
        .nav-button {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin: 0.2rem;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        }}
        
        .nav-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 180, 216, 0.3);
        }}
        
        /* بطاقات المميزات */
        .feature-card {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 180, 216, 0.1);
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 30px rgba(0, 180, 216, 0.2);
            background: rgba(255, 255, 255, 1);
            border-color: {primary_color};
        }}
        
        /* الأزرار العامة */
        .stButton > button {{
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 180, 216, 0.3);
        }}
        
        /* علامات التبويب */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(255, 255, 255, 0.5);
            padding: 5px;
            border-radius: 15px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 10px;
            gap: 1px;
            padding: 10px 20px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
            color: #1e293b;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            border-color: transparent;
        }}
        
        /* جداول البيانات */
        .dataframe {{
            width: 100%;
            border-collapse: collapse;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 180, 216, 0.1);
        }}
        
        .dataframe th {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        .dataframe td {{
            padding: 10px;
            border-bottom: 1px solid #e2e8f0;
            background: white;
        }}
        
        .dataframe tr:hover td {{
            background: #f8f9fa;
        }}
        
        /* صناديق الإدخال */
        .stTextInput>div>div>input {{
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            background: white;
            color: #1e293b;
        }}
        
        .stTextInput>div>div>input:focus {{
            border-color: {primary_color};
            box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.2);
        }}
        
        /* القوائم المنسدلة */
        .stSelectbox>div>div {{
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            background: white;
            color: #1e293b;
        }}
        
        /* تأثيرات الحركة */
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        /* تحسينات للشاشات الصغيرة */
        @media (max-width: 768px) {{
            .title {{
                font-size: 2rem;
            }}
            .metric-card {{
                padding: 1rem;
            }}
        }}
        
        /* تصميم نجوم التقييم */
        .rating-stars {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
            direction: ltr;
        }}
        
        .star {{
            font-size: 40px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: #ffd700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }}
        
        .star:hover {{
            transform: scale(1.2) rotate(5deg);
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
        }}
        
        .star.active {{
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
            animation: starPulse 1s infinite;
        }}
        
        @keyframes starPulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        /* تصميم الإشعارات */
        .notification {{
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            background: white;
            border-left: 4px solid {primary_color};
            box-shadow: 0 5px 15px rgba(0, 180, 216, 0.1);
            animation: slideIn 0.5s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        /* تصميم الفوتر */
        .footer {{
            background: linear-gradient(135deg, rgba(0, 180, 216, 0.1), rgba(0, 119, 182, 0.1));
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-top: 3rem;
            border: 1px solid rgba(0, 180, 216, 0.2);
        }}
        </style>
        """, unsafe_allow_html=True)

apply_enhanced_styles()

# ===== نظام التقييم المحسن بالنجوم التفاعلية =====
def show_rating_system_tab():
    """نظام التقييم المحسن بالنجوم التفاعلية"""
    st.subheader(f"⭐ {t('rating_system')}")
    
    # إحصائيات التقييمات
    avg_rating, total_ratings = get_average_rating()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # عرض متوسط التقييم مع تصميم محسن
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 {t('average_rating')}</h4>
            <h1 style="color: #f59e0b; text-align: center; font-size: 3rem;">{avg_rating:.1f}</h1>
            <div style="text-align: center; font-size: 2rem; margin: 0.5rem 0; color: #ffd700;">
                {"⭐" * int(avg_rating) if avg_rating > 0 else ""}
                {"☆" * (5 - int(avg_rating))}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 {t('total_ratings')}</h4>
            <h2 style="color: {primary_color}; text-align: center; font-size: 3rem;">{total_ratings}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(f"💬 {t('rate_app')}")
    
    # نظام النجوم التفاعلي باستخدام HTML/CSS/JavaScript
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <p style="font-size: 1.2rem; color: #666;">{t('click_stars')}</p>
        <div class="rating-stars" id="rating-stars">
            <span class="star" onclick="setRating(1)" id="star1">☆</span>
            <span class="star" onclick="setRating(2)" id="star2">☆</span>
            <span class="star" onclick="setRating(3)" id="star3">☆</span>
            <span class="star" onclick="setRating(4)" id="star4">☆</span>
            <span class="star" onclick="setRating(5)" id="star5">☆</span>
        </div>
        <p style="font-size: 1.1rem; color: #666; margin-top: 10px;" id="rating-text">
            {t('select_rating')}
        </p>
    </div>
    
    <script>
    let currentRating = 0;
    
    function setRating(rating) {{
        currentRating = rating;
        
        // تحديث مظهر النجوم
        for (let i = 1; i <= 5; i++) {{
            const star = document.getElementById('star' + i);
            if (i <= rating) {{
                star.innerHTML = '⭐';
                star.classList.add('active');
            }} else {{
                star.innerHTML = '☆';
                star.classList.remove('active');
            }}
        }}
        
        // تحديث النص
        const ratingText = document.getElementById('rating-text');
        const ratingMessages = [
            '{t("poor")}',
            '{t("fair")}',
            '{t("good")}',
            '{t("very_good")}',
            '{t("excellent")}'
        ];
        ratingText.innerHTML = `${{ratingMessages[rating-1]}} ({{rating}}/5)`;
        
        // تخزين التقييم في sessionStorage
        sessionStorage.setItem('selectedRating', rating);
    }}
    
    // استعادة التقييم السابق إذا وجد
    const savedRating = sessionStorage.getItem('selectedRating');
    if (savedRating) {{
        setRating(parseInt(savedRating));
    }}
    </script>
    """, unsafe_allow_html=True)
    
    # حقل التعليق
    comment = st.text_area(
        f"**{t('your_comment')}**",
        placeholder=t("your_comment"),
        height=100,
        key="rating_comment"
    )
    
    # أزرار التقييم
    col_submit, col_reset, col_space = st.columns([2, 1, 3])
    
    with col_submit:
        if st.button(f"**🚀 {t('submit_rating')}**", use_container_width=True, key="submit_rating"):
            # الحصول على التقييم من sessionStorage عبر JavaScript
            st.markdown("""
            <script>
            const rating = sessionStorage.getItem('selectedRating');
            if (rating) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'rating_value';
                input.value = rating;
                document.body.appendChild(input);
                
                // إرسال النموذج
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '';
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }
            </script>
            """, unsafe_allow_html=True)
            
            # استخدام st.session_state لتخزين التقييم مؤقتاً
            if st.session_state.temp_rating > 0:
                if add_rating(st.session_state.temp_rating, comment):
                    st.success(t("rating_success"))
                    st.balloons()
                    st.session_state.temp_rating = 0
                    st.rerun()
                else:
                    st.error(f"❌ {t('error')}")
            else:
                st.warning(f"⚠️ {t('select_rating')}")
    
    with col_reset:
        if st.button(f"**🔄 {t('reset') if st.session_state.lang == 'ar' else 'Reset'}**", use_container_width=True):
            st.markdown("""
            <script>
            sessionStorage.removeItem('selectedRating');
            for (let i = 1; i <= 5; i++) {
                const star = document.getElementById('star' + i);
                star.innerHTML = '☆';
                star.classList.remove('active');
            }
            document.getElementById('rating-text').innerHTML = 'اختر عدد النجوم';
            </script>
            """, unsafe_allow_html=True)
            st.session_state.temp_rating = 0
            st.rerun()
    
    # عرض آخر التقييمات
    if not st.session_state.ratings_df.empty:
        st.markdown("---")
        st.subheader(f"📝 {t('latest_ratings')}")
        
        latest_ratings = st.session_state.ratings_df.tail(5).iloc[::-1]
        for idx, rating in latest_ratings.iterrows():
            stars_display = "⭐" * int(rating["rating"]) + "☆" * (5 - int(rating["rating"]))
            comment_display = rating["comment"] if pd.notna(rating["comment"]) and str(rating["comment"]).strip() else ""
            
            st.markdown(f"""
            <div class="notification" style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.2rem; color: #ffd700;">{stars_display}</span>
                    <small style="opacity: 0.7; color: #666;">{rating['timestamp'].split()[0]}</small>
                </div>
                {f"<p style='margin: 10px 0 0 0; color: #666; font-style: italic;'>{comment_display}</p>" if comment_display else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"ℹ️ {t('no_ratings_yet')}")

# ===== الواجهة الرئيسية المحسنة =====
def main():
    """الواجهة الرئيسية للتطبيق"""
    
    # الهيدر الرئيسي
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        stats = calculate_attendance_stats()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t('attendance_rate') if st.session_state.lang == 'ar' else 'Attendance Rate'}</h3>
            <h1 style="color: #2a9d8f; margin: 0.5rem 0;">{stats['percentage']:.1f}%</h1>
            <p style="opacity: 0.8; margin: 0;">{stats['coming']}/{stats['total']} {t('student') if st.session_state.lang == 'ar' else 'students'}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="main-header">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">{t('title')}</h1>
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem; opacity: 0.9;">{t('subtitle')}</h3>
            <p style="font-size: 1.1rem; opacity: 0.8; line-height: 1.6;">{t('description')}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        col3a, col3b = st.columns(2)
        with col3a:
            # زر تغيير الثيم
            theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
            if st.button(theme_icon, use_container_width=True, key="theme_toggle"):
                toggle_theme()
        with col3b:
            # زر تغيير اللغة
            if st.button("🌐", use_container_width=True, key="lang_toggle"):
                toggle_language()

    # شريط التنقل
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    pages = [
        (t("student"), "student"),
        (t("driver"), "driver"), 
        (t("parents"), "parents"),
        (t("admin"), "admin"),
        (t("about"), "about")
    ]

    nav_cols = st.columns(len(pages))
    for i, (name, page_key) in enumerate(pages):
        with nav_cols[i]:
            is_active = st.session_state.page == page_key
            if st.button(name, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state.page = page_key
                st.rerun()

    st.markdown("---")

    # عرض المحتوى حسب الصفحة المختارة
    if st.session_state.page == "student":
        show_student_page()
    elif st.session_state.page == "driver":
        show_driver_page()
    elif st.session_state.page == "parents":
        show_parents_page()
    elif st.session_state.page == "admin":
        show_admin_page()
    elif st.session_state.page == "about":
        show_about_page()

    # الفوتر المحسن
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <h4 style="color: {primary_color}; margin-bottom: 0.5rem;">🚍 {t('footer')}</h4>
        <p style="opacity: 0.8; margin-bottom: 0.5rem;">{t('rights')}</p>
        <p style="font-size: 0.9rem; opacity: 0.7; line-height: 1.5;">{t('team')}</p>
        <div style="margin-top: 1rem;">
            <small>📧 {t('contact_developer')}: <a href="mailto:eyadmustafaali99@gmail.com" style="color: {primary_color};">eyadmustafaali99@gmail.com</a></small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== صفحات التطبيق المحسنة (مع الحفاظ على الوظائف السابقة) =====
def show_student_page():
    """صفحة الطالب"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        '>
            <h2>🎓 {t('student_title')}</h2>
            <p>{t('student_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        student_id = st.text_input(
            f"**{t('student_id')}**",
            placeholder=t('student_id_placeholder'),
            key="student_id_input"
        )
        
        if student_id:
            student_info = st.session_state.students_df[
                st.session_state.students_df["id"].astype(str) == student_id.strip()
            ]
            
            if not student_info.empty:
                student = student_info.iloc[0]
                
                st.success(f"**🎓 {t('student_name')}: {student['name']}**")
                
                # معلومات الطالب في بطاقات جميلة
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📚 {t('grade')}</h4>
                        <h2>{student['grade']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                with col_info2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>🚍 {t('bus')}</h4>
                        <h2>{student['bus']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # معلومات إضافية
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📞 {t('parent_phone')}</h4>
                    <p>{student['parent_phone']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                already_registered, current_status = has_student_registered_today(student_id)
                
                if already_registered:
                    status_icon = "✅" if current_status == "قادم" else "❌"
                    st.warning(f"""
                    **{status_icon} {t('already_registered')}**
                    
                    **{t('current_status')}:** {current_status}
                    """)
                    
                    if st.button(f"**🔄 {t('change_status')}**", use_container_width=True, key="change_status_btn"):
                        today = datetime.datetime.now().strftime("%Y-%m-%d")
                        st.session_state.attendance_df = st.session_state.attendance_df[
                            ~((st.session_state.attendance_df["id"].astype(str) == student_id.strip()) & 
                              (st.session_state.attendance_df["date"] == today))
                        ]
                        save_data()
                        st.success(t("reset_success"))
                        st.rerun()
                
                else:
                    st.info(f"**📋 {t('choose_status')}**")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"**✅ {t('coming')}**", use_container_width=True, key="coming_btn"):
                            now = register_attendance(student, "قادم")
                            st.balloons()
                            st.success(f"**🎉 {t('registered_success')}**")
                            add_notification(f"{t('student_name')} {student['name']} {t('registered_success')} {t('bus')} {student['bus']}")
                    with col_btn2:
                        if st.button(f"**❌ {t('not_coming')}**", use_container_width=True, key="not_coming_btn"):
                            now = register_attendance(student, "لن يحضر")
                            st.success(f"**🎉 {t('registered_success')}**")
                            add_notification(f"{t('student_name')} {student['name']} {t('not_coming')} {t('bus')} {student['bus']}")
            
            else:
                st.error(f"**❌ {t('not_found')}**")

    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {accent_color}, {secondary_color});
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(42, 157, 143, 0.2);
        '>
            <h3>📊 {t('stats_title')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stats = calculate_attendance_stats()
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>👥 {t('total_registered')}</h4>
            <h2 style="color: {primary_color};">{stats['total']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>✅ {t('expected_attendance')}</h4>
            <h2 style="color: {success_color};">{stats['coming']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 {t('attendance_rate')}</h4>
            <h2 style="color: {warning_color};">{stats['percentage']:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # آخر الإشعارات
        if st.session_state.notifications:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #e9c46a, #f4a261);
                color: white;
                padding: 1rem;
                border-radius: 15px;
                margin-top: 1rem;
                box-shadow: 0 4px 6px rgba(233, 196, 106, 0.2);
            '>
                <h4>🔔 {t('latest_ratings') if st.session_state.lang == 'ar' else 'Latest Notifications'}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for notification in st.session_state.notifications[-3:]:
                st.markdown(f"""
                <div class="notification">
                    <div style="display: flex; justify-content: space-between;">
                        <span>{notification['message']}</span>
                        <small style="opacity: 0.7;">{notification['time']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def show_driver_page():
    """صفحة السائق (مع الحفاظ على الوظائف السابقة)"""
    if not st.session_state.driver_logged_in:
        # واجهة تسجيل الدخول
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {primary_color}, {secondary_color});
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
            '>
                <h2>🚌 {t('driver_title')}</h2>
                <p>{t('driver_login')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            bus_number = st.selectbox(
                f"**{t('select_bus')}**",
                ["1", "2", "3"],
                key="driver_bus_select"
            )
            
            password = st.text_input(
                f"**{t('password')}**",
                type="password",
                placeholder=t('password_placeholder'),
                key="driver_password"
            )
            
            if st.button(f"**🚀 {t('login')}**", use_container_width=True, key="driver_login_btn"):
                if password == st.session_state.bus_passwords.get(bus_number, ""):
                    st.session_state.driver_logged_in = True
                    st.session_state.current_bus = bus_number
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error(t("login_error"))
        
        with col2:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {accent_color}, {secondary_color});
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 4px 6px rgba(42, 157, 143, 0.2);
            '>
                <h1>🚍</h1>
                <h3>{t('driver_title')}</h3>
                <p>{t('driver_login')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # لوحة التحكم بعد تسجيل الدخول
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {primary_color}, {secondary_color});
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
            '>
                <h2>🚌 {t('bus')} {st.session_state.current_bus}</h2>
                <p>{t('driver_title')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"**🔄 {t('refresh_data') if st.session_state.lang == 'ar' else 'Refresh'}**", use_container_width=True, key="refresh_driver"):
                st.rerun()
        
        with col3:
            if st.button(f"**🚪 {t('logout')}**", use_container_width=True, key="driver_logout"):
                st.session_state.driver_logged_in = False
                st.rerun()
        
        # إحصائيات سريعة
        bus_students = get_bus_students(st.session_state.current_bus)
        today_attendance = get_today_attendance_for_bus(st.session_state.current_bus)
        
        coming_count = len(today_attendance[today_attendance["status"] == "قادم"]) if not today_attendance.empty else 0
        total_count = len(bus_students)
        percentage = (coming_count / total_count * 100) if total_count > 0 else 0
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>👥 {t('total_students')}</h4>
                <h2 style="color: {primary_color};">{total_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>✅ {t('confirmed_attendance')}</h4>
                <h2 style="color: {success_color};">{coming_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📈 {t('attendance_percentage')}</h4>
                <h2 style="color: {warning_color};">{percentage:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # قائمة الطلاب مع الحالات الصحية
        st.subheader(f"📋 {t('student_list')}")
        
        if not bus_students.empty:
            # دمج بيانات الحضور والحالات الصحية
            student_data = []
            for _, student in bus_students.iterrows():
                registered, status = has_student_registered_today(student["id"])
                student_status = status if registered else t("status_not_registered")
                status_color = "🟢" if student_status == "قادم" else "🔴" if student_status == "لن يحضر" else "⚪"
                
                # الحصول على الحالات الصحية
                health_conditions = get_student_health_conditions(student["id"])
                health_icon = "🏥" if health_conditions else ""
                health_info = ""
                if health_conditions:
                    conditions_list = []
                    for condition in health_conditions:
                        if condition["type"] == t("chronic_disease"):
                            conditions_list.append(f"🏥 {condition['description']}")
                        elif condition["type"] == t("allergy"):
                            conditions_list.append(f"⚠️ {condition['description']}")
                        elif condition["type"] == t("injury"):
                            conditions_list.append(f"🩹 {condition['description']}")
                        else:
                            conditions_list.append(f"📋 {condition['description']}")
                    health_info = " | ".join(conditions_list)
                
                student_data.append({
                    t("student_name"): f"{health_icon} {student['name']}",
                    t("grade"): student['grade'],
                    t("status"): f"{status_color} {student_status}",
                    t("health_conditions"): health_info if health_info else t("no_health_conditions"),
                    t("student_id"): student["id"]
                })
            
            # عرض البيانات في جدول
            student_df = pd.DataFrame(student_data)
            st.dataframe(student_df, use_container_width=True, hide_index=True)
            
            # تسجيل حضور سريع
            st.subheader(f"📝 {t('register_attendance')}")
            col_id, col_action, col_submit = st.columns([2, 1, 1])
            
            with col_id:
                quick_student_id = st.text_input(t("student_id"), placeholder=t("student_id_placeholder"), key="quick_student_id")
            
            with col_action:
                quick_action = st.selectbox(t("status"), [t("coming"), t("not_coming")], key="quick_action")
            
            with col_submit:
                if st.button(f"**🚀 {t('save_changes')}**", use_container_width=True, key="quick_register"):
                    if quick_student_id:
                        student_info = st.session_state.students_df[
                            st.session_state.students_df["id"].astype(str) == quick_student_id.strip()
                        ]
                        
                        if not student_info.empty:
                            student = student_info.iloc[0]
                            action_text = t("coming") if quick_action == t("coming") else t("not_coming")
                            register_attendance(student, "قادم" if quick_action == t("coming") else "لن يحضر")
                            st.success(f"{t('registered_success')} {action_text} {t('student_name')} {student['name']}")
                            st.rerun()
                        else:
                            st.error(t("not_found"))
                    else:
                        st.warning(t("student_id") + " " + t("error"))
        else:
            st.info(f"**ℹ️ {t('no_students')}**")

def show_parents_page():
    """صفحة أولياء الأمور (مع الحفاظ على الوظائف السابقة)"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
        '>
            <h2>👨‍👩‍👧 {t('parents_title')}</h2>
            <p>{t('track_student')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        student_id = st.text_input(
            f"**🔍 {t('enter_student_id')}**",
            placeholder=t('parents_id_placeholder'),
            key="parent_student_id"
        )
        
        if student_id:
            student_info = st.session_state.students_df[
                st.session_state.students_df["id"].astype(str) == student_id.strip()
            ]
            
            if not student_info.empty:
                student = student_info.iloc[0]
                
                st.success(f"**🎓 {t('student_name')}: {student['name']}**")
                
                # معلومات الطالب الأساسية
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📚 {t('grade')}</h4>
                        <h3>{student['grade']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>🚍 {t('bus')}</h4>
                        <h3>{student['bus']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_info3:
                    registered, status = has_student_registered_today(student_id)
                    status_text = status if registered else t("status_not_registered")
                    status_icon = "✅" if status == "قادم" else "❌" if status == "لن يحضر" else "⏳"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 {t('today_status')}</h4>
                        <h3>{status_icon} {status_text}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                if registered:
                    today_data = st.session_state.attendance_df[
                        (st.session_state.attendance_df["id"].astype(str) == student_id.strip()) &
                        (st.session_state.attendance_df["date"] == datetime.datetime.now().strftime("%Y-%m-%d"))
                    ]
                    
                    if not today_data.empty:
                        latest_record = today_data.iloc[-1]
                        st.info(f"**⏰ {t('registration_time')}: {latest_record['time']}**")
                
                # قسم إدارة الحالات الصحية
                st.markdown("---")
                st.markdown(f"### 🏥 {t('health_management')}", unsafe_allow_html=True)
                
                # عرض الحالات الصحية الحالية
                health_conditions = get_student_health_conditions(student_id)
                
                if health_conditions:
                    st.markdown(f"**{t('student_health_info')}:**")
                    for i, condition in enumerate(health_conditions):
                        condition_icon = "🏥" if condition["type"] == t("chronic_disease") else "⚠️" if condition["type"] == t("allergy") else "🩹" if condition["type"] == t("injury") else "📋"
                        col_cond1, col_cond2 = st.columns([4, 1])
                        with col_cond1:
                            st.markdown(f"""
                            <div style="
                                background: #f0f8ff;
                                padding: 10px;
                                border-radius: 10px;
                                margin: 5px 0;
                                border-right: 5px solid {primary_color};
                            ">
                                <strong>{condition_icon} {condition['type']}:</strong> {condition['description']}
                                <br><small>📅 {t('added_date') if st.session_state.lang == 'ar' else 'Added'}: {condition['added_date']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_cond2:
                            if st.button(f"🗑️", key=f"delete_health_{i}"):
                                if delete_health_condition(student_id, i):
                                    st.success(t("health_info_updated"))
                                    st.rerun()
                else:
                    st.info(t("no_health_conditions"))
                
                # إضافة حالة صحية جديدة
                st.markdown(f"**{t('add_health_condition')}:**")
                
                col_type, col_desc, col_add = st.columns([2, 3, 1])
                
                with col_type:
                    condition_type = st.selectbox(
                        t("condition_type") if st.session_state.lang == 'ar' else "Condition Type",
                        [t("chronic_disease"), t("allergy"), t("injury"), t("other")],
                        key="condition_type"
                    )
                
                with col_desc:
                    condition_desc = st.text_input(
                        t("condition_description"),
                        placeholder=t("condition_description"),
                        key="condition_desc"
                    )
                
                with col_add:
                    if st.button(f"➕", key="add_condition_btn"):
                        if condition_desc:
                            if add_health_condition(student_id, condition_type, condition_desc):
                                st.success(t("health_info_updated"))
                                st.rerun()
                        else:
                            st.warning(t("condition_description") + " " + t("error"))
            
            else:
                st.error(f"**❌ {t('not_found')}**")
    
    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {accent_color}, {secondary_color});
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(42, 157, 143, 0.2);
        '>
            <h3>🚌 {t('bus_info')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if student_id and 'student_info' in locals() and not student_info.empty:
            student = student_info.iloc[0]
            bus_number = student["bus"]
            schedule = get_bus_schedule(bus_number)
            driver = get_driver_contact(bus_number)
            
            # جدول الباص
            st.markdown(f"""
            <div class="metric-card">
                <h4>⏰ {t('bus_schedule')}</h4>
                <p><strong>{t('morning_pickup')}:</strong> {schedule['morning']}</p>
                <p><strong>{t('evening_return')}:</strong> {schedule['evening']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # معلومات السائق
            st.markdown(f"""
            <div class="metric-card">
                <h4>📞 {t('driver_contact')}</h4>
                <p><strong>{t('contact_info') if st.session_state.lang == 'ar' else 'Driver Name'}:</strong> {driver['name']}</p>
                <p><strong>{t('contact_info') if st.session_state.lang == 'ar' else 'Phone'}:</strong> {driver['phone']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # موقع الباص
            st.markdown(f"""
            <div class="metric-card">
                <h4>📍 {t('bus_location')}</h4>
                <p><strong>{t('current_location')}:</strong> {t('current_location') if st.session_state.lang == 'ar' else 'On the way to school'}</p>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 10px; margin-top: 0.5rem;">
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">
                        🕒 {t('last_update') if st.session_state.lang == 'ar' else 'Last update'}: {datetime.datetime.now().strftime("%H:%M")}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_admin_page():
    """صفحة الإدارة (مع الحفاظ على الوظائف السابقة)"""
    if not st.session_state.admin_logged_in:
        # واجهة تسجيل الدخول
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {primary_color}, {secondary_color});
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
            '>
                <h2>🏫 {t('admin_title')}</h2>
                <p>{t('admin_login')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            password = st.text_input(
                f"**🔐 {t('admin_password')}**",
                type="password",
                placeholder=t('admin_password') + "...",
                key="admin_password_input"
            )
            
            if st.button(f"**🚀 {t('login')}**", use_container_width=True, key="admin_login_btn"):
                if password == st.session_state.admin_password:
                    st.session_state.admin_logged_in = True
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error(t("login_error"))
        
        with col2:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {accent_color}, {secondary_color});
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 4px 6px rgba(42, 157, 143, 0.2);
            '>
                <h1>🔒</h1>
                <h3>{t('admin_title')}</h3>
                <p>{t('admin_login')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # لوحة تحكم الإدارة
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, {primary_color}, {secondary_color});
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
            '>
                <h2>🏫 {t('admin_title')}</h2>
                <p>{t('system_stats')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"**🔄 {t('refresh_data') if st.session_state.lang == 'ar' else 'Refresh'}**", use_container_width=True, key="refresh_admin"):
                st.rerun()
        
        with col3:
            if st.button(f"**🚪 {t('logout')}**", use_container_width=True, key="admin_logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        # إحصائيات النظام
        st.subheader(f"📊 {t('system_stats')}")
        
        total_students = len(st.session_state.students_df)
        total_attendance = len(st.session_state.attendance_df)
        total_ratings = len(st.session_state.ratings_df)
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>👥 {t('students_count')}</h4>
                <h2 style="color: {primary_color};">{total_students}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📝 {t('attendance_records')}</h4>
                <h2 style="color: {success_color};">{total_attendance}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            avg_rating, rating_count = get_average_rating()
            st.markdown(f"""
            <div class="metric-card">
                <h4>⭐ {t('rating_system')}</h4>
                <h2 style="color: {warning_color};">{rating_count}</h2>
                <p>{t('average_rating')}: {avg_rating:.1f}/5</p>
            </div>
            """, unsafe_allow_html=True)
        
        # تبويبات إدارة الطلاب والإعدادات
        tab1, tab2, tab3 = st.tabs([t("manage_students"), t("system_actions") if st.session_state.lang == 'ar' else "Settings", t("export_data")])
        
        with tab1:
            # إدارة الطلاب
            st.subheader(f"👥 {t('manage_students')}")
            
            # إضافة طالب جديد
            with st.expander(f"➕ {t('add_student')}"):
                col_add1, col_add2 = st.columns(2)
                
                with col_add1:
                    new_id = st.text_input(t("student_id"), key="new_student_id")
                    new_name = st.text_input(t("student_name"), key="new_student_name")
                    new_grade = st.selectbox(t("select_grade"), ["6-A", "6-B", "7-A", "7-B", "8-A", "8-B", "8-C", "9-A", "9-B", "10-A", "10-B", "11-A", "11-B"], key="new_student_grade")
                
                with col_add2:
                    new_bus = st.selectbox(t("select_bus"), ["1", "2", "3"], key="new_student_bus")
                    new_phone = st.text_input(t("parent_phone_placeholder"), key="new_student_phone")
                
                if st.button(f"**➕ {t('add_student_button')}**", key="add_student_btn"):
                    if new_id and new_name and new_grade and new_bus and new_phone:
                        success, message = add_new_student(new_id, new_name, new_grade, new_bus, new_phone)
                        if success:
                            st.success(t("student_added_success"))
                            st.rerun()
                        elif message == "student_exists":
                            st.error(t("student_exists_error"))
                        else:
                            st.error(f"❌ {t('error')}: {message}")
                    else:
                        st.warning(f"⚠️ {t('error')}")
            
            # عرض وتعديل الطلاب
            st.subheader(f"📋 {t('student_list')}")
            
            if not st.session_state.students_df.empty:
                # حقل بحث
                search_term = st.text_input(f"🔍 {t('filter_data')}", key="student_search")
                
                if search_term:
                    filtered_students = st.session_state.students_df[
                        st.session_state.students_df["name"].str.contains(search_term, case=False) |
                        st.session_state.students_df["id"].astype(str).str.contains(search_term) |
                        st.session_state.students_df["grade"].str.contains(search_term, case=False)
                    ]
                else:
                    filtered_students = st.session_state.students_df
                
                # عرض البيانات مع ترميز UTF-8 صحيح
                display_df = filtered_students.copy()
                st.dataframe(display_df, use_container_width=True)
                
                # حذف طالب
                st.subheader(f"🗑️ {t('delete_student')}")
                delete_id = st.text_input(t("student_id") + " " + t("delete_student"), key="delete_student_id")
                
                if st.button(f"**🗑️ {t('delete_student')}**", key="delete_student_btn"):
                    if delete_id:
                        if str(delete_id).strip() in st.session_state.students_df["id"].astype(str).values:
                            if st.checkbox(f"⚠️ {t('delete_student_confirm')}"):
                                success, message = delete_student(delete_id)
                                if success:
                                    st.success(t("student_deleted_success"))
                                    st.rerun()
                                else:
                                    st.error(f"❌ {t('error')}: {message}")
                        else:
                            st.error(t("not_found"))
                    else:
                        st.warning(f"⚠️ {t('student_id')} {t('error')}")
            else:
                st.info(t("no_students") if st.session_state.lang == 'ar' else "No students registered")
        
        with tab2:
            # الإعدادات
            st.subheader(f"🔧 {t('system_actions')}")
            
            col_set1, col_set2 = st.columns(2)
            
            with col_set1:
                st.subheader(f"🔐 {t('change_admin_password')}")
                
                # كلمة مرور الإدارة
                st.markdown(f"**{t('admin_password')}**")
                new_admin_pass = st.text_input(t("new_password"), type="password", key="new_admin_pass")
                confirm_admin_pass = st.text_input(t("confirm_password") if st.session_state.lang == 'ar' else "Confirm Password", type="password", key="confirm_admin_pass")
                
                if st.button(f"**💾 {t('save_changes')}**", key="save_admin_pass"):
                    if new_admin_pass == confirm_admin_pass:
                        st.session_state.admin_password = new_admin_pass
                        save_data()
                        st.success(t("password_updated"))
                    else:
                        st.error(f"❌ {t('error')}")
                
                # كلمات مرور الباصات
                st.markdown(f"**{t('change_bus_password')}**")
                for bus_num in ["1", "2", "3"]:
                    new_pass = st.text_input(f"{t('bus')} {bus_num} {t('new_password')}", type="password", key=f"bus_pass_{bus_num}")
                    if new_pass:
                        st.session_state.bus_passwords[bus_num] = new_pass
                
                if st.button(f"**💾 {t('save_changes')}**", key="save_bus_pass"):
                    save_data()
                    st.success(t("password_updated"))
            
            with col_set2:
                st.subheader(f"🎨 {t('language')}")
                
                # اللغة
                current_lang = st.session_state.lang
                new_lang = st.selectbox("🌐", ["ar", "en"], index=0 if current_lang == "ar" else 1, key="language_select")
                if new_lang != current_lang:
                    st.session_state.lang = new_lang
                    save_data()
                    st.rerun()
                
                # الثيم
                current_theme = st.session_state.theme
                new_theme = st.selectbox("🎨", ["light", "dark"], index=0 if current_theme == "light" else 1, key="theme_select")
                if new_theme != current_theme:
                    st.session_state.theme = new_theme
                    save_data()
                    st.rerun()
        
        with tab3:
            # التقارير
            st.subheader(f"📊 {t('export_data')}")
            
            # تقرير الحضور اليومي
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            today_attendance = st.session_state.attendance_df[
                st.session_state.attendance_df["date"] == today
            ]
            
            col_rep1, col_rep2 = st.columns(2)
            
            with col_rep1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📅 {t('attendance_records')}</h4>
                    <p><strong>{t('date') if st.session_state.lang == 'ar' else 'Date'}:</strong> {today}</p>
                    <p><strong>{t('total_registered')}:</strong> {len(today_attendance)}</p>
                    <p><strong>{t('coming')}:</strong> {len(today_attendance[today_attendance['status'] == 'قادم'])}</p>
                    <p><strong>{t('not_coming')}:</strong> {len(today_attendance[today_attendance['status'] == 'لن يحضر'])}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_rep2:
                # تصدير البيانات
                st.markdown(f"**{t('export_data')}**")
                
                # تصدير بيانات الطلاب مع ترميز صحيح
                if st.button(f"📥 {t('export_data')} {t('students_count')}", key="export_students"):
                    csv = st.session_state.students_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label=f"📥 {t('download') if st.session_state.lang == 'ar' else 'Download'} CSV",
                        data=csv,
                        file_name=f"students_{today}.csv",
                        mime="text/csv",
                        key="download_students"
                    )
                
                # تصدير بيانات الحضور
                if st.button(f"📥 {t('export_data')} {t('attendance_records')}", key="export_attendance"):
                    csv = st.session_state.attendance_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label=f"📥 {t('download') if st.session_state.lang == 'ar' else 'Download'} CSV",
                        data=csv,
                        file_name=f"attendance_{today}.csv",
                        mime="text/csv",
                        key="download_attendance"
                    )
        
        # إجراءات النظام
        st.subheader(f"⚙️ {t('system_actions')}")
        
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if st.button(f"**🔄 {t('reset_data')}**", use_container_width=True, key="reset_data_btn"):
                if st.checkbox(f"⚠️ {t('delete_student_confirm')}"):
                    initialize_data()
                    st.success(t("data_reset_success"))
                    st.rerun()
        
        with col_act2:
            if st.button(f"**📥 {t('backup')}**", use_container_width=True, key="backup_btn"):
                if save_data():
                    st.success(t("backup_success"))
                else:
                    st.error(f"❌ {t('error')}")
        
        with col_act3:
            if st.button(f"**🗑️ {t('clear') if st.session_state.lang == 'ar' else 'Clear'}**", use_container_width=True, key="clear_attendance"):
                if st.checkbox(f"⚠️ {t('delete_student_confirm')}"):
                    st.session_state.attendance_df = pd.DataFrame(columns=[
                        "id", "name", "grade", "bus", "status", "time", "date"
                    ])
                    save_data()
                    st.success(t("data_reset_success"))
                    st.rerun()

def show_about_page():
    """صفحة حول النظام"""
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 180, 216, 0.2);
    '>
        <h2>ℹ️ {t('about_title')}</h2>
        <p>{t('about_description')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تبويبات الصفحة
    tab1, tab2, tab3, tab4 = st.tabs([t("features"), t("development_team"), t("rating_system"), t("contact_developer")])
    
    with tab1:
        # مميزات النظام
        st.subheader(f"🎯 {t('features')}")
        
        features = [
            ("🎓", t("feature1"), t("feature1_desc")),
            ("📍", t("feature2"), t("feature2_desc")),
            ("⭐", t("feature3"), t("feature3_desc")),
            ("🔔", t("feature4"), t("feature4_desc")),
            ("🎨", t("feature5"), t("feature5_desc")),
            ("🔒", t("feature6"), t("feature6_desc"))
        ]
        
        cols = st.columns(2)
        for i, (icon, title, desc) in enumerate(features):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display: flex; align-items: start; gap: 1rem;">
                        <div style="font-size: 2.5rem;">{icon}</div>
                        <div>
                            <h4 style="margin: 0 0 0.5rem 0; color: {primary_color};">{title}</h4>
                            <p style="margin: 0; opacity: 0.8; line-height: 1.5;">{desc}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # معلومات الفريق
            st.subheader(f"👥 {t('development_team')}")
            
            team_members = [
                ("🛠️", t("developer"), "إياد مصطفى"),
                ("👨‍🏫", t("supervisor") if st.session_state.lang == 'ar' else "Supervisor", t("supervisor") if st.session_state.lang == 'ar' else "Environmental Club")
            ]
            
            for icon, role, name in team_members:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                        <h4 style="margin: 0; color: {primary_color};">{role}</h4>
                        <p style="margin: 0.5rem 0 0 0; font-weight: bold; font-size: 1.1rem;">{name}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # معلومات الإصدار
            st.subheader(f"📋 {t('version_info')}")
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>📋 {t('version_info')}</h4>
                <p><strong>{t('version')}:</strong> 2.0 (Beta)</p>
                <p><strong>{t('release_date')}:</strong> 2025</p>
                <p><strong>{t('status_stable')}</strong></p>
                <p><strong>{t('last_update') if st.session_state.lang == 'ar' else 'Last Update'}:</strong> {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🤖 {t('ai_assistant')}</h4>
                <p>{t('ai_welcome')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # نظام التقييم المحسن
        show_rating_system_tab()
    
    with tab4:
        # المساعد الذكي والتواصل مع المطور
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"🤖 {t('ai_assistant')}")
            smart_ai_assistant()
        
        with col2:
            st.subheader(f"📧 {t('contact_developer')}")
            contact_developer()

# تشغيل التطبيق
if __name__ == "__main__":
    main()

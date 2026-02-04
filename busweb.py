import streamlit as st
import pandas as pd
import datetime
import json
import pickle
from pathlib import Path
import requests
import time

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

# ===== وظائف حفظ البيانات =====
def save_data():
    """حفظ جميع البيانات في الملفات"""
    try:
        # حفظ بيانات الطلاب
        if 'students_df' in st.session_state:
            with open(DATA_DIR / "students.pkl", "wb") as f:
                pickle.dump(st.session_state.students_df.to_dict(), f)
        
        # حفظ بيانات الحضور
        if 'attendance_df' in st.session_state:
            with open(DATA_DIR / "attendance.pkl", "wb") as f:
                pickle.dump(st.session_state.attendance_df.to_dict(), f)
        
        # حفظ بيانات التقييمات
        if 'ratings_df' in st.session_state:
            with open(DATA_DIR / "ratings.pkl", "wb") as f:
                pickle.dump(st.session_state.ratings_df.to_dict(), f)
        
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
            
    except Exception as e:
        st.error(f"خطأ في حفظ البيانات: {e}")

def load_data():
    """تحميل البيانات المحفوظة"""
    try:
        # تحميل بيانات الطلاب
        if (DATA_DIR / "students.pkl").exists():
            with open(DATA_DIR / "students.pkl", "rb") as f:
                students_data = pickle.load(f)
                st.session_state.students_df = pd.DataFrame(students_data)
        
        # تحميل بيانات الحضور
        if (DATA_DIR / "attendance.pkl").exists():
            with open(DATA_DIR / "attendance.pkl", "rb") as f:
                attendance_data = pickle.load(f)
                st.session_state.attendance_df = pd.DataFrame(attendance_data)
        
        # تحميل بيانات التقييمات
        if (DATA_DIR / "ratings.pkl").exists():
            with open(DATA_DIR / "ratings.pkl", "rb") as f:
                ratings_data = pickle.load(f)
                st.session_state.ratings_df = pd.DataFrame(ratings_data)
                
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
                
    except Exception as e:
        st.error(f"خطأ في تحميل البيانات: {e}")

# ===== البيانات الافتراضية =====
def initialize_data():
    if 'students_df' not in st.session_state:
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
    
    if 'attendance_df' not in st.session_state:
        st.session_state.attendance_df = pd.DataFrame(columns=[
            "id", "name", "grade", "bus", "status", "time", "date"
        ])
    
    if 'ratings_df' not in st.session_state:
        st.session_state.ratings_df = pd.DataFrame(columns=["rating", "comment", "timestamp"])

# تحميل البيانات المحفوظة
load_data()

# تهيئة البيانات
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
        
        # نظام التقييم
        "rating_system": "⭐ نظام التقييم المتطور",
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
        
        # الفوتر
        "footer": "🚍 نظام الباص الذكي - الإصدار 2.0",
        "rights": "© 2025 جميع الحقوق محفوظة",
        "team": "تم التطوير بواسطة: إياد مصطفى | التصميم: ايمن جلال | الإشراف: قسم النادي البيئي",
        
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
        
        # Rating System
        "rating_system": "⭐ Advanced Rating System",
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
        
        # Footer
        "footer": "🚍 Smart Bus System - Version 2.0",
        "rights": "© 2025 All Rights Reserved",
        "team": "Developed by: Eyad Mustafa | Design: Ayman Galal | Supervision: Environmental Club",
        
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
    st.session_state.notifications.append({
        "time": datetime.datetime.now().strftime("%H:%M"),
        "message": message
    })
    save_data()

def calculate_attendance_stats():
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
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
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
    new_rating = pd.DataFrame([{
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    if st.session_state.ratings_df.empty:
        st.session_state.ratings_df = new_rating
    else:
        st.session_state.ratings_df = pd.concat([
            st.session_state.ratings_df, new_rating
        ], ignore_index=True)
    
    save_data()

def get_average_rating():
    """حساب متوسط التقييم"""
    if st.session_state.ratings_df.empty:
        return 0, 0
    return st.session_state.ratings_df["rating"].mean(), len(st.session_state.ratings_df)

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    save_data()
    st.rerun()

def toggle_language():
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
        
        # حفظ البيانات
        save_data()
        return True, "success"
        
    except Exception as e:
        return False, str(e)

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
    st.header("🤖 المساعد الذكي")
    
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
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0;
                    border: none;
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("user"):
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0;
                    border: none;
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # الأسئلة السريعة
    st.subheader("💬 أسئلة سريعة")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 كيف أسجل حضور؟", use_container_width=True, key="ai_btn1"):
            handle_ai_question("كيف أسجل حضور؟")
    with col2:
        if st.button("🔧 مشكلة في التسجيل", use_container_width=True, key="ai_btn2"):
            handle_ai_question("مشكلة في التسجيل")
    with col3:
        if st.button("📧 تواصل مع المطور", use_container_width=True, key="ai_btn3"):
            handle_ai_question("أريد التواصل مع المطور")
    
    # إدخال السؤال
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.text_input("💭 اكتب سؤالك هنا...", key="ai_input")
    with col2:
        if st.button("🚀 إرسال", use_container_width=True, key="ai_send"):
            if user_question:
                handle_ai_question(user_question)
            else:
                st.warning("يرجى كتابة سؤال أولاً")

def handle_ai_question(question):
    """معالجة أسئلة المساعد الذكي"""
    # إضافة سؤال المستخدم
    st.session_state.chat_messages.append({
        "role": "user",
        "content": question
    })
    
    # توليد رد ذكي
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
    st.header("📧 التواصل مع المطور")
    
    with st.form("contact_form"):
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
        '>
            <h3>💼 نموذج التواصل مع المطور</h3>
            <p>سنكون سعداء بسماع رأيك ومساعدتك في حل أي مشكلة</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("**👤 الاسم الكامل**", key="contact_name", 
                               placeholder="أدخل اسمك الكامل هنا...")
            email = st.text_input("**📧 البريد الإلكتروني**", key="contact_email",
                                placeholder="example@email.com")
        
        with col2:
            subject = st.selectbox("**📋 نوع الرسالة**", [
                "🔧 مشكلة تقنية", "💡 اقتراح تحسين", 
                "🛠️ دعم فني", "❓ استفسار عام"
            ], key="contact_subject")
        
        message = st.text_area("**💬 الرسالة**", height=150, key="contact_message",
                             placeholder="اكتب رسالتك بالتفصيل هنا... شاركنا مشكلتك أو اقتراحك")
        
        if st.form_submit_button("**🚀 إرسال الرسالة**", use_container_width=True, key="contact_submit"):
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
                    
                    st.success("""
                    **✅ تم إرسال رسالتك بنجاح!**
                    
                    **📧 معلومات التواصل:**
                    - **البريد الإلكتروني:** eyadmustafaali99@gmail.com
                    - **وقت الاستجابة:** خلال 24 ساعة
                    """)
                    
                except Exception as e:
                    st.success("✅ تم حفظ رسالتك بنجاح وسيتم الرد عليك قريباً!")
                    
            else:
                st.error("**❌ يرجى ملء جميع الحقول المطلوبة**")

# ===== التصميم المحسن =====
def apply_enhanced_styles():
    """تطبيق التصميم المحسن"""
    if st.session_state.theme == "dark":
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            border: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .nav-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 0.2rem;
        }
        
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .stButton>button {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: rgba(255,255,255,0.1);
            border-radius: 10px 10px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(102, 126, 234, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2d3748;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            border: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0;
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            background: rgba(255, 255, 255, 1);
        }
        
        .nav-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 0.2rem;
        }
        
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            background: rgba(255, 255, 255, 1);
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .stButton>button {
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
        }
        
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 10px 10px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            border: 1px solid #e9ecef;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

apply_enhanced_styles()

# ===== الواجهة الرئيسية المحسنة =====
def main():
    """الواجهة الرئيسية للتطبيق"""
    
    # الهيدر الرئيسي
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        stats = calculate_attendance_stats()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 نسبة الحضور</h3>
            <h1 style="color: #10b981; margin: 0.5rem 0;">{stats['percentage']:.1f}%</h1>
            <p style="opacity: 0.8; margin: 0;">{stats['coming']}/{stats['total']} طالب</p>
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
            button_style = f"""
            <style>
            div[data-testid="stButton"] > button[kind="secondary"] {{
                background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if is_active else 'rgba(255,255,255,0.1)'} !important;
                color: {'white' if is_active else 'inherit'} !important;
                border: {'none' if is_active else '1px solid rgba(255,255,255,0.2)'} !important;
            }}
            </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
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
    <div style='
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
    '>
        <h4 style="color: #667eea; margin-bottom: 0.5rem;">🚍 {t('footer')}</h4>
        <p style="opacity: 0.8; margin-bottom: 0.5rem;">{t('rights')}</p>
        <p style="font-size: 0.9rem; opacity: 0.7; line-height: 1.5;">{t('team')}</p>
        <div style="margin-top: 1rem;">
            <small>📧 للدعم الفني: <a href="mailto:eyadmustafaali99@gmail.com" style="color: #667eea;">eyadmustafaali99@gmail.com</a></small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== صفحات التطبيق المحسنة =====
def show_student_page():
    """صفحة الطالب"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
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
                
                st.success(f"**🎓 تم العثور على الطالب: {student['name']}**")
                
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
                
                already_registered, current_status = has_student_registered_today(student_id)
                
                if already_registered:
                    st.warning(f"""
                    **✅ {t('already_registered')}**
                    
                    **الحالة الحالية:** {current_status}
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
                    with col_btn2:
                        if st.button(f"**❌ {t('not_coming')}**", use_container_width=True, key="not_coming_btn"):
                            now = register_attendance(student, "لن يحضر")
                            st.success(f"**🎉 {t('registered_success')}**")
            
            else:
                st.error(f"**❌ {t('not_found')}**")

    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            text-align: center;
        '>
            <h3>📊 {t('stats_title')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        stats = calculate_attendance_stats()
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>👥 {t('total_registered')}</h4>
            <h2 style="color: #667eea;">{stats['total']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>✅ {t('expected_attendance')}</h4>
            <h2 style="color: #10b981;">{stats['coming']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 {t('attendance_rate')}</h4>
            <h2 style="color: #f59e0b;">{stats['percentage']:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

def show_driver_page():
    """صفحة السائق"""
    if not st.session_state.driver_logged_in:
        # واجهة تسجيل الدخول
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
            '>
                <h2>🚌 {t('driver_title')}</h2>
                <p>سجل الدخول لعرض قائمة الطلاب ومتابعة الحضور</p>
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
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            '>
                <h1>🚍</h1>
                <h3>نظام متابعة الباص</h3>
                <p>ادخل بيانات الدخول للوصول إلى لوحة التحكم</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # لوحة التحكم بعد تسجيل الدخول
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
            '>
                <h2>🚌 باص رقم {st.session_state.current_bus}</h2>
                <p>لوحة متابعة الطلاب والحضور</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"**🔄 تحديث البيانات**", use_container_width=True, key="refresh_driver"):
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
                <h2 style="color: #667eea;">{total_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>✅ {t('confirmed_attendance')}</h4>
                <h2 style="color: #10b981;">{coming_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📈 {t('attendance_percentage')}</h4>
                <h2 style="color: #f59e0b;">{percentage:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # قائمة الطلاب
        st.subheader(f"📋 {t('coming_students')}")
        
        if not bus_students.empty:
            # دمج بيانات الحضور
            student_data = []
            for _, student in bus_students.iterrows():
                registered, status = has_student_registered_today(student["id"])
                student_status = status if registered else t("status_not_registered")
                status_color = "🟢" if student_status == "قادم" else "🔴" if student_status == "لن يحضر" else "⚪"
                
                student_data.append({
                    "الطالب": student["name"],
                    "الصف": student["grade"],
                    "الحالة": f"{status_color} {student_status}",
                    "رقم الوزارة": student["id"]
                })
            
            # عرض البيانات في جدول
            student_df = pd.DataFrame(student_data)
            st.dataframe(student_df, use_container_width=True, hide_index=True)
        else:
            st.info(f"**ℹ️ {t('no_students')}**")

def show_parents_page():
    """صفحة أولياء الأمور"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        '>
            <h2>👨‍👩‍👧 {t('parents_title')}</h2>
            <p>تابع حالة ابنك ومعلومات الباص</p>
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
                
                st.success(f"**🎓 تم العثور على الطالب: {student['name']}**")
                
                # معلومات الطالب
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
                    status_text = status if registered else "لم يسجل بعد"
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
            
            else:
                st.error(f"**❌ {t('not_found')}**")
    
    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            text-align: center;
        '>
            <h3>🚌 {t('bus_info')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if student_id and not student_info.empty:
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
                <p><strong>اسم السائق:</strong> {driver['name']}</p>
                <p><strong>رقم الهاتف:</strong> {driver['phone']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # موقع الباص
            st.markdown(f"""
            <div class="metric-card">
                <h4>📍 {t('bus_location')}</h4>
                <p><strong>{t('current_location')}:</strong> في الطريق إلى المدرسة</p>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 10px; margin-top: 0.5rem;">
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">
                        🕒 آخر تحديث: {datetime.datetime.now().strftime("%H:%M")}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_admin_page():
    """صفحة الإدارة"""
    if not st.session_state.admin_logged_in:
        # واجهة تسجيل الدخول
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
            '>
                <h2>🏫 {t('admin_title')}</h2>
                <p>سجل الدخول للإدارة المتقدمة للنظام</p>
            </div>
            """, unsafe_allow_html=True)
            
            password = st.text_input(
                f"**🔐 {t('admin_password')}**",
                type="password",
                placeholder="أدخل كلمة مرور الإدارة...",
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
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            '>
                <h1>🔒</h1>
                <h3>لوحة تحكم الإدارة</h3>
                <p>الدخول مخصص للمشرفين والمديرين فقط</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # لوحة تحكم الإدارة
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
            '>
                <h2>🏫 {t('admin_title')}</h2>
                <p>إدارة النظام والبيانات والإعدادات</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"**🔄 تحديث**", use_container_width=True, key="refresh_admin"):
                st.rerun()
        
        with col3:
            if st.button(f"**🚪 تسجيل الخروج**", use_container_width=True, key="admin_logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        # إحصائيات النظام
        st.subheader("📊 إحصائيات النظام")
        
        total_students = len(st.session_state.students_df)
        total_attendance = len(st.session_state.attendance_df)
        total_ratings = len(st.session_state.ratings_df)
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>👥 {t('students_count')}</h4>
                <h2 style="color: #667eea;">{total_students}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📝 {t('attendance_records')}</h4>
                <h2 style="color: #10b981;">{total_attendance}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            avg_rating, rating_count = get_average_rating()
            st.markdown(f"""
            <div class="metric-card">
                <h4>⭐ التقييمات</h4>
                <h2 style="color: #f59e0b;">{rating_count}</h2>
                <p>متوسط: {avg_rating:.1f}/5</p>
            </div>
            """, unsafe_allow_html=True)
        
        # إدارة الطلاب
        st.subheader("👥 إدارة الطلاب")
        
        # عرض قائمة الطلاب
        if not st.session_state.students_df.empty:
            st.dataframe(st.session_state.students_df, use_container_width=True)
        else:
            st.info("لا يوجد طلاب مسجلين في النظام")
        
        # إجراءات النظام
        st.subheader("⚙️ إجراءات النظام")
        
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if st.button("🔄 إعادة تعيين البيانات", use_container_width=True):
                initialize_data()
                st.success("تم إعادة تعيين البيانات بنجاح")
                st.rerun()
        
        with col_act2:
            if st.button("📥 نسخة احتياطية", use_container_width=True):
                save_data()
                st.success("تم إنشاء نسخة احتياطية بنجاح")
        
        with col_act3:
            if st.button("🔄 تحديث كلمات المرور", use_container_width=True):
                st.info("استخدم النموذج أدناه لتغيير كلمات المرور")

def show_about_page():
    """صفحة حول النظام"""
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    '>
        <h2>ℹ️ {t('about_title')}</h2>
        <p>{t('about_description')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تبويبات الصفحة
    tab1, tab2, tab3 = st.tabs(["🎯 المميزات", "👥 فريق التطوير", "📧 التواصل"])
    
    with tab1:
        # مميزات النظام
        st.subheader("🎯 المميزات الرئيسية")
        
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
                            <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{title}</h4>
                            <p style="margin: 0; opacity: 0.8; line-height: 1.5;">{desc}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # معلومات الفريق
            st.subheader("👥 فريق التطوير")
            
            team_members = [
                ("🛠️", t("developer"), "إياد مصطفى"),
                ("🎨", t("designer"), "ايمن جلال"),
                ("👨‍🏫", "المشرف", "قسم النادي البيئي")
            ]
            
            for icon, role, name in team_members:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                        <h4 style="margin: 0; color: #667eea;">{role}</h4>
                        <p style="margin: 0.5rem 0 0 0; font-weight: bold; font-size: 1.1rem;">{name}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # معلومات الإصدار ونظام التقييم
            st.subheader("📋 معلومات النظام")
            
            # معلومات الإصدار
            st.markdown(f"""
            <div class="metric-card">
                <h4>📋 {t('version_info')}</h4>
                <p><strong>{t('version')}:</strong> 2.0</p>
                <p><strong>{t('release_date')}:</strong> 2025</p>
                <p><strong>{t('status_stable')}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # نظام التقييم
            show_rating_system_tab()
    
    with tab3:
        # المساعد الذكي والتواصل مع المطور
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🤖 المساعد الذكي")
            smart_ai_assistant()
        
        with col2:
            st.subheader("📧 التواصل مع المطور")
            contact_developer()

def show_rating_system_tab():
    """نظام التقييم في تبويب منفصل"""
    st.subheader("⭐ نظام التقييم")
    
    # إحصائيات التقييمات
    avg_rating, total_ratings = get_average_rating()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 {t('average_rating')}</h4>
            <h1 style="color: #f59e0b; text-align: center;">{avg_rating:.1f}/5</h1>
            <div style="text-align: center; font-size: 1.5rem; margin: 0.5rem 0;">
                {"⭐" * int(avg_rating) if avg_rating > 0 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 {t('total_ratings')}</h4>
            <h2 style="color: #667eea; text-align: center;">{total_ratings}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # نموذج التقييم
    st.markdown("---")
    st.subheader("💬 شاركنا رأيك")
    
    rating = st.slider(
        f"**{t('your_rating')}**",
        1, 5, 5,
        key="rating_slider_about"
    )
    
    # عرض النجوم
    stars = "⭐" * rating + "☆" * (5 - rating)
    st.markdown(f"**{t('select_rating')}:** {stars}")
    
    # التعليق
    comment = st.text_area(
        f"**{t('your_comment')}**",
        placeholder="اكتب تعليقك هنا... (اختياري)",
        height=100,
        key="rating_comment_about"
    )
    
    if st.button(f"**🚀 {t('submit_rating')}**", use_container_width=True, key="submit_rating_about"):
        add_rating(rating, comment)
        st.success(t("rating_success"))
        st.balloons()
        st.rerun()
    
    # عرض آخر التقييمات
    if not st.session_state.ratings_df.empty:
        st.markdown("---")
        st.subheader("📝 آخر التقييمات")
        latest_ratings = st.session_state.ratings_df.tail(3)
        for _, rating in latest_ratings.iterrows():
            stars = "⭐" * rating["rating"] + "☆" * (5 - rating["rating"])
            st.markdown(f"""
            <div style='
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                border-left: 4px solid #f59e0b;
            '>
                <div style="display: flex; justify-content: between; align-items: center;">
                    <span style="font-size: 1.1rem;">{stars}</span>
                    <small style="opacity: 0.7;">{rating['timestamp'].split()[0]}</small>
                </div>
                {f"<p style='margin: 0.5rem 0 0 0; opacity: 0.8; font-style: italic;'>{rating['comment']}</p>" if pd.notna(rating['comment']) and rating['comment'].strip() else ""}
            </div>
            """, unsafe_allow_html=True)

# تشغيل التطبيق
if __name__ == "__main__":
    main()

"""
PriceWatch - Demo Dashboard
============================
واجهة Streamlit لعرض نتائج مراقبة الأسعار (نسخة تجريبية).
"""

import streamlit as st
import pandas as pd
from checker import check_all_prices, send_alert_email_demo, DEMO_PRODUCTS

st.set_page_config(page_title="PriceWatch - Demo", page_icon="📊", layout="wide")

# ============ CSS للدعم العربي RTL ============
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .main .block-container { direction: rtl; }
    [data-testid="stSidebar"] > div { direction: rtl; }
    #MainMenu, footer { visibility: hidden; }
    header { background-color: transparent; }
    [data-testid="stSlider"] { direction: ltr; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 PriceWatch — مراقب أسعار المنافسين")
st.caption("نسخة تجريبية (Demo) — البيانات محاكاة وليست سحب حقيقي")

st.info(
    "⚠️ هذه نسخة عرض تجريبية. البيانات هنا **محاكاة عشوائية** لتوضيح شكل النتائج. "
    "النسخة الكاملة تسحب الأسعار الفعلية من روابط المنتجات الحقيقية بشكل دوري تلقائي.",
    icon="ℹ️",
)

# ============ عرض المنتجات المراقبة ============
st.subheader("🛍️ المنتجات المراقبة")
products_df = pd.DataFrame(DEMO_PRODUCTS)[["name", "competitor"]]
products_df.columns = ["المنتج", "المنافس"]
st.dataframe(products_df, use_container_width=True, hide_index=True)

st.divider()

# ============ زر الفحص ============
if st.button("🔍 فحص الأسعار الآن", type="primary"):
    with st.spinner("جاري فحص الأسعار..."):
        results = check_all_prices()

    st.subheader("📋 نتائج الفحص")

    result_df = pd.DataFrame(results)
    display_df = result_df[
        ["name", "competitor", "old_price", "new_price", "change_pct", "status"]
    ].copy()
    display_df.columns = ["المنتج", "المنافس", "السعر السابق", "السعر الحالي", "نسبة التغيّر %", "الحالة"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # عرض التنبيهات
    changed = [r for r in results if r["status"] in ("ارتفع", "انخفض")]
    if changed:
        st.subheader("🔔 تنبيهات التغيّر")
        for r in changed:
            icon = "🔺" if r["status"] == "ارتفع" else "🔻"
            color = "red" if r["status"] == "ارتفع" else "green"
            st.markdown(
                f"{icon} **{r['name']}**: {r['old_price']} ← :{color}[{r['new_price']}] "
                f"({r['change_pct']}%)"
            )
    else:
        st.success("لا توجد تغييرات بالأسعار في هذا الفحص.")

    with st.expander("📧 معاينة الإشعار (محاكاة)"):
        st.text(send_alert_email_demo(results))

st.divider()

with st.expander("🔒 ما المتوفر في النسخة الكاملة؟"):
    st.markdown(
        """
        - **سحب حقيقي** للأسعار عبر Playwright من أي رابط منتج يضيفه العميل
        - **إضافة/حذف منتجات** ديناميكياً من الواجهة مباشرة
        - **إرسال إيميل فعلي** عند تغيّر الأسعار (SMTP بإعدادات العميل)
        - **جدولة تلقائية** (فحص دوري يومي/أسبوعي بدون تدخل يدوي)
        - **سجل تاريخي** للأسعار قابل للتصدير Excel
        - **معالجة أخطاء كاملة** (فشل اتصال، تغيّر تصميم الموقع، إلخ)
        """
    )

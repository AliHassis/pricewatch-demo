"""
PriceWatch - Demo Version
==========================
نسخة تجريبية مبسّطة لمراقبة أسعار المنتجات.

⚠️ ملاحظة: هذه نسخة Demo للعرض فقط.
- البيانات هنا محاكاة (simulated) وليست سحب حقيقي من مواقع فعلية
- في النسخة الكاملة: سحب حقيقي بـ Playwright + دعم أي رابط منتج يضيفه العميل
- في النسخة الكاملة: جدولة تلقائية (Task Scheduler / cron) لا يدوية

للاستفسار عن النسخة الكاملة، تواصل معي عبر منصة الخدمة.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

# مسار ملف تخزين آخر الأسعار المعروفة (بديل بسيط عن قاعدة بيانات)
DATA_FILE = Path("last_prices.json")

# منتجات تجريبية hardcoded — في النسخة الكاملة العميل يضيف روابطه الخاصة
DEMO_PRODUCTS = [
    {
        "id": "prod_1",
        "name": "منتج تجريبي - سماعات لاسلكية",
        "url": "https://example-store.com/product/1",
        "competitor": "متجر المنافس أ",
    },
    {
        "id": "prod_2",
        "name": "منتج تجريبي - ساعة ذكية",
        "url": "https://example-store.com/product/2",
        "competitor": "متجر المنافس ب",
    },
    {
        "id": "prod_3",
        "name": "منتج تجريبي - حقيبة ظهر",
        "url": "https://example-store.com/product/3",
        "competitor": "متجر المنافس ج",
    },
]


def simulate_price_fetch(product: dict) -> float:
    """
    محاكاة سحب السعر من موقع المنافس.

    ⚠️ Demo فقط: يرجّع رقم عشوائي قريب من سعر أساسي وهمي.
    النسخة الكاملة تستخدم Playwright للدخول الفعلي للصفحة
    واستخراج السعر الحقيقي عبر CSS/XPath selectors، مع معالجة:
    - انتظار تحميل العناصر الديناميكية (JS rendering)
    - إعادة المحاولة عند فشل الاتصال
    - كشف تغيّر تصميم الصفحة (selector breakage)
    """
    base_prices = {"prod_1": 149.0, "prod_2": 299.0, "prod_3": 89.0}
    base = base_prices.get(product["id"], 100.0)
    # تذبذب عشوائي بسيط لمحاكاة تغيّر السعر
    fluctuation = random.uniform(-0.08, 0.08)
    return round(base * (1 + fluctuation), 2)


def load_last_prices() -> dict:
    """تحميل آخر الأسعار المسجّلة من ملف JSON محلي."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_prices(prices: dict) -> None:
    """حفظ الأسعار الحالية كمرجع للمقارنة القادمة."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)


def check_all_prices() -> list[dict]:
    """
    يفحص كل المنتجات، يقارن بالسعر السابق، ويرجع تقرير بالتغييرات.

    Returns:
        قائمة بنتائج كل منتج مع حالة التغيّر (ارتفع/انخفض/ثابت)
    """
    last_prices = load_last_prices()
    current_prices = {}
    results = []

    for product in DEMO_PRODUCTS:
        new_price = simulate_price_fetch(product)
        old_price = last_prices.get(product["id"])
        current_prices[product["id"]] = new_price

        if old_price is None:
            status = "أول فحص"
            change_pct = 0.0
        else:
            change_pct = round(((new_price - old_price) / old_price) * 100, 2)
            if new_price > old_price:
                status = "ارتفع"
            elif new_price < old_price:
                status = "انخفض"
            else:
                status = "ثابت"

        results.append(
            {
                "name": product["name"],
                "competitor": product["competitor"],
                "old_price": old_price,
                "new_price": new_price,
                "change_pct": change_pct,
                "status": status,
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )

    save_prices(current_prices)
    return results


def send_alert_email_demo(results: list[dict]) -> str:
    """
    محاكاة إرسال إشعار إيميل عند تغيّر الأسعار.

    ⚠️ Demo فقط: يطبع الرسالة بدل إرسالها فعلياً.
    النسخة الكاملة تستخدم smtplib + إعدادات SMTP الخاصة بالعميل
    (Gmail App Password أو مزوّد بريد مؤسسي) لإرسال حقيقي.
    """
    changed = [r for r in results if r["status"] in ("ارتفع", "انخفض")]
    if not changed:
        return "لا توجد تغييرات بالأسعار — لن يُرسل إشعار."

    message_lines = ["📧 [محاكاة] تنبيه تغيّر أسعار:\n"]
    for r in changed:
        message_lines.append(
            f"- {r['name']}: {r['old_price']} → {r['new_price']} ({r['status']}, {r['change_pct']}%)"
        )
    return "\n".join(message_lines)


if __name__ == "__main__":
    print("🔍 جاري فحص الأسعار (Demo)...\n")
    results = check_all_prices()
    for r in results:
        print(f"{r['name']} | {r['status']} | {r['new_price']} SAR")

    print("\n" + send_alert_email_demo(results))

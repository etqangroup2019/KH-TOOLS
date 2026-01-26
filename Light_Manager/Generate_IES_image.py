"""
ملف توليد صور IES - محسن ومطور
=====================================

هذا الملف يقوم بتوليد صور مصغرة لملفات IES لاستخدامها في Blender.
تم تطوير الملف ليعمل مع أو بدون المكتبات الخارجية.

الميزات:
- يعمل بدون numpy و matplotlib (صور بديلة)
- يعمل مع numpy و matplotlib (صور عالية الجودة)
- معالجة شاملة للأخطاء
- رسائل واضحة للمستخدم

المطور: تم تحسينه لحل مشكلة الاستيراد في KH-Tools
"""

# استيراد المكتبات الأساسية
import os
import sys
import ctypes

# إعداد مسارات المكتبات مع تجنب التضارب
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.join(current_dir, "libs")

def setup_library_paths():
    """إعداد مسارات المكتبات مع تجنب التضارب"""
    if os.path.exists(libs_path):
        # إزالة المسارات المتضاربة أولاً
        paths_to_remove = []
        for path in sys.path:
            if 'Python313' in path and 'site-packages' in path:
                paths_to_remove.append(path)

        for path in paths_to_remove:
            try:
                sys.path.remove(path)
            except ValueError:
                pass

        # إضافة مجلد المكتبات المحلية في المقدمة
        if libs_path not in sys.path:
            sys.path.insert(0, libs_path)
            print(f"📚 تم إضافة مجلد المكتبات المحلية: {libs_path}")

        return True
    return False

# إعداد المسارات
local_libs_available = setup_library_paths()

# محاولة استيراد المكتبات مع معالجة شاملة للأخطاء
NUMPY_AVAILABLE = False
MATPLOTLIB_AVAILABLE = False
TKINTER_AVAILABLE = False

# محاولة استيراد numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    print("✅ numpy متوفر")
except (ImportError, PermissionError, OSError) as e:
    print(f"⚠️ numpy غير متوفر: {type(e).__name__}")
    try:
        # محاولة ثانية بدون المكتبات المحلية
        if libs_path in sys.path:
            sys.path.remove(libs_path)
        import numpy as np
        NUMPY_AVAILABLE = True
        print("✅ numpy متوفر (من النظام)")
    except:
        NUMPY_AVAILABLE = False
        print("⚠️ numpy غير متوفر نهائياً")

# محاولة استيراد matplotlib
try:
    import matplotlib
    # تعطيل GUI backend لتجنب مشاكل الصلاحيات
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    MATPLOTLIB_AVAILABLE = True
    print("✅ matplotlib متوفر")
except (ImportError, PermissionError, OSError) as e:
    print(f"⚠️ matplotlib غير متوفر: {type(e).__name__}")
    try:
        # محاولة ثانية بدون المكتبات المحلية
        if libs_path in sys.path:
            sys.path.remove(libs_path)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        MATPLOTLIB_AVAILABLE = True
        print("✅ matplotlib متوفر (من النظام)")
    except:
        MATPLOTLIB_AVAILABLE = False
        print("⚠️ matplotlib غير متوفر نهائياً")

# محاولة استيراد tkinter
try:
    from tkinter import Tk, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("⚠️ tkinter غير متوفر")

# التحقق من توفر جميع المكتبات المطلوبة
DEPENDENCIES_AVAILABLE = NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE

if DEPENDENCIES_AVAILABLE:
    print("🎉 جميع المكتبات المطلوبة متوفرة!")
else:
    print("⚠️ بعض المكتبات غير متوفرة - سيتم استخدام البدائل")

def install_dependencies_automatically():
    """محاولة تثبيت المكتبات تلقائياً"""
    try:
        import subprocess

        current_dir = os.path.dirname(os.path.abspath(__file__))
        libs_path = os.path.join(current_dir, "libs")

        # إنشاء مجلد المكتبات إذا لم يكن موجوداً
        if not os.path.exists(libs_path):
            os.makedirs(libs_path)

        # تثبيت المكتبات
        libraries = ["numpy", "matplotlib"]
        for lib in libraries:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "--target", libs_path, "--upgrade", lib
                ], check=True, capture_output=True, timeout=120)
                print(f"✅ تم تثبيت {lib} تلقائياً")
            except:
                print(f"⚠️ فشل في تثبيت {lib} تلقائياً")

        # إعادة تحميل المكتبات
        if libs_path not in sys.path:
            sys.path.insert(0, libs_path)

        return True
    except Exception as e:
        print(f"❌ خطأ في التثبيت التلقائي: {e}")
        return False

# def check_dependencies():
#     """التحقق من توفر المكتبات المطلوبة وإرجاع رسالة مناسبة"""
#     global NUMPY_AVAILABLE, MATPLOTLIB_AVAILABLE, DEPENDENCIES_AVAILABLE

#     missing_deps = []
#     available_deps = []

#     # إعادة فحص المكتبات بعد إضافة المسار المحلي
#     if not NUMPY_AVAILABLE:
#         try:
#             import numpy as np
#             NUMPY_AVAILABLE = True
#         except ImportError:
#             pass

#     if not MATPLOTLIB_AVAILABLE:
#         try:
#             import matplotlib.pyplot as plt
#             from matplotlib.colors import LinearSegmentedColormap
#             MATPLOTLIB_AVAILABLE = True
#         except ImportError:
#             pass

#     # تحديث حالة المكتبات
#     DEPENDENCIES_AVAILABLE = NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE

#     if not NUMPY_AVAILABLE:
#         missing_deps.append("numpy")
#     else:
#         available_deps.append("numpy")

#     if not MATPLOTLIB_AVAILABLE:
#         missing_deps.append("matplotlib")
#     else:
#         available_deps.append("matplotlib")

#     # التحقق من PIL كبديل
#     pil_available = False
#     try:
#         from PIL import Image
#         pil_available = True
#         available_deps.append("PIL")
#     except ImportError:
#         pass

#     if missing_deps:
#         message = f"المكتبات المطلوبة غير متوفرة: {', '.join(missing_deps)}"
#         if available_deps:
#             message += f" | المتوفرة: {', '.join(available_deps)}"
#         if pil_available and not DEPENDENCIES_AVAILABLE:
#             message += " | سيتم استخدام صور بديلة"

#         # محاولة التثبيت التلقائي
#         message += " | جاري المحاولة التلقائية..."
#         return False, message

#     return True, f"جميع المكتبات متوفرة: {', '.join(available_deps)}"




def read_ies_file(filepath):
    """قراءة زوايا رأسية وأول مجموعة إضاءة من ملف IES"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف {filepath}: {e}")
        return None, None

    # تجاوز الهيدر
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("TILT"):
            data_start = i + 1
            break

    # قراءة البيانات الرقمية
    data = []
    for line in lines[data_start:]:
        line = line.strip()
        if line:
            data.extend(line.split())

    try:
        data = list(map(float, data))
    except ValueError as e:
        print(f"❌ خطأ في تحويل البيانات الرقمية في الملف {filepath}: {e}")
        return None, None

    try:
        # قراءة معاملات الملف
        num_vertical_angles = int(data[3])
        num_horizontal_angles = int(data[4])

        vertical_angles = data[7:7+num_vertical_angles]

        candela_start = 7 + num_vertical_angles + num_horizontal_angles
        total_candela = num_vertical_angles * num_horizontal_angles
        candela_values = data[candela_start:candela_start+total_candela]

        # نأخذ فقط أول شريحة من التوزيع
        slice_values = candela_values[:num_vertical_angles]

        return vertical_angles, slice_values
    except (IndexError, ValueError) as e:
        print(f"❌ خطأ أثناء قراءة الملف {filepath}: {e}")
        return None, None


def render_ies_to_image(angles_deg, candelas, save_path, width=600, height=600, scale_factor=3):
    """توليد صورة من بيانات IES"""
    if not DEPENDENCIES_AVAILABLE:
        print("❌ المكتبات المطلوبة غير متوفرة لتوليد الصور")
        return False

    try:
        import math

        # تحويل البيانات إلى numpy arrays
        angles = [math.radians(angle) for angle in angles_deg]
        candelas = np.array(candelas)

        if candelas.max() == 0:
            print("⚠️ كل قيم الشموع صفر. تجاهل الملف.")
            return False

        # تطبيع القيم
        candelas = candelas / candelas.max()

        # إنشاء مصفوفة الصورة
        img = np.zeros((height, width))

        light_x = width // 2
        light_y = int(height * 0.1)  # نقطة مصدر الضوء 10% من الأعلى

        max_radius = min(width, height) * 0.9

        # توليد الصورة
        for y in range(height):
            for x in range(width):
                dx = x - light_x
                dy = y - light_y
                r = math.sqrt(dx ** 2 + dy ** 2)

                if r == 0 or r > max_radius:
                    continue

                # حساب الزاوية
                if r > 0:
                    theta = math.acos(min(1.0, max(-1.0, dy / r)))
                    if dx < 0:
                        theta = 2 * math.pi - theta

                    deg = math.degrees(theta)
                    if deg > 180:
                        deg = 360 - deg

                    # العثور على الشدة المناسبة
                    idx = 0
                    for i, angle in enumerate(angles_deg):
                        if angle <= deg:
                            idx = i
                        else:
                            break

                    if idx == 0:
                        intensity = candelas[0]
                    elif idx >= len(angles_deg) - 1:
                        intensity = candelas[-1]
                    else:
                        # تداخل خطي
                        a0, a1 = angles_deg[idx], angles_deg[idx + 1]
                        c0, c1 = candelas[idx], candelas[idx + 1]
                        if a1 != a0:
                            intensity = c0 + (c1 - c0) * ((deg - a0) / (a1 - a0))
                        else:
                            intensity = c0

                    # تطبيق المقياس والتخفيف
                    intensity = min(1.0, intensity * scale_factor)
                    falloff = (1 - r / max_radius) ** 2
                    img[y, x] = intensity * falloff

        # حفظ الصورة
        colors = [(0, 0, 0), (1.0, 0.65, 0.39)]  # أسود إلى أصفر دافئ
        cmap = LinearSegmentedColormap.from_list("warm_yellow", colors, N=256)

        plt.imsave(save_path, img, cmap=cmap)
        return True

    except Exception as e:
        print(f"❌ خطأ في توليد الصورة: {e}")
        return False
    
def show_message(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)

def generate_images_for_folder(folder):
    """توليد صور لجميع ملفات IES في مجلد محدد"""
    global DEPENDENCIES_AVAILABLE

    if not folder or not os.path.exists(folder):
        print("❌ المجلد غير موجود.")
        return 0, 0

    # # محاولة التثبيت التلقائي إذا لم تكن المكتبات متوفرة
    # if not DEPENDENCIES_AVAILABLE:
    #     print("🔄 محاولة تثبيت المكتبات تلقائياً...")
    #     install_success = install_dependencies_automatically()
    #     if install_success:
    #         # إعادة فحص المكتبات
    #         deps_available, deps_message = check_dependencies()
    #         if deps_available:
    #             print("🎉 تم تثبيت المكتبات بنجاح!")
    #             DEPENDENCIES_AVAILABLE = True
    #         else:
    #             print("⚠️ التثبيت التلقائي لم ينجح، سيتم استخدام الصور البديلة")

    generated_count = 0
    skipped_count = 0

    try:
        files = os.listdir(folder)
    except Exception as e:
        print(f"❌ خطأ في قراءة محتويات المجلد: {e}")
        return 0, 0

    for file in files:
        if file.lower().endswith(".ies"):
            path = os.path.join(folder, file)
            out_img = os.path.join(folder, os.path.splitext(file)[0] + ".png")

            # تحقق من وجود الصورة مسبقاً
            if not os.path.exists(out_img):
                if DEPENDENCIES_AVAILABLE:
                    # استخدام الطريقة المتقدمة
                    angles, candelas = read_ies_file(path)
                    if angles and candelas:
                        success = render_ies_to_image(angles, candelas, out_img)
                        if success:
                            print(f"✔ تم توليد صورة عالية الجودة: {out_img}")
                            generated_count += 1
                        else:
                            print(f"❌ فشل في توليد صورة لـ {file}")
                            skipped_count += 1
                    else:
                        print(f"⚠ تم تخطي الملف (خطأ في القراءة): {file}")
                        skipped_count += 1
                else:
                    # استخدام الطريقة البديلة
                    success = create_simple_placeholder_image(out_img)
                    if success:
                        print(f"✔ تم إنشاء صورة بديلة: {out_img}")
                        generated_count += 1
                    else:
                        print(f"❌ فشل في إنشاء صورة بديلة لـ {file}")
                        skipped_count += 1
            else:
                print(f"⚠ الصورة موجودة مسبقاً: {file}")
                skipped_count += 1

    return generated_count, skipped_count

def main():
    """الدالة الرئيسية لتشغيل البرنامج بشكل مستقل"""
    if not TKINTER_AVAILABLE:
        print("❌ tkinter غير متوفر - لا يمكن عرض واجهة اختيار المجلد")
        return

    if not DEPENDENCIES_AVAILABLE:
        print("❌ المكتبات المطلوبة غير متوفرة")
        show_message("خطأ", "المكتبات المطلوبة (numpy, matplotlib) غير متوفرة")
        return

    try:
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="اختر مجلد ملفات IES")

        if not folder:
            print("❌ لم يتم اختيار مجلد.")
            return

        generated_count, skipped_count = generate_images_for_folder(folder)
        generated_count, skipped_count = generate_images_for_folder(folder)

        message = f"🎉 اكتملت عملية توليد صور الإضاءة!\nتم توليد {generated_count} صورة جديدة\nتم تخطي {skipped_count} ملف"
        print(f"\n{message}")
        show_message("نجاح", message)

    except Exception as e:
        error_msg = f"❌ خطأ غير متوقع: {e}"
        print(error_msg)
        show_message("خطأ", error_msg)


if __name__ == "__main__":
    main()

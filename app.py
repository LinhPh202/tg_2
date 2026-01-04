import streamlit as st
import itertools
import math

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Unique Math Solver", page_icon="🧩", layout="wide")

# --- DANH SÁCH MẪU CÂU (TEMPLATES) ---
# Format: {0}..{4} là số, {5}..{8} là phép tính
TEMPLATE_NO_BRACKET = ["{0}{5}{1}{6}{2}{7}{3}{8}{4}"]
TEMPLATES_WITH_BRACKET = [
    "({0}{5}{1}){6}{2}{7}{3}{8}{4}",
    "{0}{5}({1}{6}{2}){7}{3}{8}{4}",
    "{0}{5}{1}{6}({2}{7}{3}){8}{4}",
    "{0}{5}{1}{6}{2}{7}({3}{8}{4})",
    "({0}{5}{1}{6}{2}){7}{3}{8}{4}",
    "{0}{5}({1}{6}{2}{7}{3}){8}{4}",
    "{0}{5}{1}{6}({2}{7}{3}{8}{4})",
    "(({0}{5}{1}){6}{2}){7}{3}{8}{4}",
    "({0}{5}({1}{6}{2})){7}{3}{8}{4}",
    "{0}{5}(({1}{6}{2}){7}{3}){8}{4}",
    "{0}{5}({1}{6}({2}{7}{3})){8}{4}",
    "({0}{5}{1}){6}({2}{7}{3}){8}{4}",
    "(({0}{5}{1}){6}{2}{7}{3}){8}{4}",
    "({0}{5}{1}){6}{2}{7}({3}{8}{4})",
    "(({0}{5}{1}){6}({2}{7}{3})){8}{4}",
    "{0}{5}(({1}{6}{2}){7}({3}{8}{4}))",
]

# --- HÀM XỬ LÝ TOÁN HỌC ---
def solve_math_unique_ops(numbers, targets, tolerance, use_brackets):
    solutions = []
    
    # Pool phép tính: 5 phép tính cơ bản
    # Lưu ý: ^ đại diện cho lũy thừa (và căn nếu số mũ là nghịch đảo)
    ops_pool = ['+', '-', '*', '/', '^']
    
    # 1. SINH HOÁN VỊ SỐ (Permutations of Numbers)
    # 5 con số -> 120 trường hợp
    num_perms = list(itertools.permutations(numbers))

    # 2. SINH HOÁN VỊ PHÉP TÍNH (Permutations of Operators)
    # YÊU CẦU CỦA BẠN: "Các phép tính chỉ được sử dụng 1 lần"
    # -> Ta lấy hoán vị (permutations) chập 4 từ 5 phép tính.
    # -> Điều này đảm bảo trong 1 bộ 4 phép tính, KHÔNG bao giờ có phép trùng.
    # Ví dụ: ('+', '-', '*', '/') hoặc ('^', '/', '+', '-')
    op_perms = list(itertools.permutations(ops_pool, 4))

    # Chọn templates
    active_patterns = TEMPLATE_NO_BRACKET[:]
    if use_brackets:
        active_patterns += TEMPLATES_WITH_BRACKET

    # Cache cho các biểu thức đã tính để tránh trùng lặp string hiển thị
    seen_expr_string = set()

    for n_p in num_perms:
        for o_p in op_perms:
            # Tạo bộ phép tính cho Python (thay ^ bằng **)
            py_ops = [o.replace('^', '**') for o in o_p]
            display_ops = o_p
            
            # Gộp data để fill vào template
            fill_data_py = list(n_p) + list(py_ops)
            fill_data_disp = list(n_p) + list(display_ops)

            for pattern in active_patterns:
                # Tạo chuỗi hiển thị trước để check trùng
                try:
                    expr_disp = pattern.format(*fill_data_disp)
                except IndexError: continue # Phòng hờ lỗi format

                if expr_disp in seen_expr_string:
                    continue
                seen_expr_string.add(expr_disp)

                # Tạo chuỗi tính toán
                expr_py = pattern.format(*fill_data_py)

                try:
                    # Eval an toàn
                    val = eval(expr_py)
                    
                    # Bỏ qua số phức (do căn bậc chẵn của số âm)
                    if isinstance(val, complex): continue
                    
                    # Bỏ qua vô cực hoặc NaN
                    if math.isinf(val) or math.isnan(val): continue

                    # Kiểm tra so với Target (1 hoặc 20)
                    for t in targets:
                        diff = abs(val - t)
                        if diff <= tolerance:
                            solutions.append({
                                'val': val,
                                'expr': expr_disp,
                                'diff': diff,
                                'target': t
                            })
                except (ZeroDivisionError, OverflowError, ValueError):
                    continue

    return solutions

# --- GIAO DIỆN STREAMLIT ---
st.title("🧩 Math Solver: Độc Nhất & Chính Xác")
st.markdown("""
Công cụ tìm biểu thức tạo ra số **1** hoặc **20** từ 5 số nhập vào.
* **Quy tắc:** Mỗi phép tính `+ - * / ^` chỉ được dùng tối đa 1 lần trong mỗi dòng.
* **Kết quả:** Đã lọc trùng lặp giá trị.
""")

with st.sidebar:
    st.header("1. Nhập liệu")
    nums_in = st.text_input("Nhập 5 số (cách nhau bởi dấu cách)", "5 5 5 5 5")
    
    st.divider()
    st.header("2. Tùy chọn")
    use_brackets = st.checkbox("Dùng Ngoặc ( )", value=True)
    tolerance = st.slider("Sai số cho phép (+/-)", 0.0, 2.0, 0.0, 0.01, format="%.2f")
    
    st.markdown("---")
    run_btn = st.button("🚀 Tìm Kiếm", type="primary", use_container_width=True)

# --- XỬ LÝ KHI ẤN NÚT ---
if run_btn:
    # 1. Parse Input
    try:
        # Hỗ trợ nhập số thập phân hoặc phân số (đơn giản)
        clean_nums_str = nums_in.replace(',', ' ').split()
        if len(clean_nums_str) != 5:
            st.error("⚠️ Vui lòng nhập đúng 5 con số.")
            st.stop()
            
        nums = []
        for x in clean_nums_str:
            f_val = float(x)
            # Nếu là số nguyên (ví dụ 5.0) thì chuyển về int cho đẹp, còn lại giữ float
            nums.append(int(f_val) if f_val.is_integer() else f_val)
            
    except ValueError:
        st.error("⚠️ Định dạng số không hợp lệ.")
        st.stop()

    # 2. Run Solver
    with st.spinner("Đang tính toán các hoán vị..."):
        # Target cố định là 1 và 20 theo context
        results = solve_math_unique_ops(nums, [1, 20], tolerance, use_brackets)

    if not results:
        st.warning("Không tìm thấy kết quả nào phù hợp với sai số này.")
    else:
        # 3. Hiển thị kết quả (Logic của bạn)
        c1, c2 = st.columns(2)

        def render_column(target_val, col_obj):
            # Lọc các kết quả thuộc target này
            subset = [r for r in results if r['target'] == target_val]
            
            # Sắp xếp: Ưu tiên sai số thấp nhất (gần đúng nhất)
            subset.sort(key=lambda x: x['diff'])

            # --- THUẬT TOÁN LỌC GIÁ TRỊ TRÙNG (QUAN TRỌNG) ---
            unique_report = []
            seen_values = set()
            
            for item in subset:
                # Làm tròn 5 số lẻ để so sánh tính độc nhất
                # Ví dụ: 19.999999 và 20.000001 có thể coi là khác nhau nếu muốn chi tiết,
                # hoặc làm tròn lỏng hơn nếu muốn gọn. Ở đây để 5 số.
                val_check = round(item['val'], 5)
                
                if val_check not in seen_values:
                    unique_report.append(item)
                    seen_values.add(val_check)
                
                # Giới hạn hiển thị 10 kết quả ĐỘC NHẤT
                if len(unique_report) >= 10:
                    break
            
            # Render UI
            col_obj.subheader(f"Mục tiêu: {target_val}")
            if not unique_report:
                col_obj.caption("Không tìm thấy.")
                return

            for item in unique_report:
                # Logic màu sắc
                if item['diff'] < 1e-9: # Rất chính xác
                    color = "#198754" # Green
                    bg = "#e8f5e9"
                    label = "Chính xác"
                else:
                    color = "#fd7e14" # Orange
                    bg = "#fff3cd"
                    label = "Gần đúng"

                col_obj.markdown(f"""
                <div style="background:{bg}; padding:12px; border-radius:8px; margin-bottom:10px; border-left:5px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-family:'Courier New', monospace; font-size:1.1em; color:#212529; font-weight:bold; letter-spacing: 0.5px;">
                        {item['expr']}
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:8px; align-items:center; border-top:1px solid rgba(0,0,0,0.05); padding-top:4px;">
                        <span style="font-size:1.2em; color:{color}; font-weight:bold">
                            = {item['val']:.5g}
                        </span>
                        <span style="font-size:0.75em; color:#555; background:#fff; padding:2px 8px; border-radius:10px; border:1px solid #ddd">
                            {label} (Lệch {item['diff']:.4f})
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with c1: render_column(1, c1)
        with c2: render_column(20, c2)

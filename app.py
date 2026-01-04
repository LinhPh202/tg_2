import streamlit as st
import itertools
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver: Đa Dạng Kết Quả", page_icon="🌈", layout="wide")

# --- DANH SÁCH MẪU CÂU (TEMPLATES) ---
TEMPLATE_NO_BRACKET = ["{0}{5}{1}{6}{2}{7}{3}{8}{4}"]

TEMPLATES_WITH_BRACKET = [
    "({0}{5}{1}){6}{2}{7}{3}{8}{4}",           # (A+B)+C+D+E
    "{0}{5}({1}{6}{2}){7}{3}{8}{4}",           # A+(B+C)+D+E
    "{0}{5}{1}{6}({2}{7}{3}){8}{4}",           # A+B+(C+D)+E
    "{0}{5}{1}{6}{2}{7}({3}{8}{4})",           # A+B+C+(D+E)
    "({0}{5}{1}{6}{2}){7}{3}{8}{4}",           # (A+B+C)+D+E
    "{0}{5}({1}{6}{2}{7}{3}){8}{4}",           # A+(B+C+D)+E
    "{0}{5}{1}{6}({2}{7}{3}{8}{4})",           # A+B+(C+D+E)
    "(({0}{5}{1}){6}{2}){7}{3}{8}{4}",         # ((A+B)+C)+D+E
    "({0}{5}({1}{6}{2})){7}{3}{8}{4}",         # (A+(B+C))+D+E
    "{0}{5}(({1}{6}{2}){7}{3}){8}{4}",         # A+((B+C)+D)+E
    "{0}{5}({1}{6}({2}{7}{3})){8}{4}",         # A+(B+(C+D))+E
    "({0}{5}{1}){6}({2}{7}{3}){8}{4}",         # (A+B)+(C+D)+E
    "(({0}{5}{1}){6}{2}{7}{3}){8}{4}",         # ((A+B)+C+D)+E
    "({0}{5}{1}){6}{2}{7}({3}{8}{4})",         # (A+B)+C+(D+E)
    "(({0}{5}{1}){6}({2}{7}{3})){8}{4}",       # ((A+B)+(C+D))+E
    "{0}{5}(({1}{6}{2}){7}({3}{8}{4}))",       # A+((B+C)+(D+E))
]

def solve_math(numbers, operators, targets, tolerance, use_brackets):
    solutions = []
    # Dùng set để lọc trùng lặp biểu thức ngay từ đầu
    seen_expr = set()

    # Lọc phép tính nối
    binary_ops_pool = [op for op in operators if op in ['+', '-', '*', '/', '^']]
    
    if len(binary_ops_pool) < 4:
        return [], f"Thiếu phép tính! Cần tối thiểu 4 phép nối (+ - * / ^) cho 5 số."

    active_patterns = TEMPLATE_NO_BRACKET[:]
    if use_brackets:
        active_patterns += TEMPLATES_WITH_BRACKET

    num_perms = list(itertools.permutations(numbers))
    op_perms = list(set(itertools.permutations(binary_ops_pool, 4)))

    for n_p in num_perms:
        for o_p in op_perms:
            py_ops = [o.replace('^', '**') for o in o_p]
            display_ops = o_p
            
            fill_data_py = list(n_p) + list(py_ops)
            fill_data_disp = list(n_p) + list(display_ops)

            for pattern in active_patterns:
                try:
                    expr_disp = pattern.format(*fill_data_disp)
                    if expr_disp in seen_expr: continue
                    seen_expr.add(expr_disp)

                    expr_py = pattern.format(*fill_data_py)
                    val = eval(expr_py)
                    
                    if isinstance(val, complex): continue
                    
                    for t in targets:
                        diff = abs(val - t)
                        if diff <= tolerance:
                            solutions.append({
                                'val': val,
                                'expr': expr_disp,
                                'diff': diff,
                                'target': t
                            })
                except:
                    continue
    return solutions, None

# --- GIAO DIỆN ---
st.title("🌈 Math Solver: Đa Dạng Kết Quả")
st.markdown("Công cụ này sẽ ưu tiên hiển thị **10 giá trị kết quả khác nhau** (không bị lặp lại số giống nhau).")

with st.sidebar:
    st.header("1. Nhập liệu")
    nums_in = st.text_input("5 Số", "3 5 2 8 1")
    ops_in = st.text_input("Phép tính", "+ - * / ^")
    
    st.divider()
    
    st.header("2. Tùy chọn")
    use_brackets = st.checkbox("Dùng Ngoặc ( )", value=False)
    # Tăng sai số lên để tìm được nhiều số lẻ hơn
    tolerance = st.slider("Sai số cho phép (+/-)", 0.0, 5.0, 1.5, 0.1)
    
    run_btn = st.button("🚀 Tính Toán", type="primary")

if run_btn:
    try:
        clean_nums = nums_in.replace(',', ' ').split()
        nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
        
        clean_ops = ops_in.replace(',', ' ').split()
        ops = [x.strip() for x in clean_ops]
        
        if len(nums) != 5:
            st.error(f"Vui lòng nhập đúng 5 con số.")
        else:
            mode_text = "Có ngoặc" if use_brackets else "Không ngoặc"
            st.info(f"Đang tìm các giá trị KHÁC NHAU... | Mode: {mode_text}")
            
            with st.spinner("Processing..."):
                results, error = solve_math(nums, ops, [1, 20], tolerance, use_brackets)
            
            if error:
                st.error(error)
            elif not results:
                st.warning("Không tìm thấy kết quả nào.")
            else:
                c1, c2 = st.columns(2)
                
                # --- HÀM HIỂN THỊ ĐA DẠNG (DISTINCT RESULTS) ---
                def show_distinct_report(target, container):
                    subset = [r for r in results if r['target'] == target]
                    # Sắp xếp theo độ lệch tăng dần (gần đúng nhất lên đầu)
                    subset.sort(key=lambda x: x['diff'])
                    
                    # THUẬT TOÁN LỌC GIÁ TRỊ TRÙNG LẶP
                    unique_values_report = []
                    seen_values = set()
                    
                    for item in subset:
                        # Làm tròn giá trị đến 4 số lẻ để so sánh
                        # Mục đích: Coi 20.0 và 20.0000001 là giống nhau -> Lọc bỏ
                        val_rounded = round(item['val'], 4)
                        
                        if val_rounded not in seen_values:
                            unique_values_report.append(item)
                            seen_values.add(val_rounded)
                        
                        # Chỉ lấy đủ 10 giá trị khác nhau thì dừng
                        if len(unique_values_report) >= 10:
                            break
                    
                    # Render ra màn hình
                    container.subheader(f"🎯 Mục tiêu: {target}")
                    
                    if not unique_values_report:
                        container.caption("Không tìm thấy.")
                        return

                    for i, item in enumerate(unique_values_report):
                        # Màu sắc
                        if item['diff'] < 1e-9:
                            color = "#198754" # Xanh
                            bg = "#e8f5e9"
                            label = "Chính xác"
                        else:
                            color = "#fd7e14" # Cam
                            bg = "#fff3cd"
                            label = "Gần đúng"

                        container.markdown(f"""
                        <div style="background:{bg}; padding:10px; border-radius:6px; margin-bottom:8px; border-left:5px solid {color}">
                            <div style="font-family:monospace; font-size:1.1em; color:#333; font-weight:bold">
                                {item['expr']}
                            </div>
                            <div style="display:flex; justify_content:space-between; margin-top:5px; align-items:center">
                                <span style="font-size:1.3em; color:{color}; font-weight:bold">
                                    = {item['val']:.5f}
                                </span>
                                <span style="font-size:0.8em; color:#666; background:#fff; padding:2px 6px; border-radius:4px; border:1px solid #ddd">
                                    {label} (Lệch {item['diff']:.4f})
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with c1: show_distinct_report(1, c1)
                with c2: show_distinct_report(20, c2)

    except Exception as e:
        st.error(f"Lỗi: {e}")

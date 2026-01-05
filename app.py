import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Smart Math Solver", page_icon="🧠")

# --- 1. HÀM TIỆN ÍCH (FORMAT & NORMALIZE) ---

def format_val(n):
    """
    Định dạng số:
    - Nếu là số nguyên (ví dụ 5.0) -> Trả về "5"
    - Nếu là số thực (ví dụ 5.5) -> Trả về "5.5"
    """
    if n is None: return "Error"
    # Kiểm tra sai số cực nhỏ để xác định số nguyên
    if abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    else:
        # Làm tròn 5 chữ số thập phân, bỏ số 0 thừa ở cuối
        return f"{n:.5f}".rstrip('0').rstrip('.')

def normalize_op(op_input):
    """
    Chẩn hóa các ký tự phép tính người dùng nhập về chuẩn Python
    """
    op = op_input.strip().lower()
    
    # Từ điển ánh xạ (Mapping)
    mapping = {
        # Cộng
        '+': '+', '＋': '+',
        # Trừ (Dấu gạch ngang, dấu trừ toán học)
        '-': '-', '−': '-', '–': '-',
        # Nhân
        '*': '*', '×': '*', 'x': '*', '.': '*',
        # Chia
        '/': '/', '÷': '/', ':': '/',
        # Mũ
        '^': '^',
        # Căn bậc 2
        'sqrt': 'sqrt', '√': 'sqrt',
        # Giai thừa
        '!': '!'
    }
    
    return mapping.get(op, None) # Trả về None nếu không nhận diện được

# --- 2. CORE: HÀM TÍNH TOÁN ---

def safe_eval(expr):
    """Tính toán an toàn"""
    try:
        if "**" in expr: 
            parts = expr.split("**")
            # Chặn số mũ quá lớn
            if float(parts[1].split()[0].replace(')', '')) > 6: return None
            
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "factorial": math.factorial})
        
        if isinstance(val, complex) or math.isinf(val) or math.isnan(val):
            return None
        return val
    except:
        return None

def apply_unary(val, op):
    """Tính toán 1 ngôi"""
    try:
        if op == 'sqrt':
            return math.sqrt(val) if val >= 0 else None
        if op == '!':
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-9:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- 3. CORE: BỘ SINH BIỂU THỨC ---

def generate_expressions(nums, ops, allow_brackets):
    """
    Sinh tất cả biểu thức hợp lệ
    """
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    # Loop Hoán vị Số
    for num_perm in itertools.permutations(nums):
        # Loop Hoán vị Unary
        for u_perm in unary_perms:
            terms_vals = []
            terms_strs = []
            valid_term = True
            
            for i, n in enumerate(num_perm):
                u_op = u_perm[i]
                
                # --- SỬ DỤNG FORMAT_VAL ĐỂ HIỂN THỊ ĐẸP (VD: sqrt(4) thay vì sqrt(4.0)) ---
                n_fmt = format_val(n) 
                
                if u_op:
                    val = apply_unary(n, u_op)
                    if val is None: valid_term = False; break
                    terms_vals.append(val)
                    if u_op == 'sqrt': terms_strs.append(f"sqrt({n_fmt})") # √
                    else: terms_strs.append(f"{n_fmt}!") # !
                else:
                    terms_vals.append(n)
                    terms_strs.append(n_fmt)
            
            if not valid_term: continue

            # Loop Hoán vị Binary
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i]))
                    op_symbol = b_perm[i]
                    
                    # Hiển thị đẹp cho dấu nhân/chia/căn
                    display_sym = op_symbol
                    if op_symbol == '*': display_sym = '×'
                    if op_symbol == '/': display_sym = '÷'
                    
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((display_sym, py_op))
                base_components.append((terms_strs[-1], terms_vals[-1]))
                
                # Logic Ngoặc
                bracket_configs = [None]
                if allow_brackets:
                    n_terms = len(terms_vals)
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            if i == 0 and j == n_terms - 1: continue
                            bracket_configs.append((i, j))

                # Tính toán
                for cfg in bracket_configs:
                    py_parts = []
                    disp_parts = []
                    term_idx = 0
                    for k, comp in enumerate(base_components):
                        if k % 2 == 0: # Số
                            t_str, t_val = comp
                            if cfg and term_idx == cfg[0]:
                                py_parts.append("(")
                                disp_parts.append("(")
                            py_parts.append(str(t_val))
                            disp_parts.append(t_str)
                            if cfg and term_idx == cfg[1]:
                                py_parts.append(")")
                                disp_parts.append(")")
                            term_idx += 1
                        else: # Dấu
                            disp_sym, py_sym = comp
                            py_parts.append(py_sym)
                            disp_parts.append(disp_sym)
                    
                    full_py = "".join(py_parts)
                    full_disp = "".join(disp_parts)
                    final_val = safe_eval(full_py)
                    
                    if final_val is not None:
                        yield final_val, full_disp

# --- 4. HÀM GIẢI (SOLVERS) ---

def solve_target_search(nums, ops, allow_brackets, targets, max_tolerance):
    results = []
    seen_exprs = set()
    gen = generate_expressions(nums, ops, allow_brackets)
    if gen == "ERROR_COUNT": return "ERROR_COUNT"
    
    for val, expr in gen:
        for t in targets:
            diff = abs(val - t)
            if diff <= max_tolerance:
                unique_key = f"{expr}_{t}"
                if unique_key not in seen_exprs:
                    results.append({
                        'val': val, 'expr': expr, 'diff': diff,
                        'target_matched': t, 'is_exact': diff < 1e-9
                    })
                    seen_exprs.add(unique_key)
    return results

def solve_optimization(nums, ops, allow_brackets, mode):
    if mode == 'max_negative': best_val = float('-inf')
    else: best_val = float('inf')

    best_results = []
    seen_exprs = set()
    
    gen = generate_expressions(nums, ops, allow_brackets)
    if gen == "ERROR_COUNT": return "ERROR_COUNT"
    
    for val, expr in gen:
        # Check số nguyên
        if abs(val - round(val)) < 1e-9:
            int_val = int(round(val))
            
            if mode == 'min_positive' and int_val <= 0: continue
            if mode == 'max_negative' and int_val >= 0: continue
            
            update_record = False
            if mode == 'max_negative':
                if int_val > best_val: update_record = True
            else:
                if int_val < best_val: update_record = True
            
            if update_record:
                best_val = int_val
                best_results = [{'val': int_val, 'expr': expr}]
                seen_exprs = {expr}
            elif int_val == best_val:
                if expr not in seen_exprs:
                    best_results.append({'val': int_val, 'expr': expr})
                    seen_exprs.add(expr)
                    
    return best_results, best_val

# --- 5. GIAO DIỆN (UI) ---
st.title("🧠 Solver: Phương trình Quần Què - Chơi xong Xóa")

mode_label = st.radio(
    "👉 Chọn mục tiêu:",
    [
        "🎯 Tìm theo Đích (Target)", 
        "📉 Tìm số nguyên Bé nhất (Global Min)",
        "➕ Tìm số nguyên DƯƠNG bé nhất (Min Positive)",
        "➖ Tìm số nguyên ÂM lớn nhất (Max Negative)"
    ]
)

mode_map = {
    "🎯 Tìm theo Đích (Target)": "target",
    "📉 Tìm số nguyên Bé nhất (Global Min)": "global_min",
    "➕ Tìm số nguyên DƯƠNG bé nhất (Min Positive)": "min_positive",
    "➖ Tìm số nguyên ÂM lớn nhất (Max Negative)": "max_negative"
}
current_mode = mode_map[mode_label]

st.write("---")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        input_nums = st.text_input("1. Nhập số:", "5, 5, 5, 5")
    with col2:
        # Hướng dẫn thông minh
        input_ops_raw = st.text_input("2. Nhập phép tính:", "+, −, ×, ÷, √, ()")
        st.caption("Hỗ trợ: `+, -, *, /, sqrt, !` và cả `×, ÷, −, √`")

    # --- LOGIC TỰ ĐỘNG PHÁT HIỆN NGOẶC ---
    # Kiểm tra xem người dùng có nhập ký tự ngoặc không
    auto_bracket_detected = any(c in input_ops_raw for c in ['(', ')'])
    
    if auto_bracket_detected:
        allow_bracket = True
        st.info("💡 Đã phát hiện ký tự `()` trong ô phép tính -> **Tự động BẬT chế độ Ngoặc**.")
    else:
        # Nếu không nhập ngoặc thì hiện checkbox cho chọn thủ công
        allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (1 cặp)", value=False)

    col3, col4 = st.columns(2)
    with col3:
        is_disabled = (current_mode != "target")
        input_targets = st.text_input("3. Nhập Target:", "24", disabled=is_disabled)
    with col4:
        if not is_disabled:
            max_tol = st.slider("4. Phạm vi sai số:", 0.0, 10.0, 2.0, 0.1)

if st.button("🚀 Giải bài toán"):
    try:
        # Parse Số
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        
        # --- PARSE PHÉP TÍNH THÔNG MINH ---
        # 1. Loại bỏ ngoặc khỏi chuỗi để tách phép tính (vì ngoặc đã được xử lý bằng biến allow_bracket)
        clean_ops_str = input_ops_raw.replace('(', '').replace(')', '')
        
        # 2. Tách và Chuẩn hóa từng phép tính
        raw_list = [x for x in clean_ops_str.split(',') if x.strip() != '']
        ops = []
        unknown_ops = []
        
        for x in raw_list:
            norm = normalize_op(x)
            if norm:
                ops.append(norm)
            else:
                unknown_ops.append(x)
        
        if unknown_ops:
            st.warning(f"⚠️ Không nhận diện được các ký tự: {', '.join(unknown_ops)}. Đã bỏ qua.")

        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        else:
            # === CHẾ ĐỘ TARGET ===
            if current_mode == "target":
                target_list = [float(x.strip()) for x in input_targets.split(',') if x.strip() != '']
                target_list.sort()
                
                if not target_list:
                    st.error("Vui lòng nhập Target.")
                else:
                    with st.spinner('Đang tính toán...'):
                        res = solve_target_search(nums, ops, allow_bracket, target_list, max_tol)
                        
                        if res == "ERROR_COUNT":
                            st.error(f"❌ Lỗi: Bạn nhập {len(nums)} số nhưng chỉ có {len([o for o in ops if o in ['+','-','*','/','^']])} phép tính nối (cần {len(nums)-1}).")
                        else:
                            r_map = {t: [] for t in target_list}
                            for r in res: r_map[r['target_matched']].append(r)
                            
                            tabs = st.tabs([f"{'✅' if any(i['is_exact'] for i in r_map[t]) else ('⚠️' if r_map[t] else '❌')} {format_val(t)}" for t in target_list])
                            
                            for i, t in enumerate(target_list):
                                with tabs[i]:
                                    dat = r_map[t]
                                    if not dat: st.error(f"Không tìm thấy {format_val(t)}")
                                    else:
                                        dat.sort(key=lambda x: x['diff'])
                                        exacts = [x for x in dat if x['is_exact']]
                                        approxs = [x for x in dat if not x['is_exact']]
                                        
                                        if exacts:
                                            st.success(f"🎉 CHÍNH XÁC")
                                            # Dùng format_val cho kết quả hiển thị
                                            for e in exacts[:10]: st.code(f"{e['expr']} = {format_val(t)}")
                                        
                                        if approxs:
                                            if exacts: 
                                                with st.expander("Kết quả gần đúng"):
                                                    for a in approxs[:5]: st.code(f"{a['expr']} = {format_val(a['val'])}")
                                            else:
                                                st.warning("⚠️ GẦN ĐÚNG")
                                                for a in approxs[:5]: 
                                                    st.write(f"Sai số: {format_val(a['diff'])}")
                                                    st.code(f"{a['expr']} = {format_val(a['val'])}")

            # === CHẾ ĐỘ OPTIMIZATION ===
            else:
                title_map = {
                    "global_min": "SỐ NGUYÊN BÉ NHẤT",
                    "min_positive": "SỐ NGUYÊN DƯƠNG BÉ NHẤT",
                    "max_negative": "SỐ NGUYÊN ÂM LỚN NHẤT"
                }
                with st.spinner('Đang tìm kiếm...'):
                    results, best_val = solve_optimization(nums, ops, allow_bracket, current_mode)
                    
                    if results == "ERROR_COUNT":
                        st.error("❌ Lỗi: Số lượng phép tính nối không khớp.")
                    elif not results:
                        st.warning("Không tìm thấy số nguyên nào thỏa mãn.")
                    else:
                        st.success(f"🏆 {title_map[current_mode]}: {format_val(best_val)}")
                        st.write(f"Tìm thấy **{len(results)}** cách:")
                        for r in results[:10]:
                            st.code(f"{r['expr']} = {format_val(r['val'])}")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")

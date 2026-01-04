import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver: Kiểm soát Ngoặc", page_icon="🧩")

# --- HÀM TÍNH TOÁN CƠ BẢN ---
def safe_eval(expr):
    """Tính toán biểu thức chuỗi một cách an toàn"""
    try:
        # Giới hạn số mũ để tránh treo máy
        if "**" in expr:
            parts = expr.split("**")
            # Kiểm tra sơ bộ số mũ
            if float(parts[1].split()[0].replace(')', '')) > 6: return None
            
        # Sử dụng eval của Python (tuân thủ PEMDAS: Nhân chia trước, Cộng trừ sau)
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "factorial": math.factorial})
        
        # Kiểm tra số phức hoặc vô cực
        if isinstance(val, complex) or math.isinf(val) or math.isnan(val):
            return None
        return val
    except:
        return None

def apply_unary(val, op):
    """Áp dụng phép tính 1 ngôi ngay lập tức vào giá trị"""
    try:
        if op == 'sqrt':
            return math.sqrt(val) if val >= 0 else None
        if op == '!':
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-5:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- THUẬT TOÁN GIẢI (LINEAR PERMUTATION) ---
def solve_linear(nums, ops, allow_brackets, target_1=1, target_2=20, tolerance=0.5):
    results = []
    seen_exprs = set() # Tránh trùng lặp biểu thức hiển thị
    
    # 1. PHÂN LOẠI PHÉP TÍNH
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # Kiểm tra số lượng phép tính 2 ngôi
    # N số cần N-1 phép nối.
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    # Chuẩn bị hoán vị phép tính Unary
    # Nếu có 2 unary ops và 5 số, ta cần gán chúng vào 5 vị trí. 3 vị trí còn lại là None.
    # Logic: Hoán vị danh sách [sqrt, !, None, None, None]
    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    
    # Để tối ưu, dùng set các hoán vị của unary (tránh lặp nếu nhiều None)
    unary_perms = set(itertools.permutations(u_pool_full))

    # 2. VÒNG LẶP CHÍNH
    # Duyệt qua mọi hoán vị của Số
    for num_perm in itertools.permutations(nums):
        
        # Duyệt qua mọi cách gán Unary Ops
        for u_perm in unary_perms:
            
            # -- Tính toán giá trị các Số hạng (Terms) sau khi áp dụng Unary --
            # Ví dụ: 4 bị gán sqrt -> thành 2.0. Chuỗi hiển thị "sqrt(4)"
            terms_vals = []
            terms_strs = []
            valid_term = True
            
            for i, n in enumerate(num_perm):
                u_op = u_perm[i]
                if u_op:
                    val = apply_unary(n, u_op)
                    if val is None: 
                        valid_term = False; break
                    
                    terms_vals.append(val)
                    if u_op == 'sqrt': terms_strs.append(f"sqrt({n})")
                    else: terms_strs.append(f"{n}!") # Giai thừa
                else:
                    terms_vals.append(n)
                    terms_strs.append(str(n))
            
            if not valid_term: continue

            # Duyệt qua mọi hoán vị của Binary Ops (Cộng trừ nhân chia)
            # Dùng set để tránh lặp nếu phép tính giống nhau (vd: +, +)
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                
                # Danh sách các thành phần để ghép chuỗi
                # Với 3 số (T1, T2, T3) và 2 op (O1, O2) -> [T1, O1, T2, O2, T3]
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i])) # Số
                    op_symbol = b_perm[i]
                    # Chuyển đổi ký hiệu cho Python eval
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((op_symbol, py_op)) # Phép tính
                base_components.append((terms_strs[-1], terms_vals[-1])) # Số cuối
                
                # --- LOGIC XỬ LÝ NGOẶC ---
                
                # Danh sách các cấu hình cần kiểm tra
                # Mỗi cấu hình là 1 tuple (start_idx_of_term, end_idx_of_term) để đóng ngoặc
                bracket_configs = []
                
                # Case A: Không dùng ngoặc (Mặc định luôn chạy)
                bracket_configs.append(None)
                
                # Case B: Dùng ĐÚNG 1 cặp ngoặc (Nếu được phép)
                if allow_brackets:
                    n_terms = len(terms_vals)
                    # Chỉ số của các số hạng trong base_components: 0, 2, 4, 6...
                    # Ta cần chọn cặp (start, end) sao cho nó bao ít nhất 1 phép tính
                    # Start từ 0 đến n-2. End từ start+1 đến n-1.
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            # Bỏ qua trường hợp bao toàn bộ biểu thức (vô nghĩa)
                            if i == 0 and j == n_terms - 1:
                                continue
                            bracket_configs.append((i, j))

                # --- TÍNH TOÁN TỪNG CẤU HÌNH ---
                for cfg in bracket_configs:
                    
                    # Xây dựng chuỗi biểu thức Python (để eval) và chuỗi hiển thị
                    py_expr_parts = []
                    display_expr_parts = []
                    
                    # base_components có dạng: [ (Str, Val), (Sym, PySym), (Str, Val)... ]
                    # Index chẵn là Số, Lẻ là Phép tính
                    
                    current_term_idx = 0
                    
                    for k, comp in enumerate(base_components):
                        if k % 2 == 0: # Là SỐ
                            term_str, term_val = comp
                            
                            # Thêm dấu mở ngoặc '('
                            if cfg and current_term_idx == cfg[0]:
                                py_expr_parts.append("(")
                                display_expr_parts.append("(")
                            
                            py_expr_parts.append(str(term_val))
                            display_expr_parts.append(term_str)
                            
                            # Thêm dấu đóng ngoặc ')'
                            if cfg and current_term_idx == cfg[1]:
                                py_expr_parts.append(")")
                                display_expr_parts.append(")")
                            
                            current_term_idx += 1
                        else: # Là PHÉP TÍNH
                            op_sym, op_py = comp
                            py_expr_parts.append(op_py)
                            display_expr_parts.append(op_sym)
                    
                    full_py_expr = "".join(py_expr_parts)
                    full_display_expr = "".join(display_expr_parts)
                    
                    # Eval
                    final_val = safe_eval(full_py_expr)
                    
                    if final_val is not None:
                        # CHECK KẾT QUẢ
                        
                        # Target 1
                        diff1 = abs(final_val - target_1)
                        if final_val != target_1 and diff1 < tolerance:
                            if full_display_expr not in seen_exprs:
                                results.append({'val': final_val, 'expr': full_display_expr, 'target': target_1, 'diff': diff1})
                                seen_exprs.add(full_display_expr)

                        # Target 2
                        diff2 = abs(final_val - target_2)
                        if final_val != target_2 and diff2 < tolerance:
                            if full_display_expr not in seen_exprs:
                                results.append({'val': final_val, 'expr': full_display_expr, 'target': target_2, 'diff': diff2})
                                seen_exprs.add(full_display_expr)
                                
    return results

# --- GIAO DIỆN STREAMLIT ---
st.title("🧩 Solver: Xếp hình (Tùy chọn Ngoặc)")
st.markdown("""
- Dùng **chính xác** các phép tính đã nhập.
- Kết quả **GẦN** 1 hoặc 20 (Không bằng chính xác).
""")

col1, col2 = st.columns(2)
with col1:
    input_nums = st.text_input("1. Nhập các số:", "3, 5, 2")
with col2:
    input_ops = st.text_input("2. Nhập phép tính:", "+, *")
    st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")

# --- CONTROL NGOẶC ---
st.write("---")
allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc? (Tối đa 1 cặp)", value=False)
if allow_bracket:
    st.caption("💡 Máy sẽ thử thêm dạng: `A + B * (C - D)` bên cạnh dạng `A + B * C - D`.")
else:
    st.caption("🔒 Chế độ KHÔNG ngoặc: Tính theo thứ tự ưu tiên (Nhân/Chia trước, Cộng/Trừ sau).")

tolerance = st.slider("Độ lệch chấp nhận được (+/-):", 0.1, 5.0, 1.5, 0.1)

if st.button("🚀 Giải bài toán"):
    try:
        # Parse Input
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        # Validations
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Vui lòng nhập tối đa 5-6 số để tránh treo máy.")
        else:
            with st.spinner('Đang thử mọi hoán vị số và phép tính...'):
                res_code = solve_linear(nums, ops, allow_bracket, target_1=1, target_2=20, tolerance=tolerance)
                
                if res_code == "ERROR_COUNT":
                    binary_ops = [op for op in ops if op in ['+', '-', '*', '/', '^']]
                    st.error(f"""
                    ❌ **Lỗi số lượng phép tính:**
                    Bạn có **{len(nums)} số** → Cần đúng **{len(nums)-1} phép tính nối** (+, -, *, /, ^).
                    Bạn nhập: {len(binary_ops)}.
                    """)
                elif not res_code:
                    st.warning("Không tìm thấy kết quả nào thỏa mãn.")
                else:
                    # Sắp xếp
                    res_code.sort(key=lambda x: x['diff'])
                    
                    st.success(f"Tìm thấy {len(res_code)} kết quả!")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("🎯 Gần 1 (Khác 1.0)")
                        count = 0
                        for s in res_code:
                            if s['target'] == 1:
                                st.code(f"{s['expr']} \n= {s['val']:.5f}")
                                count += 1
                        if count == 0: st.write("Không có.")

                    with c2:
                        st.info("🎯 Gần 20 (Khác 20.0)")
                        count = 0
                        for s in res_code:
                            if s['target'] == 20:
                                st.code(f"{s['expr']} \n= {s['val']:.5f}")
                                count += 1
                        if count == 0: st.write("Không có.")

    except Exception as e:
        st.error(f"Lỗi: {e}")

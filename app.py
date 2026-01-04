import streamlit as st
import itertools
import math
import pandas as pd

# ==========================================
# 1. LOGIC XỬ LÝ TOÁN HỌC
# ==========================================

def get_number_variants(numbers, use_sqrt):
    """
    Tạo biến thể cho từng số.
    - Nếu use_sqrt = False: Chỉ lấy chính nó.
    - Nếu use_sqrt = True: Lấy nó VÀ căn bậc 2 của nó (nếu > 0).
      Ví dụ input 5 -> [(5, '5', '5'), (2.236.., '√5', 'math.sqrt(5)')]
    """
    variants = []
    for n in numbers:
        vars_for_n = []
        # 1. Dạng nguyên bản
        vars_for_n.append((n, str(n), str(n))) 
        
        # 2. Dạng căn bậc 2 (Áp dụng cho MỌI SỐ dương nếu được chọn)
        if use_sqrt and n > 0:
            # Giá trị thực tế
            val = math.sqrt(n)
            # Nếu căn ra chẵn (vd √9=3) thì hiển thị đẹp, nếu lẻ thì để nguyên format √
            if val.is_integer():
                # display_str = f"√{n}"
                pass # Logic dưới sẽ xử lý hiển thị chung
            
            # Lưu tuple: (giá trị thực, chuỗi hiển thị, chuỗi code python)
            vars_for_n.append((val, f"√{n}", f"math.sqrt({n})"))
        
        variants.append(vars_for_n)
    return variants

def solve_expression(numbers, allowed_binary_ops, use_sqrt, use_brackets):
    """
    numbers: List 5 số đầu vào
    allowed_binary_ops: List phép tính 2 ngôi [+, -, *, /, **]
    use_sqrt: Boolean (Có dùng căn hay không)
    use_brackets: Boolean (Có dùng ngoặc hay không)
    """
    results = []
    seen_formulas = set()
    
    # 1. Tạo biến thể số (Thêm √n vào danh sách nếu được chọn)
    number_variants = get_number_variants(numbers, use_sqrt)
    
    # Mapping hiển thị phép tính 2 ngôi
    ops_display = {'+': '+', '-': '-', '*': 'x', '/': ':', '**': '^'}

    # 2. Vòng lặp chính
    # Lưu ý: Khi bật use_sqrt, số lượng tổ hợp tăng gấp 32 lần (2^5).
    # Cần limit hoặc tối ưu nếu server yếu.
    
    count = 0
    MAX_ITERATIONS = 2000000 # Giới hạn vòng lặp để tránh treo trình duyệt
    
    # Hoán vị vị trí các số (Permutations of slots)
    for perm in itertools.permutations(number_variants):
        
        # Chọn biến thể (Dùng số thường hay dùng √)
        # itertools.product sẽ quét qua: (5, 5, 5...) rồi (√5, 5, 5...) rồi (5, √5, 5...)...
        for nums_chosen in itertools.product(*perm):
            vals = [x[0] for x in nums_chosen]      # Giá trị (float/int)
            disps = [x[1] for x in nums_chosen]     # Hiển thị (str)
            calcs = [x[2] for x in nums_chosen]     # Code Python (str)
            
            n = len(vals) # = 5
            
            # Chọn phép tính 2 ngôi lấp vào 4 khoảng trống
            for ops in itertools.product(allowed_binary_ops, repeat=n-1):
                count += 1
                if count > MAX_ITERATIONS: return results # Safety break

                templates = []
                
                # Logic ghép chuỗi cho 5 số
                if n == 5:
                    A, B, C, D, E = calcs
                    dA, dB, dC, dD, dE = disps
                    o1, o2, o3, o4 = ops
                    d1, d2, d3, d4 = [ops_display[o] for o in ops]
                    
                    # --- MẪU 1: KHÔNG NGOẶC (Theo PEDAMS) ---
                    templates.append((
                        f"{A}{o1}{B}{o2}{C}{o3}{D}{o4}{E}", 
                        f"{dA} {d1} {dB} {d2} {dC} {d3} {dD} {d4} {dE}"
                    ))
                    
                    # --- MẪU 2: CÓ NGOẶC ---
                    if use_brackets:
                        # Chỉ thêm vài mẫu cơ bản để giảm tải tính toán
                        templates.append((f"({A}{o1}{B}){o2}{C}{o3}{D}{o4}{E}", f"({dA} {d1} {dB}) {d2} {dC} {d3} {dD} {d4} {dE}"))
                        templates.append((f"{A}{o1}({B}{o2}{C}){o3}{D}{o4}{E}", f"{dA} {d1} ({dB} {d2} {dC}) {d3} {dD} {d4} {dE}"))
                        templates.append((f"{A}{o1}{B}{o2}({C}{o3}{D}){o4}{E}", f"{dA} {d1} {dB} {d2} ({dC} {d3} {dD}) {d4} {dE}"))
                        templates.append((f"{A}{o1}{B}{o2}{C}{o3}({D}{o4}{E})", f"{dA} {d1} {dB} {d2} {dC} {d3} ({dD} {d4} {dE})"))

                # Đánh giá kết quả
                for calc_str, disp_str in templates:
                    if disp_str in seen_formulas: continue
                    
                    try:
                        # Chặn mũ quá lớn
                        if "**" in calc_str and len(calc_str) > 60: continue

                        res = eval(calc_str)
                        
                        # Chỉ lấy kết quả hợp lý (số thực, không vô cực)
                        if isinstance(res, (int, float)) and not math.isinf(res) and abs(res) < 1000000:
                            # Vì dùng căn nên số sẽ lẻ, ta lưu raw value
                            results.append({'val': res, 'expr': disp_str})
                            seen_formulas.add(disp_str)
                    except:
                        continue
    return results

# ==========================================
# 2. GIAO DIỆN STREAMLIT
# ==========================================

def main():
    st.set_page_config(page_title="Math Solver Pro", page_icon="🧩", layout="wide")
    
    st.title("🧩 Math Solver: Mọi phép tính & Căn bậc 2")
    st.markdown("Nhập 5 số bất kỳ. Hệ thống sẽ tìm cách kết hợp để ra kết quả **Gần 1** và **Gần 20**.")
    
    # --- INPUT ---
    with st.expander("⚙️ Cấu hình phép tính", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            input_str = st.text_input("Nhập 5 số (cách nhau dấu phẩy)", value="5, 2, 3, 1, 4")
            
            # Checkbox riêng cho Căn bậc 2 (vì nó là phép 1 ngôi, khác bọn kia)
            use_sqrt = st.checkbox("✅ Sử dụng Căn bậc 2 (√) cho mọi số", value=True)
            st.caption("Ví dụ: Nhập 5 sẽ tự động thử cả 5 và √5 (≈2.23)")
            
        with col2:
            ops_selected = st.multiselect(
                "Chọn phép tính nối (2 ngôi):",
                ['+', '-', '*', '/', '**'],
                default=['+', '-', '*', '/'],
                format_func=lambda x: {'+':'Cộng (+)', '-':'Trừ (-)', '*':'Nhân (x)', '/':'Chia (:)', '**':'Mũ (^)'}[x]
            )
            use_brackets = st.checkbox("Sử dụng Ngoặc ()", value=False)

    run_btn = st.button("🚀 Bắt đầu tìm kiếm", type="primary", use_container_width=True)

    # --- PROCESS ---
    if run_btn:
        try:
            numbers = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
        except:
            st.error("Lỗi nhập liệu: Chỉ nhập số nguyên!")
            return

        if len(numbers) != 5:
            st.warning(f"⚠️ Đang nhập {len(numbers)} số. Hệ thống chạy tốt nhất với 5 số.")
        
        if not ops_selected:
            st.error("Vui lòng chọn ít nhất 1 phép tính nối (+, -, ...)")
            return

        with st.spinner("Đang tính toán (có thể mất vài giây nếu dùng Căn và Ngoặc)..."):
            # Gọi hàm xử lý
            all_results = solve_expression(numbers, ops_selected, use_sqrt, use_brackets)
            
            if not all_results:
                st.warning("Không tìm thấy kết quả nào hợp lý.")
                return

            # Chuyển thành DataFrame để lọc
            df = pd.DataFrame(all_results)
            
            # Tính khoảng cách tới đích
            df['diff_1'] = abs(df['val'] - 1)
            df['diff_20'] = abs(df['val'] - 20)

            # Lấy Top 15 kết quả tốt nhất cho mỗi mục tiêu
            # drop_duplicates('expr') để tránh hiện 1 công thức 2 lần
            df_target_1 = df.sort_values('diff_1').drop_duplicates(subset=['expr']).head(15)
            df_target_20 = df.sort_values('diff_20').drop_duplicates(subset=['expr']).head(15)

            st.divider()
            
            # --- HIỂN THỊ KẾT QUẢ ---
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.subheader("🎯 Mục tiêu: Gần 1")
                if df_target_1.empty:
                    st.write("Không có kết quả.")
                else:
                    for _, row in df_target_1.iterrows():
                        val = row['val']
                        expr = row['expr']
                        diff = row['diff_1']
                        
                        # Format số lẻ (vì dùng căn nên hay ra số lẻ)
                        val_str = f"{val:.5f}".rstrip('0').rstrip('.')
                        
                        # Logic hiển thị màu sắc
                        if diff < 1e-9: # Chính xác tuyệt đối
                            st.success(f"**{expr} = {val_str}**")
                        elif diff < 0.1: # Rất gần
                            st.info(f"{expr} = {val_str}")
                        else:
                            st.write(f"{expr} = {val_str}")

            with col_res2:
                st.subheader("🎯 Mục tiêu: Gần 20")
                if df_target_20.empty:
                    st.write("Không có kết quả.")
                else:
                    for _, row in df_target_20.iterrows():
                        val = row['val']
                        expr = row['expr']
                        diff = row['diff_20']
                        
                        val_str = f"{val:.5f}".rstrip('0').rstrip('.')
                        
                        if diff < 1e-9:
                            st.success(f"**{expr} = {val_str}**")
                        elif diff < 0.1:
                            st.info(f"{expr} = {val_str}")
                        else:
                            st.write(f"{expr} = {val_str}")

if __name__ == "__main__":
    main()

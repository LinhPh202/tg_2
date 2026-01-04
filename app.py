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
    - Nếu use_sqrt = True: Tạo thêm biến thể căn bậc 2 (nếu n > 0).
    """
    variants = []
    for n in numbers:
        vars_for_n = []
        # 1. Dạng nguyên bản
        vars_for_n.append((n, str(n), str(n))) 
        
        # 2. Dạng căn bậc 2 (Áp dụng cho mọi số dương)
        if use_sqrt and n > 0:
            val = math.sqrt(n)
            # Lưu ý: Python hiển thị số thực, ta dùng f-string format để xử lý sau
            vars_for_n.append((val, f"√{n}", f"math.sqrt({n})"))
        
        variants.append(vars_for_n)
    return variants

def solve_expression(numbers, allowed_binary_ops, use_sqrt, use_brackets):
    results = []
    seen_formulas = set() # Set giúp loại bỏ công thức trùng lặp ngay khi tìm kiếm
    
    number_variants = get_number_variants(numbers, use_sqrt)
    ops_display = {'+': '+', '-': '-', '*': 'x', '/': ':', '**': '^'}
    
    # Giới hạn vòng lặp an toàn
    count = 0
    MAX_ITERATIONS = 2000000 
    
    for perm in itertools.permutations(number_variants):
        for nums_chosen in itertools.product(*perm):
            vals = [x[0] for x in nums_chosen]
            disps = [x[1] for x in nums_chosen]
            calcs = [x[2] for x in nums_chosen]
            
            n = len(vals)
            
            # Nếu user chọn bắt buộc dùng căn, ta có thể check nhanh ở đây để skip
            # Nếu trong disps không có chữ '√' nào và use_sqrt=True -> Skip luôn cho nhanh?
            # Tuy nhiên, để logic lọc ở cuối cho an toàn và linh hoạt.
            
            for ops in itertools.product(allowed_binary_ops, repeat=n-1):
                count += 1
                if count > MAX_ITERATIONS: return results

                templates = []
                if n == 5:
                    A, B, C, D, E = calcs
                    dA, dB, dC, dD, dE = disps
                    o1, o2, o3, o4 = ops
                    d1, d2, d3, d4 = [ops_display[o] for o in ops]
                    
                    # Mẫu KHÔNG ngoặc
                    templates.append((
                        f"{A}{o1}{B}{o2}{C}{o3}{D}{o4}{E}", 
                        f"{dA} {d1} {dB} {d2} {dC} {d3} {dD} {d4} {dE}"
                    ))
                    
                    # Mẫu CÓ ngoặc
                    if use_brackets:
                        templates.append((f"({A}{o1}{B}){o2}{C}{o3}{D}{o4}{E}", f"({dA} {d1} {dB}) {d2} {dC} {d3} {dD} {d4} {dE}"))
                        templates.append((f"{A}{o1}({B}{o2}{C}){o3}{D}{o4}{E}", f"{dA} {d1} ({dB} {d2} {dC}) {d3} {dD} {d4} {dE}"))
                        templates.append((f"{A}{o1}{B}{o2}({C}{o3}{D}){o4}{E}", f"{dA} {d1} {dB} {d2} ({dC} {d3} {dD}) {d4} {dE}"))
                        templates.append((f"{A}{o1}{B}{o2}{C}{o3}({D}{o4}{E})", f"{dA} {d1} {dB} {d2} {dC} {d3} ({dD} {d4} {dE})"))

                for calc_str, disp_str in templates:
                    # Kiểm tra trùng lặp công thức
                    if disp_str in seen_formulas: continue
                    
                    try:
                        if "**" in calc_str and len(calc_str) > 60: continue
                        
                        res = eval(calc_str)
                        
                        if isinstance(res, (int, float)) and not math.isinf(res) and abs(res) < 1000000:
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
    
    st.title("🧩 Math Solver Pro")
    st.markdown("Tìm các công thức tạo ra kết quả **Gần 1** và **Gần 20** từ 5 số bất kỳ.")
    
    with st.expander("⚙️ Cấu hình", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            input_str = st.text_input("Nhập 5 số (cách nhau dấu phẩy)", value="5, 2, 3, 1, 4")
            # Checkbox này giờ mang ý nghĩa BẮT BUỘC
            use_sqrt = st.checkbox("✅ Bắt buộc dùng Căn bậc 2 (√)", value=True, help="Nếu tích vào đây, chỉ hiện các kết quả có chứa dấu căn.")
            
        with col2:
            ops_selected = st.multiselect(
                "Phép tính nối:",
                ['+', '-', '*', '/', '**'],
                default=['+', '-', '*', '/'],
                format_func=lambda x: {'+':'Cộng (+)', '-':'Trừ (-)', '*':'Nhân (x)', '/':'Chia (:)', '**':'Mũ (^)'}[x]
            )
            use_brackets = st.checkbox("Dùng Ngoặc ()", value=False)

    run_btn = st.button("🚀 Tính toán", type="primary", use_container_width=True)

    if run_btn:
        try:
            numbers = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
        except:
            st.error("Lỗi: Chỉ nhập số nguyên.")
            return

        if len(numbers) != 5:
            st.warning("Nên nhập đúng 5 số để có kết quả tốt nhất.")
            
        if not ops_selected:
            st.error("Chưa chọn phép tính nào.")
            return

        with st.spinner("Đang tìm kiếm giải pháp..."):
            all_results = solve_expression(numbers, ops_selected, use_sqrt, use_brackets)
            
            if not all_results:
                st.warning("Không tìm thấy kết quả nào.")
                return

            # Chuyển thành DataFrame
            df = pd.DataFrame(all_results)

            # --- LOGIC MỚI: BẮT BUỘC DÙNG CĂN ---
            if use_sqrt:
                # Lọc chỉ giữ lại dòng nào cột 'expr' có chứa ký tự '√'
                df = df[df['expr'].str.contains("√")]
                if df.empty:
                    st.error("Không tìm thấy kết quả nào thỏa mãn điều kiện 'Bắt buộc dùng Căn bậc 2' để ra gần 1 hoặc 20.")
                    return

            # Tính độ lệch
            df['diff_1'] = abs(df['val'] - 1)
            df['diff_20'] = abs(df['val'] - 20)

            # --- LỌC KẾT QUẢ KHÁC NHAU ---
            # drop_duplicates(['expr']) đảm bảo mỗi công thức chỉ hiện 1 lần
            # head(15) lấy 15 kết quả tốt nhất
            df_target_1 = df.sort_values('diff_1').drop_duplicates(subset=['expr']).head(15)
            df_target_20 = df.sort_values('diff_20').drop_duplicates(subset=['expr']).head(15)

            st.divider()
            c1, c2 = st.columns(2)
            
            # Hàm hiển thị con
            def display_results(dataframe, target_val):
                if dataframe.empty:
                    st.write("Không có kết quả phù hợp.")
                    return
                
                count_shown = 0
                for _, row in dataframe.iterrows():
                    val = row['val']
                    expr = row['expr']
                    # Tính lại diff để color
                    diff = abs(val - target_val)
                    
                    # Format số
                    val_str = f"{val:.5f}".rstrip('0').rstrip('.')
                    
                    # Hiển thị
                    if diff < 1e-9:
                        st.success(f"**{expr} = {val_str}**")
                    elif diff < 0.5:
                        st.info(f"{expr} = {val_str}")
                    else:
                        st.write(f"{expr} = {val_str}")
                    
                    count_shown += 1
            
            with c1:
                st.subheader("🎯 Gần 1 (Top 15)")
                display_results(df_target_1, 1)

            with c2:
                st.subheader("🎯 Gần 20 (Top 15)")
                display_results(df_target_20, 20)

if __name__ == "__main__":
    main()

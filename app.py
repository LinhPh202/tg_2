import streamlit as st
import math
from collections import Counter

# Cấu hình trang
st.set_page_config(page_title="Solver: Cố định phép tính", page_icon="🧩")

# --- HÀM TÍNH TOÁN ---
def calculate_binary(a, b, op):
    try:
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b if b != 0 else None
        if op == '^':
            if abs(a) > 50 or abs(b) > 6: return None # Giới hạn mũ
            if a < 0 and int(b) != b: return None
            return math.pow(a, b)
    except: return None
    return None

def calculate_unary(a, op):
    try:
        if op == 'sqrt':
            return math.sqrt(a) if a >= 0 else None
        if op == '!':
            if 0 <= a <= 10 and abs(a - round(a)) < 1e-5:
                return math.factorial(int(round(a)))
    except: return None
    return None

# --- THUẬT TOÁN GIẢI (BACKTRACKING) ---
def solve_exact_ops(nums, available_ops, target_1=1, target_2=20, tolerance=0.5):
    results = []
    seen_states = set()

    def recursive_solve(current_nums, current_ops):
        # 1. Tối ưu: Memoization để tránh tính lại các trường hợp trùng
        # Key gồm: (các số hiện tại đã sort, các phép tính còn lại đã sort)
        current_nums_sig = tuple(sorted([round(x[0], 5) for x in current_nums]))
        current_ops_sig = tuple(sorted(current_ops))
        state_key = (current_nums_sig, current_ops_sig)
        
        if state_key in seen_states: return
        seen_states.add(state_key)

        # 2. ĐIỀU KIỆN DỪNG: Hết phép tính
        if not current_ops:
            if len(current_nums) == 1:
                val, expr = current_nums[0]
                # Check Target 1
                if val != target_1 and abs(val - target_1) < tolerance:
                    results.append({'val': val, 'expr': expr, 'target': target_1, 'diff': abs(val - target_1)})
                # Check Target 2
                if val != target_2 and abs(val - target_2) < tolerance:
                    results.append({'val': val, 'expr': expr, 'target': target_2, 'diff': abs(val - target_2)})
            return

        # 3. CHECK LOGIC SỐ LƯỢNG
        # Nếu số lượng phép tính 2 ngôi còn lại < số lượng số - 1 -> Không thể giải hết số -> Cắt nhánh
        binary_left = sum(1 for op in current_ops if op in ['+', '-', '*', '/', '^'])
        if binary_left < len(current_nums) - 1:
            return

        # 4. THỬ CÁC PHÉP TÍNH TRONG KHO (available_ops)
        # Lấy danh sách các phép tính ĐỘC NHẤT hiện có để tránh lặp (VD: có 2 dấu +, chỉ cần thử 1 lần)
        unique_ops = set(current_ops)
        
        for op in unique_ops:
            # Tạo danh sách ops mới (bỏ đi 1 op vừa chọn)
            # Lưu ý: Chỉ remove 1 instance đầu tiên tìm thấy
            next_ops = list(current_ops)
            next_ops.remove(op)
            
            # --- TRƯỜNG HỢP A: PHÉP TÍNH 2 NGÔI (+, -, *, /, ^) ---
            if op in ['+', '-', '*', '/', '^']:
                # Cần ít nhất 2 số để tính
                if len(current_nums) >= 2:
                    # Thử ghép mọi cặp số
                    for i in range(len(current_nums)):
                        for j in range(len(current_nums)):
                            if i == j: continue
                            
                            val1, expr1 = current_nums[i]
                            val2, expr2 = current_nums[j]
                            
                            # Tính toán
                            res = calculate_binary(val1, val2, op)
                            if res is not None:
                                new_expr = f"({expr1} {op} {expr2})"
                                # Tạo list số mới
                                next_nums = [x for k, x in enumerate(current_nums) if k != i and k != j]
                                next_nums.append((res, new_expr))
                                
                                recursive_solve(next_nums, next_ops)

            # --- TRƯỜNG HỢP B: PHÉP TÍNH 1 NGÔI (sqrt, !) ---
            elif op in ['sqrt', '!']:
                # Thử áp dụng lên từng số
                for i in range(len(current_nums)):
                    val, expr = current_nums[i]
                    
                    res = calculate_unary(val, op)
                    if res is not None:
                        # Format hiển thị
                        if op == 'sqrt': new_expr = f"sqrt({expr})"
                        else: new_expr = f"({expr}!)"
                        
                        # Tạo list số mới (thay thế số cũ bằng số mới)
                        next_nums = current_nums[:i] + [(res, new_expr)] + current_nums[i+1:]
                        
                        recursive_solve(next_nums, next_ops)

    # Bắt đầu chạy
    initial_nums = [(x, str(x)) for x in nums]
    recursive_solve(initial_nums, available_ops)
    return results

# --- GIAO DIỆN STREAMLIT ---
st.title("🧩 Solver: Xếp hình Toán học")
st.markdown("""
Bạn cung cấp số và các mảnh ghép phép tính. Máy tính sẽ tìm cách sắp xếp để **dùng hết** các phép tính đó.
""")

col1, col2 = st.columns(2)
with col1:
    input_nums = st.text_input("1. Nhập các số (cách nhau dấu phẩy):", "5, 5, 5, 5, 5")
with col2:
    input_ops = st.text_input("2. Nhập các phép tính muốn dùng:", "+, +, -, /, sqrt")
    st.caption("Hỗ trợ: `+, -, *, /, ^` (mũ), `sqrt`, `!` (giai thừa)")

if st.button("🚀 Giải bài toán"):
    try:
        # Xử lý dữ liệu đầu vào
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        # --- VALIDATION (Kiểm tra điều kiện tiên quyết) ---
        binary_ops = [op for op in ops if op in ['+', '-', '*', '/', '^']]
        unary_ops = [op for op in ops if op in ['sqrt', '!']]
        
        required_binary = len(nums) - 1
        
        # Logic kiểm tra: Để nối N số thành 1 số cuối cùng, cần đúng N-1 phép tính nối (2 ngôi)
        # Phép tính 1 ngôi (sqrt, !) không làm giảm số lượng số, nên không ảnh hưởng count này.
        if len(binary_ops) != required_binary:
            st.error(f"""
            ❌ **Lỗi Logic:** Bạn nhập {len(nums)} số, nên bắt buộc phải dùng đúng {required_binary} phép tính 2 ngôi (+, -, *, /, ^).
            \nHiện tại bạn đang nhập {len(binary_ops)} phép tính 2 ngôi ({', '.join(binary_ops)}).
            \n(Lưu ý: `sqrt` và `!` không tính vào điều kiện ghép nối này).
            """)
        else:
            with st.spinner('Đang thử mọi cách sắp xếp...'):
                solutions = solve_exact_ops(nums, ops, target_1=1, target_2=20, tolerance=1.5)
                
                if not solutions:
                    st.warning("Không tìm thấy cách sắp xếp nào thỏa mãn yêu cầu (Gần 1 hoặc 20).")
                else:
                    # Lọc kết quả trùng biểu thức
                    unique_sols = []
                    seen = set()
                    for s in solutions:
                        if s['expr'] not in seen:
                            unique_sols.append(s)
                            seen.add(s['expr'])
                    
                    # Sắp xếp theo sai số thấp nhất
                    unique_sols.sort(key=lambda x: x['diff'])

                    st.success(f"Tìm thấy {len(unique_sols)} cách sắp xếp!")
                    
                    c_res1, c_res2 = st.columns(2)
                    with c_res1:
                        st.info("🎯 Kết quả gần 1")
                        for s in unique_sols:
                            if s['target'] == 1:
                                st.code(f"{s['expr']} \n= {s['val']:.5f}")
                    
                    with c_res2:
                        st.info("🎯 Kết quả gần 20")
                        for s in unique_sols:
                            if s['target'] == 20:
                                st.code(f"{s['expr']} \n= {s['val']:.5f}")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")

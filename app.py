import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver Toán Học", page_icon="🧩")

# --- HÀM TÍNH TOÁN CỐT LÕI ---
def get_ops(allow_add, allow_sub, allow_mul, allow_div, allow_pow, allow_sqrt):
    """Tạo danh sách các phép toán được phép sử dụng"""
    ops = []
    if allow_add: ops.append('+')
    if allow_sub: ops.append('-')
    if allow_mul: ops.append('*')
    if allow_div: ops.append('/')
    if allow_pow: ops.append('^')
    # sqrt được xử lý riêng như một phép toán 1 ngôi (unary)
    return ops

def calculate(a, b, op):
    """Thực hiện phép tính an toàn giữa 2 số"""
    try:
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': 
            return a / b if b != 0 else None
        if op == '^':
            # Giới hạn mũ để tránh treo máy hoặc số quá lớn
            if abs(a) > 100 or abs(b) > 10: return None 
            if a == 0 and b <= 0: return None
            # Tránh số phức
            if a < 0 and int(b) != b: return None
            return math.pow(a, b)
    except:
        return None
    return None

def solve_numbers(nums, ops, allow_sqrt, target_1=1, target_2=20, tolerance=0.5):
    """
    Thuật toán đệ quy tìm kiếm mọi khả năng.
    nums: Danh sách các số (kèm chuỗi biểu thức biểu diễn nó)
    """
    results = []
    
    # Memoization để tránh tính trùng lặp các trạng thái giống nhau
    seen_states = set()

    def recursive_solve(current_list):
        # Tạo key đại diện cho trạng thái hiện tại (sắp xếp để tránh trùng hoán vị)
        # Chỉ lấy giá trị số để check duplicate state
        state_key = tuple(sorted([x[0] for x in current_list]))
        if state_key in seen_states:
            return
        seen_states.add(state_key)

        # 1. Kiểm tra kết quả nếu chỉ còn 1 số
        if len(current_list) == 1:
            val, expr = current_list[0]
            
            # Kiểm tra Target 1
            if val != target_1 and abs(val - target_1) < tolerance:
                results.append({'val': val, 'expr': expr, 'target': target_1, 'diff': abs(val - target_1)})
            
            # Kiểm tra Target 2
            if val != target_2 and abs(val - target_2) < tolerance:
                results.append({'val': val, 'expr': expr, 'target': target_2, 'diff': abs(val - target_2)})
            return

        # 2. Thử phép tính Căn bậc 2 (Unary) - Chỉ áp dụng nếu được chọn
        if allow_sqrt:
            for i in range(len(current_list)):
                val, expr = current_list[i]
                # Chỉ căn nếu số dương và chưa bị căn quá nhiều (để tránh loop)
                if val > 0 and "sqrt" not in expr: 
                    new_val = math.sqrt(val)
                    new_expr = f"sqrt({expr})"
                    
                    # Tạo list mới với số đã được căn
                    new_list = current_list[:i] + [(new_val, new_expr)] + current_list[i+1:]
                    recursive_solve(new_list)

        # 3. Thử phép tính 2 ngôi (+, -, *, /, ^)
        # Chọn 2 số bất kỳ trong list hiện tại
        for i in range(len(current_list)):
            for j in range(len(current_list)):
                if i == j: continue # Không chọn cùng 1 số
                
                val1, expr1 = current_list[i]
                val2, expr2 = current_list[j]

                # Thử tất cả phép tính đã chọn
                for op in ops:
                    res = calculate(val1, val2, op)
                    if res is not None:
                        # Tạo biểu thức mới có ngoặc
                        new_expr = f"({expr1} {op} {expr2})"
                        
                        # Tạo list mới: Bỏ 2 số cũ, thêm số mới vào
                        # Lưu ý: cần xử lý index cẩn thận khi remove
                        remain = [x for k, x in enumerate(current_list) if k != i and k != j]
                        remain.append((res, new_expr))
                        
                        recursive_solve(remain)

    # Bắt đầu đệ quy: Input ban đầu là list các tuple (giá trị, "chuỗi hiển thị")
    initial_list = [(x, str(x)) for x in nums]
    recursive_solve(initial_list)
    return results

# --- GIAO DIỆN STREAMLIT ---
st.title("🧩 Solver: Tìm số gần 1 hoặc 20")
st.markdown("Nhập 5 số và chọn các phép tính. Máy sẽ tự tìm cách ghép (có dùng ngoặc) để ra kết quả.")

# Input 5 số
col_input, col_ops = st.columns([1, 1])

with col_input:
    st.subheader("Nhập liệu")
    input_str = st.text_input("Nhập 5 số (cách nhau bởi dấu phẩy):", "3, 5, 2, 8, 4")
    
with col_ops:
    st.subheader("Chọn phép tính được dùng")
    c1, c2, c3 = st.columns(3)
    use_add = c1.checkbox("Cộng (+)", value=True)
    use_sub = c2.checkbox("Trừ (-)", value=True)
    use_mul = c3.checkbox("Nhân (*)", value=True)
    
    c4, c5, c6 = st.columns(3)
    use_div = c4.checkbox("Chia (/)", value=True)
    use_pow = c5.checkbox("Mũ (^)", value=False) # Mặc định tắt vì dễ ra số ảo
    use_sqrt = c6.checkbox("Căn (sqrt)", value=False)

if st.button("🔍 Tìm kiếm giải pháp"):
    try:
        # Xử lý input đầu vào
        nums = [float(x.strip()) for x in input_str.split(',') if x.strip() != '']
        if len(nums) > 6:
            st.warning("⚠️ Nhập quá nhiều số sẽ làm máy tính chạy rất chậm! Khuyên dùng tối đa 5 số.")
        
        ops = get_ops(use_add, use_sub, use_mul, use_div, use_pow, use_sqrt)
        
        with st.spinner('Đang tính toán hàng nghìn khả năng...'):
            # Gọi hàm giải
            found_solutions = solve_numbers(nums, ops, use_sqrt, target_1=1, target_2=20, tolerance=2.0)
            
            # Lọc và hiển thị kết quả
            if not found_solutions:
                st.error("Không tìm thấy kết quả nào gần 1 hoặc 20 với các số này.")
            else:
                # Sắp xếp theo độ lệch (diff) tăng dần -> Số gần nhất lên đầu
                found_solutions.sort(key=lambda x: x['diff'])
                
                # Loại bỏ các kết quả trùng lặp về biểu thức
                unique_solutions = []
                seen_exprs = set()
                for sol in found_solutions:
                    if sol['expr'] not in seen_exprs:
                        unique_solutions.append(sol)
                        seen_exprs.add(sol['expr'])

                # Chia làm 2 nhóm hiển thị
                st.write("---")
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.success("🎯 Kết quả gần 1 nhất")
                    count = 0
                    for s in unique_solutions:
                        if s['target'] == 1:
                            st.code(f"{s['expr']} \n= {s['val']:.5f}")
                            count += 1
                            if count >= 5: break # Chỉ hiện top 5
                    if count == 0: st.write("Không tìm thấy.")

                with col_res2:
                    st.warning("🎯 Kết quả gần 20 nhất")
                    count = 0
                    for s in unique_solutions:
                        if s['target'] == 20:
                            st.code(f"{s['expr']} \n= {s['val']:.5f}")
                            count += 1
                            if count >= 5: break # Chỉ hiện top 5
                    if count == 0: st.write("Không tìm thấy.")

    except ValueError:
        st.error("Lỗi nhập liệu: Vui lòng nhập đúng định dạng số, cách nhau bởi dấu phẩy.")

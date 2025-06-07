import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt 

# Kết nối tới MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["streamlit"]
    return db["students"]

# Thêm sinh viên mới
def add_student(collection, student_data):
    collection.insert_one(student_data)

# Lấy danh sách sinh viên
def get_students(collection):
    data = list(collection.find({}))
    for item in data:
        item.pop('_id', None)  # cột id  
    return pd.DataFrame(data)

# Thêm điểm cho sinh viên
def add_grade(collection, student_id, subject, grade):
    collection.update_one(
        {"student_id": student_id},
        {"$set": {f"grades.{subject}": grade}}
    )

# Lấy điểm sinh viên
def get_student_grades(collection, student_id):
    student = collection.find_one({"student_id": student_id}, {"_id": 0, "grades": 1})
    return student.get("grades", {}) if student else None

# Sửa thông tin sinh viên
def update_student(collection, student_id, update_data):
    collection.update_one({"student_id": student_id}, {"$set": update_data})

# Streamlit App
def main():
    st.title("Quản Lý Sinh Viên")

    # Kết nối đến collection
    collection = connect_to_mongodb()

    # Menu chức năng
    menu = st.sidebar.selectbox("Chọn chức năng", ["Thêm sinh viên", "Danh sách sinh viên", "Thêm điểm", "Tìm điểm", "Sửa sinh viên",  "Phân tích loại sinh viên"])

    # Thêm sinh viên
    if menu == "Thêm sinh viên":
        st.header("Thêm sinh viên mới")
        student_id = st.text_input("Mã sinh viên")
        name = st.text_input("Họ và tên")
        age = st.number_input("Tuổi", min_value=0, step=1)
        major = st.text_input("Ngành học")

        if st.button("Thêm sinh viên"):
            if student_id and name and age > 0 and major:
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "age": age,
                    "major": major,
                    "grades": {}
                }
                add_student(collection, student_data)
                st.success("Thêm sinh viên thành công!")
            else:
                st.error("Vui lòng nhập đầy đủ thông tin!")

    # Danh sách sinh viên
    elif menu == "Danh sách sinh viên":
        st.header("Danh sách sinh viên")
        students = get_students(collection)
        if not students.empty:
            st.dataframe(students)
        else:
            st.warning("Chưa có sinh viên nào!")

    # Thêm điểm
    elif menu == "Thêm điểm":
        st.header("Thêm điểm cho sinh viên")
        student_id = st.text_input("Nhập mã sinh viên")
        subject = st.text_input("Nhập tên môn học")
    
        st.write("**Nhập điểm thành phần:**")
        grade_a = st.number_input("Điểm A (hệ số 0.6)", min_value=0.0, max_value=10.0, step=0.1)
        grade_b = st.number_input("Điểm B (hệ số 0.3)", min_value=0.0, max_value=10.0, step=0.1)
        grade_c = st.number_input("Điểm C (hệ số 0.1)", min_value=0.0, max_value=10.0, step=0.1)

        if st.button("Thêm điểm"):
            if student_id and subject:
            # Tính điểm trung bình
              avg_grade = grade_a * 0.6 + grade_b * 0.3 + grade_c * 0.1
            
            # Cập nhật điểm vào MongoDB
            collection.update_one(
                {"student_id": student_id},
                {
                    "$set": {
                        f"grades.{subject}": {
                            "A": grade_a,
                            "B": grade_b,
                            "C": grade_c,
                            "avg": avg_grade
                        }
                    }
                },
                upsert=True
            )
            st.success(f"Thêm điểm thành công! Điểm trung bình của môn {subject} là {avg_grade:.2f}.")
        else:
            st.error("Vui lòng nhập đầy đủ mã sinh viên và tên môn học!")


    # Tìm điểm
    elif menu == "Tìm điểm":
        st.header("Tìm điểm của sinh viên")
        student_id = st.text_input("Nhập mã sinh viên")

        if st.button("Tìm điểm"):
            if student_id:
                student = collection.find_one({"student_id": student_id}, {"_id": 0, "name": 1, "student_id": 1, "grades": 1})
            if student:
                st.write(f"**Tên sinh viên:** {student.get('name', 'Không rõ')}")
                st.write(f"**Mã sinh viên (MSV):** {student.get('student_id', 'Không rõ')}")
                
                grades = student.get("grades", {})
                if grades:
                    # Hiển thị điểm theo bảng
                    grades_table = [{"Môn học": subject, "Điểm": grade} for subject, grade in grades.items()]
                    st.write("**Danh sách điểm:**")
                    st.dataframe(pd.DataFrame(grades_table))
                else:
                    st.warning("Sinh viên này chưa có điểm!")
            else:
                st.error("Không tìm thấy sinh viên với mã này!")
        else:
            st.error("Vui lòng nhập mã sinh viên!")


    # Sửa thông tin sinh viên
    elif menu == "Sửa sinh viên":
        st.header("Sửa thông tin sinh viên")
        student_id = st.text_input("Mã sinh viên")
        name = st.text_input("Họ và tên (mới)")
        age = st.number_input("Tuổi (mới)", min_value=0, step=1)
        major = st.text_input("Ngành học (mới)")

        if st.button("Cập nhật"):
            if student_id:
                update_data = {}
                if name:
                    update_data["name"] = name
                if age > 0:
                    update_data["age"] = age
                if major:
                    update_data["major"] = major

                if update_data:
                    update_student(collection, student_id, update_data)
                    st.success("Cập nhật thông tin thành công!")
                else:
                    st.warning("Không có thông tin nào để cập nhật!")
            else:
                st.error("Vui lòng nhập mã sinh viên!")
    # Phân tích loại sinh viên
    elif menu == "Phân tích loại sinh viên":
        st.header("Phân tích loại sinh viên")

    # Lấy tất cả dữ liệu sinh viên
    students = list(collection.find({}, {"_id": 0, "name": 1, "student_id": 1, "grades": 1}))
    
    if students:
        # Biến đếm loại sinh viên
        categories = {"Trung bình": 0, "Khá": 0, "Giỏi": 0}
        
        for student in students:
            grades = student.get("grades", {})
            if grades:
                # Tính điểm trung bình tổng cộng cho mỗi sinh viên
                avg_scores = [details.get("avg", 0) for details in grades.values()]
                overall_avg = sum(avg_scores) / len(avg_scores) if avg_scores else 0
                
                # Phân loại sinh viên
                if overall_avg < 5:
                    categories["Trung bình"] += 1
                elif 5 <= overall_avg < 8:
                    categories["Khá"] += 1
                elif overall_avg <= 10:
                    categories["Giỏi"] += 1
        
        # Hiển thị phân tích dưới dạng biểu đồ
        st.subheader("Phân bố loại sinh viên")
        
        # Tạo biểu đồ
        fig, ax = plt.subplots()
        ax.bar(categories.keys(), categories.values(), color=['red', 'orange', 'green'])
        ax.set_xlabel("Loại sinh viên")
        ax.set_ylabel("Số lượng")
        ax.set_title("Phân tích loại sinh viên")
        st.pyplot(fig)
    else:
        st.warning("Không có dữ liệu sinh viên để phân tích!")

if __name__ == "__main__":
    main()

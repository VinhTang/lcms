import os
import sys
import django
import random

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'apps')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lcms.settings")
django.setup()

from students.models import Student

# Data arrays for random name generation
LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE_NAMES = ["Văn", "Hữu", "Đức", "Công", "Minh", "Thanh", "Thị", "Ngọc", "Thu", "Bảo", "Gia", "Kim", "Thảo", "Tuyết", "Trà", "Khánh"]
FIRST_NAMES = ["Nam", "Thắng", "Quang", "Huy", "Vũ", "Thiện", "Hiên", "Hải", "Tuấn", "Hoàng", "Khiết", "Nga", "Thy", "My", "Thảo", "Hân", "Trúc", "Ngân", "Tuệ", "Thư", "Vy", "Ngọc", "Trân", "Nhi", "Minh", "Tâm", "Anh", "Lâm", "Hằng", "Hoa", "Mai", "Phương", "Hương"]

SCHOOLS = [
    "THPT Chuyên Lê Hồng Phong",
    "THPT Nguyễn Thượng Hiền",
    "THPT Bùi Thị Xuân",
    "THPT Trần Đại Nghĩa",
    "THPT Mạc Đĩnh Chi",
    "THPT Gia Định",
    "THPT Nguyễn Trãi"
]

def generate_random_name():
    last = random.choice(LAST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    first = random.choice(FIRST_NAMES)
    return f"{last} {middle} {first}"

def import_students():
    target_count = 50
    print(f"Bắt đầu tự động sinh và import {target_count} học sinh ngẫu nhiên...")
    success_count = 0
    
    for _ in range(target_count):
        # Generate random unique name
        while True:
            name = generate_random_name()
            if not Student.objects.filter(full_name=name).exists():
                break
        
        try:
            birth_year = random.randint(2005, 2012)
            school = random.choice(SCHOOLS)
            gender = random.choice(['male', 'female'])
            
            student = Student(full_name=name, birth_year=birth_year, school=school, gender=gender)
            student.save() # generate_domain will execute automatically
            print(f"✅ Đã tạo mới: {name} (Domain: {student.domain}, Năm sinh: {birth_year}, Giới tính: {gender})")
            
            success_count += 1
        except Exception as e:
            print(f"❌ Lỗi khi xử lý {name}: {str(e)}")
            
    print(f"\\n🎉 Hoàn tất! Đã xử lý thành công {success_count}/{target_count} học sinh.")

if __name__ == '__main__':
    import_students()

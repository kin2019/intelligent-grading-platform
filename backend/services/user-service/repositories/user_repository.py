"""
用户仓储层
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from ....shared.utils.database import BaseRepository
from ....shared.models.user import User, Student, Teacher, UserRole, UserStatus, VIPType, GradeLevel


class UserRepository(BaseRepository):
    """用户仓储"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_openid(self, db: Session, openid: str) -> Optional[User]:
        """根据OpenID获取用户"""
        return db.query(User).filter(User.openid == openid).first()
    
    def get_by_phone(self, db: Session, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return db.query(User).filter(User.phone == phone).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def get_users_by_role(self, db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """根据角色获取用户列表"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def get_vip_users(self, db: Session, vip_type: VIPType = None, skip: int = 0, limit: int = 100) -> List[User]:
        """获取VIP用户列表"""
        query = db.query(User).filter(User.vip_type != VIPType.FREE)
        if vip_type:
            query = query.filter(User.vip_type == vip_type)
        return query.offset(skip).limit(limit).all()
    
    def get_expired_vip_users(self, db: Session) -> List[User]:
        """获取VIP已过期的用户"""
        now = datetime.now()
        return db.query(User).filter(
            and_(
                User.vip_type != VIPType.FREE,
                User.vip_expire_time < now
            )
        ).all()
    
    def update_vip_status(self, db: Session, user_id: int, vip_type: VIPType, expire_time: datetime) -> User:
        """更新用户VIP状态"""
        user = self.get_by_id(db, user_id)
        if user:
            user.vip_type = vip_type
            user.vip_expire_time = expire_time
            db.commit()
            db.refresh(user)
        return user
    
    def update_quota(self, db: Session, user_id: int, daily_quota: int, daily_used: int = None) -> User:
        """更新用户配额"""
        user = self.get_by_id(db, user_id)
        if user:
            user.daily_quota = daily_quota
            if daily_used is not None:
                user.daily_used = daily_used
            user.last_quota_reset = datetime.now().date()
            db.commit()
            db.refresh(user)
        return user
    
    def reset_daily_quota(self, db: Session) -> int:
        """重置所有用户的每日配额"""
        today = datetime.now().date()
        affected_rows = db.query(User).filter(
            or_(
                User.last_quota_reset.is_(None),
                User.last_quota_reset < today
            )
        ).update({
            User.daily_used: 0,
            User.last_quota_reset: today
        })
        db.commit()
        return affected_rows
    
    def update_statistics(self, db: Session, user_id: int, corrections: int = 0, questions: int = 0, accuracy: float = None) -> User:
        """更新用户统计信息"""
        user = self.get_by_id(db, user_id)
        if user:
            user.total_corrections += corrections
            user.total_questions += questions
            if accuracy is not None:
                # 计算累计正确率（加权平均）
                if user.total_questions > 0:
                    user.accuracy_rate = ((user.accuracy_rate or 0) * (user.total_questions - questions) + accuracy * questions) / user.total_questions
                else:
                    user.accuracy_rate = accuracy
            db.commit()
            db.refresh(user)
        return user
    
    def search_users(self, db: Session, keyword: str, role: UserRole = None, skip: int = 0, limit: int = 100) -> List[User]:
        """搜索用户"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if keyword:
            query = query.filter(
                or_(
                    User.nickname.ilike(f"%{keyword}%"),
                    User.phone.ilike(f"%{keyword}%"),
                    User.email.ilike(f"%{keyword}%")
                )
            )
        
        return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()


class StudentRepository(BaseRepository):
    """学生仓储"""
    
    def __init__(self):
        super().__init__(Student)
    
    def get_by_parent_id(self, db: Session, parent_id: int) -> List[Student]:
        """根据家长ID获取学生列表"""
        return db.query(Student).filter(Student.parent_id == parent_id).all()
    
    def get_by_teacher_id(self, db: Session, teacher_id: int) -> List[Student]:
        """根据教师ID获取学生列表"""
        return db.query(Student).filter(Student.teacher_id == teacher_id).all()
    
    def get_by_grade(self, db: Session, grade: GradeLevel, skip: int = 0, limit: int = 100) -> List[Student]:
        """根据年级获取学生列表"""
        return db.query(Student).filter(Student.grade == grade).offset(skip).limit(limit).all()
    
    def get_with_parent_info(self, db: Session, student_id: int) -> Optional[Student]:
        """获取学生信息（包含家长信息）"""
        return db.query(Student).options(joinedload(Student.parent)).filter(Student.id == student_id).first()
    
    def assign_teacher(self, db: Session, student_id: int, teacher_id: int) -> Student:
        """为学生分配教师"""
        student = self.get_by_id(db, student_id)
        if student:
            student.teacher_id = teacher_id
            db.commit()
            db.refresh(student)
        return student
    
    def update_statistics(self, db: Session, student_id: int, homework_count: int = 0, completed_count: int = 0, score: float = None) -> Student:
        """更新学生统计信息"""
        student = self.get_by_id(db, student_id)
        if student:
            student.total_homework += homework_count
            student.completed_homework += completed_count
            
            if score is not None:
                # 计算平均分数
                total_scores = (student.average_score or 0) * (student.completed_homework - completed_count) + score
                student.average_score = total_scores / student.completed_homework if student.completed_homework > 0 else score
            
            db.commit()
            db.refresh(student)
        return student
    
    def search_students(self, db: Session, keyword: str, grade: GradeLevel = None, parent_id: int = None, skip: int = 0, limit: int = 100) -> List[Student]:
        """搜索学生"""
        query = db.query(Student)
        
        if parent_id:
            query = query.filter(Student.parent_id == parent_id)
        
        if grade:
            query = query.filter(Student.grade == grade)
        
        if keyword:
            query = query.filter(
                or_(
                    Student.name.ilike(f"%{keyword}%"),
                    Student.school.ilike(f"%{keyword}%"),
                    Student.class_name.ilike(f"%{keyword}%")
                )
            )
        
        return query.order_by(desc(Student.created_at)).offset(skip).limit(limit).all()


class TeacherRepository(BaseRepository):
    """教师仓储"""
    
    def __init__(self):
        super().__init__(Teacher)
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Teacher]:
        """根据用户ID获取教师信息"""
        return db.query(Teacher).filter(Teacher.user_id == user_id).first()
    
    def get_by_id_card(self, db: Session, id_card: str) -> Optional[Teacher]:
        """根据身份证号获取教师"""
        return db.query(Teacher).filter(Teacher.id_card == id_card).first()
    
    def get_verified_teachers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """获取已认证的教师列表"""
        return db.query(Teacher).filter(Teacher.is_verified == True).offset(skip).limit(limit).all()
    
    def get_pending_verification(self, db: Session, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """获取待认证的教师列表"""
        return db.query(Teacher).filter(Teacher.is_verified == False).offset(skip).limit(limit).all()
    
    def get_with_user_info(self, db: Session, teacher_id: int) -> Optional[Teacher]:
        """获取教师信息（包含用户信息）"""
        return db.query(Teacher).options(joinedload(Teacher.user)).filter(Teacher.id == teacher_id).first()
    
    def verify_teacher(self, db: Session, teacher_id: int) -> Teacher:
        """认证教师"""
        teacher = self.get_by_id(db, teacher_id)
        if teacher:
            teacher.is_verified = True
            teacher.verified_at = datetime.now()
            db.commit()
            db.refresh(teacher)
        return teacher
    
    def update_statistics(self, db: Session, teacher_id: int, students: int = 0, corrections: int = 0, rating: float = None) -> Teacher:
        """更新教师统计信息"""
        teacher = self.get_by_id(db, teacher_id)
        if teacher:
            teacher.total_students += students
            teacher.total_corrections += corrections
            
            if rating is not None:
                # 计算评分（简单平均）
                teacher.rating = rating
            
            db.commit()
            db.refresh(teacher)
        return teacher
    
    def update_income(self, db: Session, teacher_id: int, income: float) -> Teacher:
        """更新教师收入"""
        teacher = self.get_by_id(db, teacher_id)
        if teacher:
            teacher.total_income += income
            db.commit()
            db.refresh(teacher)
        return teacher
    
    def withdraw_income(self, db: Session, teacher_id: int, amount: float) -> Teacher:
        """教师提现"""
        teacher = self.get_by_id(db, teacher_id)
        if teacher and teacher.total_income - teacher.withdraw_amount >= amount:
            teacher.withdraw_amount += amount
            db.commit()
            db.refresh(teacher)
        return teacher
    
    def search_teachers(self, db: Session, keyword: str, verified: bool = None, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """搜索教师"""
        query = db.query(Teacher).options(joinedload(Teacher.user))
        
        if verified is not None:
            query = query.filter(Teacher.is_verified == verified)
        
        if keyword:
            query = query.filter(
                or_(
                    Teacher.real_name.ilike(f"%{keyword}%"),
                    Teacher.user.has(User.nickname.ilike(f"%{keyword}%")),
                    Teacher.user.has(User.phone.ilike(f"%{keyword}%"))
                )
            )
        
        return query.order_by(desc(Teacher.created_at)).offset(skip).limit(limit).all()
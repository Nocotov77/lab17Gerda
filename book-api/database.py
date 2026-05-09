from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy модель книги
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    genre = Column(String, nullable=False)        # храним значение жанра как строку
    publication_year = Column(Integer, nullable=False)
    pages = Column(Integer, nullable=False)
    isbn = Column(String(13), unique=True, nullable=False)
    available = Column(Boolean, default=True)

    # Связь один-к-одному с записью о выдаче
    borrow_record = relationship("BorrowRecord", back_populates="book", uselist=False)

# SQLAlchemy модель записи о выдаче книги
class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), unique=True, nullable=False)
    borrower_name = Column(String(100), nullable=False)
    borrowed_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)

    book = relationship("Book", back_populates="borrow_record")

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
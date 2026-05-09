from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import date, timedelta

from models import (
    BookCreate, BookResponse, BookUpdate, BorrowRequest,
    BookDetailResponse, Genre
)
from database import get_db, Book, BorrowRecord

router = APIRouter()


# GET /books – список с фильтрацией и пагинацией
@router.get("/books", response_model=List[BookResponse])
async def get_books(
    genre: Optional[Genre] = Query(None),
    author: Optional[str] = Query(None),
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Book)
    if genre is not None:
        query = query.filter(Book.genre == genre.value)
    if author is not None:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if available_only:
        query = query.filter(Book.available == True)

    books = query.order_by(Book.id).offset(skip).limit(limit).all()
    return books


# GET /books/{book_id} – детальная информация
@router.get("/books/{book_id}", response_model=BookDetailResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена")

    # Если книга занята – добавляем информацию о выдаче
    borrowed_by = None
    borrowed_date = None
    return_date = None
    if not book.available and book.borrow_record:
        borrowed_by = book.borrow_record.borrower_name
        borrowed_date = book.borrow_record.borrowed_date
        return_date = book.borrow_record.return_date

    return BookDetailResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        publication_year=book.publication_year,
        pages=book.pages,
        isbn=book.isbn,
        available=book.available,
        borrowed_by=borrowed_by,
        borrowed_date=borrowed_date,
        return_date=return_date
    )


# POST /books – создание книги
@router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # Проверка уникальности ISBN
    existing = db.query(Book).filter(Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Книга с таким ISBN уже существует")

    new_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre.value,
        publication_year=book.publication_year,
        pages=book.pages,
        isbn=book.isbn,
        available=True
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


# PUT /books/{book_id} – обновление книги
@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена")

    update_data = book_update.dict(exclude_unset=True)

    # Проверка уникальности ISBN, если он изменился
    if "isbn" in update_data and update_data["isbn"] != book.isbn:
        existing = db.query(Book).filter(Book.isbn == update_data["isbn"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Книга с таким ISBN уже существует")

    # Обновляем поля
    for field, value in update_data.items():
        if field == "genre" and hasattr(value, "value"):
            value = value.value
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


# DELETE /books/{book_id} – удаление книги
@router.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена")
    if not book.available:
        raise HTTPException(status_code=400, detail="Нельзя удалить книгу, которая находится на руках")

    db.delete(book)
    db.commit()
    return


# POST /books/{book_id}/borrow – взять книгу
@router.post("/books/{book_id}/borrow", response_model=BookDetailResponse)
async def borrow_book(book_id: int, borrow_request: BorrowRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена")
    if not book.available:
        raise HTTPException(status_code=400, detail="Книга уже выдана")

    today = date.today()
    # Создаём запись о выдаче
    record = BorrowRecord(
        book_id=book.id,
        borrower_name=borrow_request.borrower_name,
        borrowed_date=today,
        return_date=today + timedelta(days=borrow_request.return_days)
    )
    book.available = False
    db.add(record)
    db.commit()
    db.refresh(book)   # чтобы загрузить связь borrow_record
    return await get_book(book_id, db)


# POST /books/{book_id}/return – вернуть книгу
@router.post("/books/{book_id}/return", response_model=BookResponse)
async def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга с указанным ID не найдена")
    if book.available:
        raise HTTPException(status_code=400, detail="Книга не была выдана")

    # Удаляем запись о выдаче
    record = db.query(BorrowRecord).filter(BorrowRecord.book_id == book_id).first()
    if record:
        db.delete(record)
    book.available = True
    db.commit()
    db.refresh(book)
    return book


# GET /stats – статистика библиотеки
@router.get("/stats")
async def get_library_stats(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    available_books = db.query(Book).filter(Book.available == True).count()
    borrowed_books = total_books - available_books

    # Книги по жанрам
    genre_counts = (
        db.query(Book.genre, func.count(Book.id))
        .group_by(Book.genre)
        .all()
    )
    books_by_genre = {genre: count for genre, count in genre_counts}

    # Автор с наибольшим количеством книг
    author_counts = (
        db.query(Book.author, func.count(Book.id))
        .group_by(Book.author)
        .order_by(func.count(Book.id).desc())
        .all()
    )
    most_prolific_author = author_counts[0][0] if author_counts else None

    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "books_by_genre": books_by_genre,
        "most_prolific_author": most_prolific_author
    }
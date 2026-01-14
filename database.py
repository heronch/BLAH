# ==========================================
# COMPLETE LIBRARY DATABASE MANAGER
# ==========================================
# This is a class - a blueprint for managing our database
# You can create an instance and use its methods

import sqlite3

class LibraryDatabase:
    """
    A class to manage the library database operations.
    Makes it easy to add, search, update, and delete books.
    """
    
    def __init__(self, db_name='library.db'):
        """
        Constructor - runs when you create a new LibraryDatabase object
        
        Args:
            db_name: Name of the database file (default: 'library.db')
        """
        self.db_name = db_name
        self.create_table()
    
    def get_connection(self):
        """
        Creates and returns a connection to the database
        
        Returns:
            connection object
        """
        return sqlite3.connect(self.db_name)
    
    def create_table(self):
        """
        Creates the books table if it doesn't exist
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                description TEXT,
                available INTEGER DEFAULT 1
            )
        """)
        
        connection.commit()
        connection.close()
    
    def add_book(self, title, author, genre, description, available=1):
        """
        Adds a single book to the database
        
        Args:
            title: Book title (required)
            author: Book author (required)
            genre: Book genre (optional)
            description: Book description (optional)
            available: 1 if available, 0 if borrowed (default: 1)
        
        Returns:
            The ID of the newly added book
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO books (title, author, genre, description, available)
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, genre, description, available))
        
        book_id = cursor.lastrowid  # Get the ID of the book just added
        connection.commit()
        connection.close()
        
        return book_id
    
    def get_all_books(self):
        """
        Retrieves all books from the database
        
        Returns:
            List of tuples, each containing book data
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        
        connection.close()
        return books
    
    def get_book_by_id(self, book_id):
        """
        Gets a specific book by its ID
        
        Args:
            book_id: The ID of the book
        
        Returns:
            Tuple with book data, or None if not found
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        
        connection.close()
        return book
    
    def search_books(self, search_term):
        """
        Searches for books by title or author
        
        Args:
            search_term: Text to search for
        
        Returns:
            List of matching books
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        # Search in both title and author fields
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ?
        """, (search_pattern, search_pattern))
        
        books = cursor.fetchall()
        connection.close()
        return books
    
    def get_available_books(self):
        """
        Gets all books that are currently available
        
        Returns:
            List of available books
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM books WHERE available = 1")
        books = cursor.fetchall()
        
        connection.close()
        return books
    
    def update_availability(self, book_id, available):
        """
        Updates whether a book is available or borrowed
        
        Args:
            book_id: The ID of the book
            available: 1 for available, 0 for borrowed
        
        Returns:
            True if successful, False if book not found
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE books 
            SET available = ? 
            WHERE id = ?
        """, (available, book_id))
        
        rows_affected = cursor.rowcount
        connection.commit()
        connection.close()
        
        return rows_affected > 0
    
    def borrow_book(self, book_id):
        """
        Marks a book as borrowed
        
        Args:
            book_id: The ID of the book
        
        Returns:
            True if successful, False if book not found or already borrowed
        """
        book = self.get_book_by_id(book_id)
        
        if not book:
            return False  # Book doesn't exist
        
        if book[5] == 0:  # book[5] is the 'available' column
            return False  # Already borrowed
        
        return self.update_availability(book_id, 0)
    
    def return_book(self, book_id):
        """
        Marks a book as returned (available)
        
        Args:
            book_id: The ID of the book
        
        Returns:
            True if successful
        """
        return self.update_availability(book_id, 1)
    
    def update_book(self, book_id, title=None, author=None, genre=None, 
                    description=None, available=None):
        """
        Updates book information
        
        Args:
            book_id: The ID of the book
            title: New title (optional)
            author: New author (optional)
            genre: New genre (optional)
            description: New description (optional)
            available: New availability status (optional)
        
        Returns:
            True if successful
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        # Build update query dynamically based on what's provided
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if author is not None:
            updates.append("author = ?")
            values.append(author)
        if genre is not None:
            updates.append("genre = ?")
            values.append(genre)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if available is not None:
            updates.append("available = ?")
            values.append(available)
        
        if not updates:
            return False  # Nothing to update
        
        values.append(book_id)
        query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        connection.commit()
        connection.close()
        
        return True
    
    def delete_book(self, book_id):
        """
        Deletes a book from the database
        
        Args:
            book_id: The ID of the book
        
        Returns:
            True if successful, False if book not found
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        rows_affected = cursor.rowcount
        
        connection.commit()
        connection.close()
        
        return rows_affected > 0
    
    def get_stats(self):
        """
        Gets statistics about the library
        
        Returns:
            Dictionary with total, available, and borrowed counts
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM books")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE available = 1")
        available = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE available = 0")
        borrowed = cursor.fetchone()[0]
        
        connection.close()
        
        return {
            'total': total,
            'available': available,
            'borrowed': borrowed
        }


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    # Create a database manager instance
    db = LibraryDatabase()
    
    print("="*70)
    print("LIBRARY DATABASE MANAGER - DEMO")
    print("="*70)
    
    # Add a book
    print("\n1. Adding a book...")
    book_id = db.add_book(
        title="The Lord of the Rings",
        author="J.R.R. Tolkien",
        genre="Fantasy",
        description="An epic tale of good versus evil"
    )
    print(f"✓ Added book with ID: {book_id}")
    
    # Get all books
    print("\n2. All books in library:")
    books = db.get_all_books()
    for book in books:
        print(f"  • ID {book[0]}: {book[1]} by {book[2]}")
    
    # Search for books
    print("\n3. Searching for 'Tolkien'...")
    results = db.search_books("Tolkien")
    for book in results:
        print(f"  • Found: {book[1]}")
    
    # Get available books
    print("\n4. Available books:")
    available = db.get_available_books()
    print(f"  • {len(available)} books available")
    
    # Borrow a book
    print("\n5. Borrowing a book...")
    if db.borrow_book(book_id):
        print(f"  ✓ Book {book_id} borrowed successfully")
    
    # Return a book
    print("\n6. Returning a book...")
    if db.return_book(book_id):
        print(f"  ✓ Book {book_id} returned successfully")
    
    # Get statistics
    print("\n7. Library statistics:")
    stats = db.get_stats()
    print(f"  • Total books: {stats['total']}")
    print(f"  • Available: {stats['available']}")
    print(f"  • Borrowed: {stats['borrowed']}")
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70)
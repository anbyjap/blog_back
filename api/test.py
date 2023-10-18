from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, engine  # Import your SQLAlchemy Base and engine
from models import User, Post, PostCategory, PostTag, Tag, Category

# Import your SQLAlchemy model classes (User, Post, PostTag, Tag, PostCategory, Category)

# Create tables
Base.metadata.create_all(bind=engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into the 'users' table
user1 = User(user_id=1, name="User1", email="user1@example.com", hashed_password="password123")
user2 = User(user_id=2, name="User2", email="user2@example.com", hashed_password="password456")
session.add_all([user1, user2])

# Insert data into the 'posts' table with manually set post_id
post1 = Post(post_id=1, user_id=user1.user_id, title="Post 1", content="Content for Post 1")
post2 = Post(post_id=2, user_id=user2.user_id, title="Post 2", content="Content for Post 2")
session.add_all([post1, post2])

# Insert data into the 'tags' table with manually set id
tag1 = Tag(id=1, title="Tag 1")
tag2 = Tag(id=2, title="Tag 2")
session.add_all([tag1, tag2])

# Insert data into the 'post_tag' table with manually set post_tag_id
post_tag1 = PostTag(post_tag_id=1, post=post1, tag=tag1)
post_tag2 = PostTag(post_tag_id=2, post=post1, tag=tag2)
post_tag3 = PostTag(post_tag_id=3, post=post2, tag=tag2)
session.add_all([post_tag1, post_tag2, post_tag3])
session.commit()  # Commit post tags

# Insert data into the 'categories' table with manually set id
category1 = Category(id=1, title="Category 1", context="Category 1 Description")
category2 = Category(id=2, title="Category 2", context="Category 2 Description")
session.add_all([category1, category2])

# Insert data into the 'post_category' table with manually set category_id
post_category1 = PostCategory(post_category_id=1,category_id=category1.id, post_id=post1.post_id, categories=category1)
post_category2 = PostCategory(post_category_id=1,category_id=category2.id, post_id=post2.post_id, categories=category2)
session.add_all([post_category1, post_category2])

# Commit the changes to the database
session.commit()

# Close the session
session.close()

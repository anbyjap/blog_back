-- DB作成
CREATE DATABASE blog;

\connect blog;

\c blog;

-- Create the 'users' table
CREATE TABLE public.users (
    "user_id" INTEGER NOT NULL,
    "name" VARCHAR NOT NULL,
    "email" VARCHAR NOT NULL,
    "hashed_password" VARCHAR NOT NULL,
    "is_active" BOOLEAN DEFAULT TRUE,
    PRIMARY KEY ("user_id"),
    UNIQUE ("name"),
    UNIQUE ("email")
);

-- Create the 'posts' table
CREATE TABLE public.posts (
    "post_id" INTEGER NOT NULL,
    "user_id" INTEGER REFERENCES users ("user_id"),
    "title" VARCHAR,
    "meta_title" VARCHAR,
    "slug" VARCHAR,
    "content" VARCHAR,
    "summary" VARCHAR,
    "is_published" BOOLEAN DEFAULT TRUE,
    "like" INTEGER,
    "dislike" INTEGER,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "published_at" TIMESTAMP,
    PRIMARY KEY ("post_id")
);

-- Create the 'post_tag' table
CREATE TABLE public.post_tag (
	"post_tag_id" INTEGER not NULL,
    "tag_id" INTEGER NOT NULL,
    "post_id" INTEGER REFERENCES posts ("post_id"),
    PRIMARY KEY ("post_tag_id")
);

-- Create the 'tags' table
CREATE TABLE public.tag (
    "id" INTEGER NOT NULL,
    "tag_id" INTEGER REFERENCES post_tag ("post_tag_id"),
    "title" VARCHAR,
    "meta_title" VARCHAR,
    PRIMARY KEY ("id")
);

-- Create the 'post_category' table
CREATE TABLE public.post_category (
	"post_category_id" INTEGER NOT NULL,
    "category_id" INTEGER NOT NULL,
    "post_id" INTEGER REFERENCES posts ("post_id"),
    PRIMARY KEY ("post_category_id")
);

-- Create the 'categories' table
CREATE TABLE public.categories (
    "id" INTEGER NOT NULL,
    "category_id" INTEGER REFERENCES post_category ("post_category_id"),
    "title" VARCHAR,
    "meta_title" VARCHAR,
    "context" VARCHAR,
    PRIMARY KEY ("id")
);

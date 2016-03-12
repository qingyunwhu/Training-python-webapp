#!/usr/bin/env python
# -*- coding:utf-8 -*-

from models import *
from transwarp import db

db.create_engine("root","3181028cwj","py")
db.update('drop table if EXISTS users')
db.update('drop table if EXISTS blogs')
db.update('drop table if EXISTS comments')
db.update("""create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `password` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
""")
db.update("""create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
""")
db.update("""create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
""")
u = User(name='Test',email='test@example.com',password='123456',image='about:blank')
u.insert()
print 'new user id:',u.id
u1 = User.find_first('where email=?','test@example.com')
print 'find user\'s name:',u1.name
u1.delete()

u2 = User.find_first('where email=?','test@example.com')
print 'find user:',u2

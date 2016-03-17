CREATE TABLE `spider_comment` (
  `commentid` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '评论id',
  `skuid` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '商品skuid',
  `comment_content` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '评论内容',
  `comment_time` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '评论时间',
  `user_level_id` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户等级id',
  `user_rovince` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户所在地',
  `user_register_time` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户注册时间',
  `score` int(2) DEFAULT '-1' COMMENT '评分',
  PRIMARY KEY (`commentid`),
  KEY `index_skuid` (`skuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
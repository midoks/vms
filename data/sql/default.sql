
CREATE TABLE IF NOT EXISTS `video` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` INTEGER,
  `name` TEXT,
  `filename` TEXT,
  `size` INTEGER,
  `status` INTEGER,
  `uptime` TEXT,
  `addtime` TEXT
);


INSERT INTO `video` (`id`, `type`, `name`, `filename`, `size`, `status`, `addtime`) VALUES
(1, '1', '21232f297a57a5a743894a0e4a801fc3', '12', '12', 0, '2016-12-10 15:12:56','2016-12-10 15:12:56');


CREATE TABLE IF NOT EXISTS `video_list` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `md5` TEXT,
  `pid` INTEGER,
  `filename` TEXT,
  `size` INTEGER,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `logs` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` TEXT,
  `log` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `api` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `appkey` VARCHAR(20),
  `appsecret` CHAR(32),
  `addtime` TEXT
);

INSERT INTO `api` (`id`, `appkey`, `appsecret`, `addtime`) VALUES
(1, 'demo','e10adc3949ba59abbe56e057f20f883e','2016-12-10 15:12:56');



CREATE TABLE IF NOT EXISTS `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT,
  `password` TEXT,
  `login_ip` TEXT,
  `login_time` TEXT,
  `phone` TEXT,
  `email` TEXT
);

INSERT INTO `users` (`id`, `username`, `password`, `login_ip`, `login_time`, `phone`, `email`) VALUES
(1, 'admin', '21232f297a57a5a743894a0e4a801fc3', '192.168.0.10', '2016-12-10 15:12:56', 0, '287962566@qq.com');


CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` 			TEXT,
  `type`			TEXT,
  `status` 		TEXT,
  `addtime` 	TEXT,
  `start` 	  INTEGER,
  `end` 	    INTEGER,
  `execstr` 	TEXT
);

CREATE TABLE IF NOT EXISTS `panel` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `title` TEXT,
  `url` TEXT,
  `username` TEXT,
  `password` TEXT,
  `click` INTEGER,
  `addtime` INTEGER
);

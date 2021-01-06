CREATE TABLE IF NOT EXISTS `video` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `filename` TEXT, 
  `size` INTEGER,
  `status` INTEGER,
  `uptime` TEXT,
  `addtime` TEXT
);

INSERT INTO `video` (`id`, `name`, `filename`, `size`, `status`, `addtime`) VALUES
(1, '21232f297a57a5a743894a0e4a801fc3', '12', '12', 0, '2016-12-10 15:12:56','2016-12-10 15:12:56');


CREATE TABLE IF NOT EXISTS `video_list` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `md5` TEXT,
  `pid` INTEGER,
  `filename` TEXT,
  `size` INTEGER,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `video_tmp` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `md5` TEXT,
  `filename` TEXT,
  `size` INTEGER,
  `status` INTEGER,
  `uptime` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `kv` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `value` TEXT,
  `addtime` TEXT
);

INSERT INTO `kv` (`id`, `name`, `value`, `addtime`) VALUES
(1, 'run_model', '1','2016-12-10 15:12:56'),
(2, 'video_size', '10','2016-12-10 15:12:56');


CREATE TABLE IF NOT EXISTS `node` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `ip` TEXT,
  `uptime` TEXT,
  `addtime` TEXT
);

INSERT INTO `node` (`id`, `name`, `type`,`ip`, `uptime`,`addtime`) VALUES
(1, '测试', 'type','127.0.0.1', '2016-12-10 15:12:56', '2016-12-10 15:12:56');


CREATE TABLE IF NOT EXISTS `logs` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` TEXT,
  `log` TEXT,
  `addtime` TEXT
);


INSERT INTO `logs` (`id`, `type`, `log`, `addtime`) VALUES
(1, '1', '测试','2016-12-10 15:12:56');


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
(1, 'admin', '4297f44b13955235245b2497399d7a93', '192.168.0.10', '2016-12-10 15:12:56', 0, '627293072@qq.com');

